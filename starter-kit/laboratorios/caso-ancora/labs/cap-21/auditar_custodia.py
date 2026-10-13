#!/usr/bin/env python3
"""Audita manifesto e lacunas temporais; não aprova continuidade da custódia."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import sys
from datetime import datetime
from pathlib import Path

VERSAO = "1.1.0"
ROOT = Path(__file__).resolve().parents[4]
spec = importlib.util.spec_from_file_location("manifesto_c4", ROOT / "scripts/gerar_manifesto_caso.py")
manifesto_c4 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manifesto_c4)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def carregar_log(path):
    eventos = []
    for numero, linha in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not linha.strip():
            continue
        try:
            item = json.loads(linha)
            ts = datetime.fromisoformat(item["timestamp"])
            if ts.tzinfo is None:
                raise ValueError()
        except (ValueError, TypeError, KeyError):
            raise ValueError(f"log inválido ou timestamp sem fuso na linha {numero}") from None
        item.update(_dt=ts, _linha=numero)
        eventos.append(item)
    if not eventos:
        raise ValueError("log vazio")
    return sorted(eventos, key=lambda e: e["_dt"])


def produtos_com_timestamp(pasta):
    produtos = []
    for path in sorted((pasta / "produtos").glob("*.json")):
        try:
            dados = json.loads(path.read_text(encoding="utf-8"))
            dt = datetime.fromisoformat(dados["gerado_em"])
            if dt.tzinfo is None:
                continue
        except (ValueError, KeyError, TypeError, OSError):
            continue
        produtos.append({"arquivo": path.relative_to(pasta).as_posix(), "gerado_em": dados["gerado_em"], "_dt": dt})
    return produtos


def auditar(pasta, limite_minutos=40, referencia=None):
    pasta = pasta.resolve()
    if limite_minutos <= 0:
        raise ValueError("limite-minutos deve ser positivo")
    manifesto = pasta / manifesto_c4.NOME_MANIFESTO
    log = pasta / "log-agente.jsonl"
    if not manifesto.is_file() or not log.is_file():
        raise ValueError("manifesto ou log-agente.jsonl ausente")
    ref = manifesto
    autenticada = False
    erros = []
    if referencia is not None:
        if referencia.is_symlink() or any(p.is_symlink() or (hasattr(p, "is_junction") and p.is_junction()) for p in referencia.parents):
            raise ValueError("referência atravessa link ou junção")
        ref = referencia.resolve()
        if ref.is_relative_to(pasta) or not ref.is_file():
            raise ValueError("referência precisa ser arquivo externo à pasta auditada")
        autenticada = ref.read_bytes() == manifesto.read_bytes()
        if not autenticada:
            erros.append("manifesto interno diverge da referência externa; integridade não autenticada")
    erros += manifesto_c4.verificar(pasta)
    hashes = []
    try:
        dados = json.loads(ref.read_text(encoding="utf-8"))
        for item in dados["arquivos"]:
            nome = item["caminho"]
            path = (pasta / nome).resolve()
            if not path.is_relative_to(pasta) or ".." in Path(nome).parts:
                raise ValueError()
            hashes.append({"arquivo": nome, "esperado": item["sha256"], "atual": digest(path) if path.is_file() else None})
    except (ValueError, KeyError, TypeError):
        erros.append("referência sem inventário verificável")
    eventos = carregar_log(log)
    produtos = produtos_com_timestamp(pasta)
    lacunas = []
    for a, b in zip(eventos, eventos[1:]):
        delta = (b["_dt"] - a["_dt"]).total_seconds()
        gerados = [{"arquivo": p["arquivo"], "gerado_em": p["gerado_em"]} for p in produtos if a["_dt"] < p["_dt"] < b["_dt"]]
        if delta >= limite_minutos * 60 and gerados:
            lacunas.append({"inicio": a["timestamp"], "fim": b["timestamp"], "duracao_minutos": int(delta // 60), "produtos_gerados_no_intervalo": gerados})
    com_metadados = {p["arquivo"] for p in produtos}
    for p in produtos:
        dados = json.loads((pasta / p["arquivo"]).read_text(encoding="utf-8"))
        nome = dados.get("produto")
        if isinstance(nome, str):
            path = (pasta / "produtos" / nome).resolve()
            if path.is_relative_to(pasta / "produtos") and path.is_file():
                com_metadados.add(path.relative_to(pasta).as_posix())
    nao_verificaveis = [p.relative_to(pasta).as_posix() for p in sorted((pasta / "produtos").rglob("*"))
                       if p.is_file() and p.relative_to(pasta).as_posix() not in com_metadados]
    log_incompleto = [{"linha": e["_linha"], "campos_ausentes": [c for c in ("acao", "arquivo", "instrucao", "resposta") if not e.get(c)]}
                      for e in eventos if any(not e.get(c) for c in ("acao", "arquivo", "instrucao", "resposta"))]
    anomalias = [{"tipo": "integridade", "detalhe": e} for e in erros] + [{"tipo": "lacuna_log_com_produto", "detalhe": e} for e in lacunas]
    return {
        "ferramenta": "auditar_custodia.py", "versao": VERSAO, "manifesto": manifesto.name,
        "referencia_usada": {"caminho": ref.as_posix(), "sha256": digest(ref), "externa": referencia is not None,
                            "manifesto_interno_autenticado": autenticada, "sha256_interno": digest(manifesto)},
        "integridade": {"erros": erros, "hashes": hashes}, "lacunas_log": lacunas,
        "total_anomalias": len(anomalias), "anomalias": anomalias, "limite_minutos": limite_minutos,
        "produtos_sem_metadata_verificavel": nao_verificaveis, "log_incompleto": log_incompleto,
        "avaliacao_completa": False,
        "limites": "Detector entre dois registros separados pelo limiar; gerado_em é declarado pelo produto. Intervalos menores, fora dos extremos do log e produtos sem metadados exigem conferência complementar.",
    }


def renderizar_markdown(resultado):
    ref = resultado["referencia_usada"]
    out = [
        "# Relatório de auditoria de custódia", "",
        f"- **Ferramenta:** `auditar_custodia.py` v{resultado['versao']}",
        f"- **Manifesto:** `{resultado['manifesto']}`",
        f"- **Referência efetivamente usada:** `{ref['caminho']}`",
        f"- **SHA-256 da referência:** `{ref['sha256']}`",
        f"- **Referência externa / manifesto interno autenticado:** {ref['externa']} / {ref['manifesto_interno_autenticado']}",
        f"- **Anomalias:** {resultado['total_anomalias']}",
        f"- **Limiar do detector:** {resultado['limite_minutos']} minutos", "",
        "## Integridade dos originais", "",
    ]
    out += [f"- [ANOMALIA] {e}" for e in resultado["integridade"]["erros"]] or ["- Sem divergência de hash/tamanho no escopo do manifesto."]
    out += ["", "| Arquivo | Hash esperado | Hash atual |", "|---|---|---|"]
    for item in resultado["integridade"]["hashes"]:
        out.append(f"| {item['arquivo']} | {item['esperado']} | {item['atual']} |")
    out += ["", "## Lacunas de log com produto gerado", ""]
    for item in resultado["lacunas_log"]:
        nomes = ", ".join(p["arquivo"] for p in item["produtos_gerados_no_intervalo"])
        out.append(f"- [ANOMALIA] {item['inicio']} → {item['fim']} ({item['duracao_minutos']} min); produto(s): {nomes}")
    if not resultado["lacunas_log"]:
        out.append("- Nenhuma lacuna acima do limiar com produto declarado.")
    out += ["", "## Cobertura e pendências", "", resultado["limites"]]
    if not ref["externa"]:
        out.append("- Referência interna sem autenticação externa; não comprova o estado da juntada.")
    for nome in resultado["produtos_sem_metadata_verificavel"]:
        out.append(f"- Produto sem metadados temporais verificáveis: {nome}")
    for item in resultado["log_incompleto"]:
        out.append(f"- Log linha {item['linha']}: faltam {', '.join(item['campos_ausentes'])}.")
    out += ["", "> A ferramenta apenas constata divergências. Ela não corrige, substitui ou regrava originais e não atribui responsabilidade pela anomalia. Conferência humana complementar obrigatória; ausência de anomalia não aprova a custódia."]
    return "\n".join(out) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pasta", required=True, type=Path)
    parser.add_argument("--limite-minutos", type=int, default=40)
    parser.add_argument("--saida", type=Path)
    parser.add_argument("--referencia", type=Path)
    args = parser.parse_args()
    try:
        if args.saida:
            destino = args.saida.resolve()
            produtos = (args.pasta.resolve() / "produtos").resolve()
            if (not destino.is_relative_to(produtos) or args.saida.exists() or ".." in args.saida.parts):
                raise ValueError("saída precisa ser arquivo novo dentro de produtos/")
            for pai in (args.saida, *args.saida.parents):
                if pai.is_symlink() or (hasattr(pai, "is_junction") and pai.is_junction()):
                    raise ValueError("saída atravessa link ou junção")
        resultado = auditar(args.pasta, args.limite_minutos, args.referencia)
        texto = renderizar_markdown(resultado)
        if args.saida:
            args.saida.parent.mkdir(parents=True, exist_ok=True)
            with args.saida.open("x", encoding="utf-8", newline="\n") as arquivo:
                arquivo.write(texto)
        else:
            print(texto, end="")
    except (OSError, ValueError) as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return 2
    return 1 if resultado["total_anomalias"] else 0


if __name__ == "__main__":
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8")
    raise SystemExit(main())
