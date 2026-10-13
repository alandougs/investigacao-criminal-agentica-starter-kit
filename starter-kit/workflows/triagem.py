#!/usr/bin/env python3
"""Triagem documental determinística, com log — laboratório do Cap. 8.

Lê todos os arquivos de uma pasta de entrada e produz:
  - triagem.csv        inventário: arquivo, extensão, bytes, sha256, tipo, registros
  - triagem-log.jsonl  registro de cada etapa, com data/hora, versão e hash do próprio script

A mesma entrada gera sempre o mesmo triagem.csv (o log muda só nas datas/horas).
Nenhum modelo de linguagem é usado: é um workflow determinístico (P6).

Uso:
    python triagem.py <pasta-de-entrada> <pasta-de-saida>
Exemplo:
    python triagem.py laboratorios/caso-ancora/dados trabalho/triagem
"""

import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

VERSAO = "1.0.1"


def sha256(caminho: Path) -> str:
    h = hashlib.sha256()
    with caminho.open("rb") as f:
        for bloco in iter(lambda: f.read(65536), b""):
            h.update(bloco)
    return h.hexdigest()


def tipo_e_registros(caminho: Path):
    ext = caminho.suffix.lower()
    if ext == ".csv":
        with caminho.open(encoding="utf-8-sig", newline="") as f:
            linhas = list(csv.reader(f))
        colunas = ";".join(linhas[0]) if linhas else ""
        return f"CSV (colunas: {colunas})", max(len(linhas) - 1, 0)
    if ext == ".md":
        texto = caminho.read_text(encoding="utf-8")
        if texto.startswith("---"):
            for linha in texto.split("---", 2)[1].splitlines():
                if linha.strip().startswith("tipo_documento:"):
                    return linha.split(":", 1)[1].strip(), ""
        return "Markdown (sem tipo_documento)", ""
    return f"não classificado ({ext or 'sem extensão'})", ""


def main(argv):
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8")
    if len(argv) != 2:
        print(__doc__)
        return 2
    entrada, saida = Path(argv[0]), Path(argv[1])
    if not entrada.is_dir():
        print(f"Pasta de entrada não encontrada: {entrada}", file=sys.stderr)
        return 1
    entrada, saida = entrada.resolve(), saida.resolve()
    if saida.is_relative_to(entrada):
        print("A saída deve ficar fora da pasta de entrada.", file=sys.stderr)
        return 1
    if any(p.is_symlink() or p.is_junction() for p in entrada.iterdir()):
        print("Links simbólicos/junções não são aceitos na entrada.", file=sys.stderr)
        return 1
    saida.mkdir(parents=True, exist_ok=True)
    log_path = saida / "triagem-log.jsonl"

    def registrar(evento, **dados):
        dados.update(evento=evento, momento=datetime.now(timezone.utc).isoformat(timespec="seconds"))
        with log_path.open("a", encoding="utf-8") as log:
            log.write(json.dumps(dados, ensure_ascii=False) + "\n")

    registrar("inicio", versao=VERSAO, script_sha256=sha256(Path(__file__)),
              entrada=entrada.as_posix())
    arquivos = sorted(p for p in entrada.iterdir() if p.is_file() and not p.name.startswith("."))
    linhas = []
    for arq in arquivos:
        tipo, registros = tipo_e_registros(arq)
        linha = {"arquivo": arq.name, "extensao": arq.suffix.lower(), "bytes": arq.stat().st_size,
                 "sha256": sha256(arq), "tipo": tipo, "registros": registros}
        linhas.append(linha)
        registrar("arquivo_triado", **linha)
    with (saida / "triagem.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["arquivo", "extensao", "bytes", "sha256", "tipo", "registros"],
                           lineterminator="\n")
        w.writeheader()
        w.writerows(linhas)
    registrar("fim", arquivos_triados=len(linhas), saida=(saida / "triagem.csv").as_posix())
    print(f"{len(linhas)} arquivo(s) triado(s). Saída: {saida / 'triagem.csv'} · Log: {log_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
