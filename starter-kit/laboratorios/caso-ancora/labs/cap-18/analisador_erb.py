#!/usr/bin/env python3
"""Analisador local de ERB; biblioteca padrão, sem rede ou modelo."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

VERSAO = "1.1.1"
COLUNAS_OBRIGATORIAS = (
    "data_hora", "tipo_evento", "linha_origem", "linha_destino",
    "identificador_dispositivo_sintetico", "erb_id", "erb_nome",
    "municipio_ficticio", "latitude_aproximada", "longitude_aproximada", "duracao_segundos",
)
AVISOS = (
    "A ERB indica a antena que atendeu o evento, não a posição exata do aparelho.",
    "O fuso horário é o do arquivo; confirme com a operadora.",
    "O titular de uma linha não é, por isso, quem a usava.",
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalizar_telefone(texto):
    digitos = re.sub(r"\D", "", texto)
    if not digitos:
        return ""
    if len(digitos) in (10, 11):
        digitos = "55" + digitos
    return "+" + digitos


def ler_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        faltantes = [c for c in COLUNAS_OBRIGATORIAS if c not in (leitor.fieldnames or [])]
        if faltantes:
            raise ValueError("colunas ausentes: " + ", ".join(faltantes))
        if len(leitor.fieldnames) != len(set(leitor.fieldnames)):
            raise ValueError("cabeçalho contém colunas duplicadas")
        observacao = "observacao" in leitor.fieldnames
        validas, invalidas = [], []
        for numero, linha in enumerate(leitor, start=2):
            if None in linha or any(value is None for value in linha.values()):
                raise ValueError(f"linha {numero}: quantidade de campos diferente do cabeçalho")
            bruto = linha.get("data_hora") or ""
            try:
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", bruto):
                    raise ValueError()
                datetime.strptime(bruto, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                invalidas.append({"linha": numero, "data_hora": bruto})
                continue
            # observacao jamais entra no resumo nem no texto produzido.
            r = {c: (linha.get(c) or "").strip() for c in COLUNAS_OBRIGATORIAS}
            r["origem_original"] = r["linha_origem"]
            r["destino_original"] = r["linha_destino"]
            r["linha_origem"] = normalizar_telefone(r["linha_origem"])
            r["linha_destino"] = normalizar_telefone(r["linha_destino"])
            validas.append(r)
    return validas, invalidas, observacao


def carregar_csv(path):
    return ler_csv(path)[0]


def resumir(linhas):
    # sorted é estável: empate conserva a ordem do arquivo.
    ordenadas = sorted(linhas, key=lambda r: r["data_hora"])
    erbs, contatos, origens = defaultdict(list), defaultdict(list), defaultdict(list)
    for r in ordenadas:
        erbs[r["erb_id"]].append(r)
        if r["linha_destino"]:
            contatos[r["linha_destino"]].append(r)
        if r["linha_origem"]:
            origens[r["linha_origem"]].append(r)
    return ordenadas, erbs, contatos, origens


def celula(texto):
    return str(texto).replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def renderizar_markdown(path, linhas, log_path=None, invalidas=None, observacao=False):
    invalidas = invalidas or []
    ordenadas, erbs, contatos, origens = resumir(linhas)
    out = [
        "# Relatório do analisador de extrato telefônico/ERB", "",
        "> Resultado determinístico sobre dado sintético. Não conclui localização, identidade ou conduta.", "",
        f"- **Ferramenta:** `analisador_erb.py` v{VERSAO}",
        f"- **Entrada:** `{path.name}`",
        f"- **SHA-256 da entrada:** `{sha256(path)}`",
        f"- **Linhas lidas / processadas / não processadas:** {len(linhas) + len(invalidas)} / {len(linhas)} / {len(invalidas)}", "",
    ]
    if not linhas:
        out += ["> Aviso: 0 eventos processados.", ""]
    if observacao:
        out += ["> Coluna observacao presente e ignorada.", ""]
    out += ["## Eventos por ERB", "", "| ERB | Nome | Eventos | Primeiro | Último |", "|---|---|---:|---|---|"]
    for erb, eventos in sorted(erbs.items()):
        nomes = ", ".join(sorted({r["erb_nome"] for r in eventos}))
        out.append(f"| {erb} | {celula(nomes)} | {len(eventos)} | {eventos[0]['data_hora']} | {eventos[-1]['data_hora']} |")
    out += ["", "## Linha do tempo", "", "| Data/hora | Tipo | Origem normalizada | Destino normalizado | ERB | Origem original | Destino original |", "|---|---|---|---|---|---|---|"]
    for r in ordenadas:
        campos = (r["data_hora"], r["tipo_evento"], r["linha_origem"], r["linha_destino"], r["erb_id"], r["origem_original"], r["destino_original"])
        out.append("| " + " | ".join(celula(c) for c in campos) + " |")
    out += ["", "## Contatos por frequência", "", "| Contraparte | Eventos | Primeiro | Último |", "|---|---:|---|---|"]
    for contato, eventos in sorted(contatos.items(), key=lambda item: (-len(item[1]), item[0])):
        out.append(f"| {contato} | {len(eventos)} | {eventos[0]['data_hora']} | {eventos[-1]['data_hora']} |")
    out += ["", "## Primeiro e último evento por linha de origem", "", "| Linha | Eventos | Primeiro | Tipo | ERB | Último | Tipo | ERB |", "|---|---:|---|---|---|---|---|---|"]
    for origem, eventos in sorted(origens.items()):
        a, b = eventos[0], eventos[-1]
        campos = (origem, len(eventos), a["data_hora"], a["tipo_evento"], a["erb_id"], b["data_hora"], b["tipo_evento"], b["erb_id"])
        out.append("| " + " | ".join(celula(c) for c in campos) + " |")
    out += ["", "## Linhas não processadas", "", "| Linha CSV | data_hora recebida |", "|---:|---|"]
    for item in invalidas:
        out.append(f"| {item['linha']} | {celula(item['data_hora'])} |")
    out += ["", "## Avisos", ""] + [f"- {aviso}" for aviso in AVISOS]
    return "\n".join(out) + "\n"


def validar_destinos(entrada, saida, log):
    destinos = [p for p in (saida, log) if p is not None]
    resolvidos = [p.resolve() for p in destinos]
    if len(set(resolvidos)) != len(resolvidos):
        raise ValueError("relatório e log precisam de caminhos distintos")
    for bruto, destino in zip(destinos, resolvidos):
        if destino == entrada.resolve() or bruto.exists() or bruto.is_symlink() or ".." in bruto.parts:
            raise ValueError("destino já existe ou coincide com entrada")
        if any(parte.casefold() == "originais" for parte in destino.parts + bruto.absolute().parts):
            raise ValueError("gravação em originais recusada")
        for pai in (bruto, *bruto.parents):
            if pai.is_symlink() or (hasattr(pai, "is_junction") and pai.is_junction()):
                raise ValueError("destino atravessa link ou junção")
    if saida and log and saida.resolve().parent != log.resolve().parent:
        raise ValueError("log deve ficar na pasta de saída")


def executar(entrada, saida=None, log=None):
    # Se houver arquivo de saída, log.txt é obrigatório e automático.
    if saida is not None and log is None:
        log = saida.parent / "log.txt"
    validar_destinos(entrada, saida, log)
    inicio = datetime.now(timezone.utc).isoformat()
    linhas, invalidas, observacao = ler_csv(entrada)
    texto = renderizar_markdown(entrada, linhas, invalidas=invalidas, observacao=observacao)
    registro = {
        "inicio_utc": inicio, "fim_utc": datetime.now(timezone.utc).isoformat(),
        "ferramenta": "analisador_erb.py", "versao": VERSAO,
        "entrada": entrada.as_posix(), "sha256": sha256(entrada), "status": "ok",
        "linhas_lidas": len(linhas) + len(invalidas), "linhas_processadas": len(linhas),
        "linhas_nao_processadas": len(invalidas), "eventos": len(linhas),
    }
    # x evita sobrescrita inclusive se um arquivo surgir após a validação.
    for path, conteudo in ((saida, texto), (log, json.dumps(registro, ensure_ascii=False, sort_keys=True) + "\n")):
        if path is not None:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("x", encoding="utf-8", newline="\n") as arquivo:
                arquivo.write(conteudo)
    return texto


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", required=True, type=Path)
    parser.add_argument("--saida", type=Path)
    parser.add_argument("--log", type=Path)
    args = parser.parse_args()
    try:
        texto = executar(args.entrada, args.saida, args.log)
    except FileNotFoundError as erro:
        print(f"Erro: arquivo ausente: {erro.filename}", file=sys.stderr)
        return 1
    except (OSError, ValueError) as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return 2
    if not args.saida:
        print(texto, end="")
    return 0


if __name__ == "__main__":
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8")
    raise SystemExit(main())
