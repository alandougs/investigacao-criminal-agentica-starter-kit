#!/usr/bin/env python3
"""Compara registros normalizados e referências; não avalia sustentação semântica."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
import unicodedata
from collections import defaultdict, deque
from pathlib import Path

VERSAO = "1.1.2"


def normalizar_evento(texto):
    texto = unicodedata.normalize("NFKC", str(texto)).casefold().strip()
    return re.sub(r"\s+", " ", texto).rstrip(" .;:")


def chave_evento(evento):
    if not isinstance(evento, dict):
        raise ValueError("evento precisa ser objeto")
    descricao = evento.get("evento") or evento.get("descricao")
    if not isinstance(descricao, str) or not descricao.strip():
        raise ValueError("evento sem evento/descricao")
    for campo in ("data", "data_hora"):
        if campo in evento and evento[campo] is not None and not isinstance(evento[campo], str):
            raise ValueError(f"{campo} precisa ser texto ou null")
    data = evento.get("data") or evento.get("data_hora")
    # Ausência explícita ou implícita de data é legítima; nunca preencher pelo cânone.
    if data is not None and not isinstance(data, str):
        raise ValueError("data precisa ser texto ou null")
    return (data or "").strip(), normalizar_evento(descricao)


def extrair_eventos_gabarito(dados):
    if not isinstance(dados, dict):
        raise ValueError("gabarito precisa ser objeto")
    candidatos = dados.get("eventos_esperados", dados.get("eventos"))
    resultado = dados.get("resultado_esperado")
    if resultado is not None and not isinstance(resultado, dict):
        raise ValueError("resultado_esperado precisa ser objeto")
    if candidatos is None and isinstance(resultado, dict):
        candidatos = resultado.get("eventos")
    if not isinstance(candidatos, list):
        raise ValueError("gabarito sem lista de eventos")
    sem_data = (resultado or {}).get("eventos_sem_data", dados.get("eventos_sem_data", []))
    if not isinstance(sem_data, list):
        raise ValueError("eventos_sem_data precisa ser lista")
    for evento in candidatos + sem_data:
        if not isinstance(evento, dict):
            raise ValueError("evento precisa ser objeto")
    for evento in sem_data:
        if evento.get("data") or evento.get("data_hora"):
            raise ValueError("gabarito: evento_sem_data com data")
    eventos = candidatos + sem_data
    ids = [e.get("id") for e in eventos if e.get("id") is not None]
    if len(ids) != len(set(ids)):
        raise ValueError("IDs de referência duplicados")
    return eventos


def extrair_eventos_saida(dados):
    if isinstance(dados, list):
        eventos = dados
    elif isinstance(dados, dict):
        eventos = dados.get("eventos")
        extras = dados.get("eventos_sem_data", [])
        if not isinstance(eventos, list) or not isinstance(extras, list):
            raise ValueError("eventos e eventos_sem_data precisam ser listas")
        eventos = eventos + extras
    else:
        eventos = None
    if not isinstance(eventos, list):
        raise ValueError("saída sem lista de eventos")
    return eventos


def parse_fonte(fonte):
    if isinstance(fonte, dict):
        nome = fonte.get("arquivo") or fonte.get("path")
        bruto = fonte.get("linhas", fonte.get("linha"))
        if isinstance(bruto, list) and all(type(n) is int and n > 0 for n in bruto):
            linhas = sorted(set(bruto))
        elif type(bruto) is int and bruto > 0:
            linhas = [bruto]
        else:
            linhas = []
        return str(nome).strip() if nome else None, linhas
    if isinstance(fonte, str):
        m = re.fullmatch(r"\s*(.+?),\s*linhas?\s+([0-9 ,ea]+)\s*", fonte, flags=re.I)
        if m:
            bruto = m.group(2)
            intervalo = re.fullmatch(r"(\d+)\s*a\s*(\d+)", bruto)
            if intervalo:
                a, b = map(int, intervalo.groups())
                linhas = list(range(a, b + 1)) if 0 < a <= b <= a + 10000 else []
            else:
                linhas = sorted(set(map(int, re.findall(r"\d+", bruto))))
            return m.group(1).strip(), linhas
        return fonte.strip(), []
    return None, []


def resolver_fonte(raiz, nome):
    if not nome:
        return None
    bruto = Path(nome)
    if bruto.is_absolute() or ".." in bruto.parts or ":" in nome:
        return None
    raiz = raiz.resolve()
    direto = (raiz / bruto).resolve()
    if not direto.is_relative_to(raiz):
        return None
    if direto.is_file():
        return direto
    # Somente basename admite descoberta, nunca um caminho fornecido incorretamente.
    if len(bruto.parts) != 1:
        return None
    canonico = (raiz / "laboratorios/caso-ancora/dados" / bruto.name).resolve()
    if canonico.is_file() and canonico.is_relative_to(raiz):
        return canonico
    encontrados = [p.resolve() for p in raiz.rglob(bruto.name) if p.is_file() and p.resolve().is_relative_to(raiz)]
    return encontrados[0] if len(encontrados) == 1 else None


def fontes_evento(evento):
    fontes = evento.get("fontes")
    if fontes is None:
        fontes = [evento.get("fonte")]
    if not isinstance(fontes, list):
        return []
    return fontes


def validar_citacao(predito, esperado, raiz):
    # A comparação comprova caminho/linhas existentes e coincidência com referência.
    # Nem a referência nem a frase são aprovadas semanticamente por este programa.
    fontes_p = fontes_evento(predito)
    fontes_e = fontes_evento(esperado) if esperado else []
    referencias = []
    hashes_fontes = []
    for fonte in fontes_e:
        nome, linhas = parse_fonte(fonte)
        caminho = resolver_fonte(raiz, nome)
        if caminho is None or not linhas:
            return {"status": "gabarito_com_fonte_nao_resolvida", "sustentacao": "revisao_humana_pendente"}
        atual = hashlib.sha256(caminho.read_bytes()).hexdigest()
        hash_esperado = fonte.get("sha256") if isinstance(fonte, dict) else None
        hashes_fontes.append({"arquivo": nome, "sha256_atual": atual, "sha256_esperado": hash_esperado,
                             "fixado_no_gabarito": bool(hash_esperado)})
        if hash_esperado and atual != hash_esperado:
            return {"status": "fonte_alterada", "hashes_fontes": hashes_fontes, "sustentacao": "revisao_humana_pendente"}
        referencias.append((caminho, linhas))
    fornecidas = []
    for fonte in fontes_p:
        nome, linhas = parse_fonte(fonte)
        if not nome or not linhas:
            return {"status": "ausente", "arquivo": nome, "linhas": linhas, "sustentacao": "revisao_humana_pendente"}
        caminho = resolver_fonte(raiz, nome)
        if caminho is None:
            return {"status": "arquivo_inexistente_ou_ambiguo", "arquivo": nome, "linhas": linhas}
        try:
            conteudo = caminho.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            return {"status": "arquivo_ilegivel", "arquivo": nome, "linhas": linhas}
        if any(n < 1 or n > len(conteudo) for n in linhas):
            return {"status": "linha_inexistente", "arquivo": nome, "linhas": linhas}
        fornecidas.append((caminho, linhas))
    if not fornecidas:
        status = "ausente"
    elif esperado is None or not referencias:
        status = "existente_sem_referencia_no_gabarito"
    elif sorted((str(p), ns) for p, ns in fornecidas) != sorted((str(p), ns) for p, ns in referencias):
        status = "divergente_do_gabarito"
    else:
        status = "referencia_conferida"
    return {"status": status, "hashes_fontes": hashes_fontes, "sustentacao": "revisao_humana_pendente"}


def componente_corresponde(predito, esperado):
    # Componentes de fatos compostos devem ser integralmente representados.
    campos = ("id", "data", "data_hora", "evento", "descricao", "classificacao")
    def assinatura(e):
        return tuple((k, normalizar_evento(e[k])) for k in campos if e.get(k) is not None)
    return sorted(map(assinatura, predito.get("componentes", []))) == sorted(map(assinatura, esperado.get("componentes", [])))


def avaliar_execucao(gabarito, saida, raiz):
    esperados = extrair_eventos_gabarito(gabarito)
    preditos = extrair_eventos_saida(saida)
    fila = defaultdict(deque)
    for evento in esperados:
        fila[chave_evento(evento)].append(evento)
    vp, fp, referencias, erros_classificacao = 0, 0, 0, 0
    detalhes = []
    for indice, pred in enumerate(preditos, 1):
        chave = chave_evento(pred)
        candidatos = fila[chave]
        esperado = None
        for candidato in candidatos:
            id_ok = not gabarito.get("exigir_ids") or pred.get("id") == candidato.get("id")
            if id_ok and componente_corresponde(pred, candidato):
                esperado = candidato
                break
        if esperado is not None:
            candidatos.remove(esperado)
            vp += 1
        else:
            fp += 1
        citacao = validar_citacao(pred, esperado, raiz)
        if esperado and citacao["status"] == "referencia_conferida":
            referencias += 1
        classificacao_ok = None
        if esperado and esperado.get("classificacao"):
            classificacao_ok = normalizar_evento(pred.get("classificacao", "")) == normalizar_evento(esperado["classificacao"])
            erros_classificacao += int(not classificacao_ok)
        detalhes.append({
            "indice": indice, "classe_evento": "VP" if esperado else "FP",
            "id": pred.get("id"), "data": chave[0] or None, "evento_normalizado": chave[1],
            "citacao": citacao, "classificacao_conforme_referencia": classificacao_ok,
        })
    fn = sum(len(q) for q in fila.values())
    return {
        "vp": vp, "fp": fp, "fn": fn, "precisao": round(vp / (vp + fp), 6) if vp + fp else 0.0,
        "recall": round(vp / (vp + fn), 6) if vp + fn else 0.0,
        "eventos_esperados": len(esperados), "eventos_preditos": len(preditos),
        "vp_com_referencia_conferida": referencias,
        # Campo legado preservado; não equivale a fonte que sustenta a frase.
        "vp_com_citacao_valida": referencias,
        "citacoes_invalidas_ou_nao_verificaveis": sum(d["citacao"]["status"] != "referencia_conferida" for d in detalhes),
        "erros_classificacao": erros_classificacao, "detalhes": detalhes,
        "sustentacao_semantica": "revisao_humana_pendente",
        "aprovacao_automatica": False,
    }


def carregar_gabarito(path):
    texto = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".md":
        blocos = re.findall(r"```json-gabarito\s*\n(.*?)\n```", texto, re.S)
        if len(blocos) != 1:
            raise ValueError("Markdown precisa de um único bloco json-gabarito")
        texto = blocos[0]
    return json.loads(texto)


def avaliar_arquivos(gabarito_path, saidas, raiz):
    gabarito = carregar_gabarito(gabarito_path)
    resultados, assinaturas = [], []
    for path in saidas:
        dados = json.loads(path.read_text(encoding="utf-8"))
        metrica = avaliar_execucao(gabarito, dados, raiz)
        metrica["arquivo"] = path.as_posix()
        resultados.append(metrica)
        # A ordem não importa; fonte, classificação e componentes também integram variabilidade.
        assinaturas.append(tuple(sorted(json.dumps(e, ensure_ascii=False, sort_keys=True) for e in extrair_eventos_saida(dados))))
    return {
        "ferramenta": "avaliar.py", "versao": VERSAO, "execucoes": resultados,
        "gabarito_sha256": hashlib.sha256(gabarito_path.read_bytes()).hexdigest(),
        "limite": "Correspondência textual e referências; sustentação semântica e aprovação exigem revisão humana.",
        "agregado": {
            "n": len(resultados),
            "media_precisao": round(sum(r["precisao"] for r in resultados) / len(resultados), 6) if resultados else 0.0,
            "media_recall": round(sum(r["recall"] for r in resultados) / len(resultados), 6) if resultados else 0.0,
            "total_fp": sum(r["fp"] for r in resultados), "total_fn": sum(r["fn"] for r in resultados),
            "total_erros_classificacao": sum(r["erros_classificacao"] for r in resultados),
            "resultados_distintos": len(set(assinaturas)),
        },
    }


def gravar_novo(path, texto, protegidos):
    destino = path.resolve()
    if (path.exists() or path.is_symlink() or destino in [p.resolve() for p in protegidos]
            or ".." in path.parts or any(p.casefold() == "originais" for p in path.absolute().parts + destino.parts)):
        raise ValueError("destino existente, protegido ou fora do escopo")
    for pai in (path, *path.parents):
        if pai.is_symlink() or (hasattr(pai, "is_junction") and pai.is_junction()):
            raise ValueError("destino atravessa link ou junção")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as arquivo:
        arquivo.write(texto)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gabarito", required=True, type=Path)
    parser.add_argument("--saida", action="append", type=Path, dest="saidas")
    parser.add_argument("--raiz", type=Path, default=Path.cwd())
    parser.add_argument("--relatorio", type=Path)
    parser.add_argument("--extrair-gabarito", type=Path, help="Extrai bloco JSON do gabarito MD para um arquivo novo.")
    args = parser.parse_args()
    try:
        if args.extrair_gabarito:
            if args.saidas or args.relatorio:
                raise ValueError("extração não pode ser combinada com avaliação")
            texto = json.dumps(carregar_gabarito(args.gabarito), ensure_ascii=False, indent=2) + "\n"
            gravar_novo(args.extrair_gabarito, texto, [args.gabarito])
            return 0
        if not args.saidas:
            raise ValueError("informe ao menos uma --saida")
        resultado = avaliar_arquivos(args.gabarito, args.saidas, args.raiz.resolve())
        texto = json.dumps(resultado, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        if args.relatorio:
            gravar_novo(args.relatorio, texto, [args.gabarito, *args.saidas])
        else:
            print(texto, end="")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8")
    raise SystemExit(main())
