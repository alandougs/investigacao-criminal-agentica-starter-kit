#!/usr/bin/env python3
"""Extração e normalização de entidades — laboratório do Cap. 10 (ferramenta determinística).

Lê arquivos .md, .txt, .csv e .docx de uma pasta e extrai, com expressões
regulares, telefones, contas sintéticas do caso, valores em reais, datas e
horários. Cada ocorrência sai com o arquivo e a linha (ou o parágrafo, no
.docx) de origem, o texto original e a forma normalizada — para que o mesmo
telefone escrito de três jeitos apareça como UMA entidade.

Não usa modelo de linguagem. Não lê PDF (use o texto já extraído).
DOCX também gera cópia pesquisável <nome>.docx.txt junto ao CSV de saída,
com posição física XML por parágrafo; confira a conversão no original.

Uso:
    python entidades.py <pasta-de-entrada> [arquivo-de-saida.csv]
"""

import csv
import re
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

VERSAO = "1.0.1"

PADROES = {
    # (14) 90000-0001 · +55 14 90000 0042 · +55-14-90000-0042
    "telefone": re.compile(r"(?:\+55[\s-]?)?\(?\b(\d{2})\)?[\s-]?(9?\d{4})[\s-]?(\d{4})\b"),
    "conta": re.compile(r"\bCONTA[\s-](PASSAGEM|VITIMA)[\s-](\d{4})\b", re.I),
    "valor": re.compile(r"R\$\s?(\d{1,3}(?:\.\d{3})*,\d{2})"),
    "data": re.compile(r"\b(\d{2})/(\d{2})/(\d{4})\b|\b(\d{4})-(\d{2})-(\d{2})\b"),
    "hora": re.compile(r"\b([01]?\d|2[0-3])(?:h(?:([0-5]\d)(?::([0-5]\d))?)?|:([0-5]\d)(?::([0-5]\d))?)(?![\w:])"),
}


def normalizar(tipo, m):
    if tipo == "telefone":
        return f"+55{m.group(1)}{m.group(2)}{m.group(3)}"
    if tipo == "conta":
        return f"CONTA-{m.group(1).upper()}-{m.group(2)}"
    if tipo == "valor":
        return m.group(1).replace(".", "").replace(",", ".")
    if tipo == "data":
        if m.group(1):
            return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
        return f"{m.group(4)}-{m.group(5)}-{m.group(6)}"
    if tipo == "hora":
        hora, minuto, segundo = int(m.group(1)), m.group(2) or m.group(4), m.group(3) or m.group(5)
        if minuto is None:
            return f"{hora:02d}h"  # não inventa os minutos de '20h'
        return f"{hora:02d}:{minuto}" + (f":{segundo}" if segundo is not None else "")
    return m.group(0)


def linhas_de(arq: Path):
    """Posição DOCX é parágrafo físico XML, incluindo vazios; não é o § impresso."""
    if arq.suffix.lower() == ".docx":
        xml = zipfile.ZipFile(arq).read("word/document.xml").decode("utf-8")
        paragrafos = re.findall(r"<w:p[ >].*?</w:p>", xml, re.S)
        for i, p in enumerate(paragrafos, 1):
            texto = "".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", p, re.S))
            if texto.strip():
                yield f"parágrafo {i}", texto
    else:
        for i, linha in enumerate(arq.read_text(encoding="utf-8").splitlines(), 1):
            yield f"linha {i}", linha


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if not argv:
        print(__doc__)
        return 2
    entrada = Path(argv[0])
    saida = Path(argv[1]) if len(argv) > 1 else Path("entidades.csv")
    if not entrada.is_dir():
        print(f"Pasta de entrada não encontrada: {entrada}", file=sys.stderr)
        return 1

    registros, textos_docx = [], {}
    for arq in sorted(entrada.iterdir()):
        if not arq.is_file() or arq.suffix.lower() not in {".md", ".txt", ".csv", ".docx"}:
            continue
        linhas = list(linhas_de(arq))
        if arq.suffix.lower() == '.docx':
            textos_docx[arq.name + '.txt'] = '\n'.join(f'{pos}: {texto}' for pos, texto in linhas) + '\n'
        for pos, texto in linhas:
            ocupado = []
            for tipo in ("telefone", "conta", "valor", "data", "hora"):
                for m in PADROES[tipo].finditer(texto):
                    if any(a <= m.start() < b for a, b in ocupado):
                        continue  # trecho já reconhecido (evita ler parte de um telefone como hora)
                    ocupado.append((m.start(), m.end()))
                    registros.append({"tipo": tipo, "normalizado": normalizar(tipo, m),
                                      "original": m.group(0), "arquivo": arq.name, "posicao": pos})

    saida.parent.mkdir(parents=True, exist_ok=True)
    with saida.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["tipo", "normalizado", "original", "arquivo", "posicao"],
                           lineterminator="\n")
        w.writeheader()
        w.writerows(registros)

    for nome, texto in textos_docx.items():
        derivado = saida.parent / nome
        if derivado.resolve() == (entrada / nome).resolve():
            raise ValueError('cópia de texto deve ficar separada dos originais')
        derivado.write_text(texto, encoding='utf-8')

    resumo = defaultdict(set)
    for r in registros:
        resumo[(r["tipo"], r["normalizado"])].add(r["original"])
    print(f"entidades.py v{VERSAO} — {len(registros)} ocorrência(s) em {entrada}")
    for (tipo, norm), originais in sorted(resumo.items()):
        if tipo in ("telefone", "conta") or len(originais) > 1:
            print(f"- {tipo} {norm}: {len(originais)} forma(s) escrita(s): {' | '.join(sorted(originais))}")
    print(f"Gravado em {saida}")
    for nome in textos_docx:
        print(f"Texto DOCX derivado em {saida.parent / nome}; conferir no original")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
