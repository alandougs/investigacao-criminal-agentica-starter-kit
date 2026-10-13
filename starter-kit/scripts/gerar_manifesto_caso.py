"""Gera e verifica manifesto SHA-256 de uma pasta de caso.

Uso: python scripts/gerar_manifesto_caso.py gerar --raiz <pasta>
     python scripts/gerar_manifesto_caso.py verificar --raiz <pasta>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from pathlib import PurePosixPath

NOME_MANIFESTO = "manifesto-sha256.json"


def hash_arquivo(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
            digest.update(bloco)
    return digest.hexdigest()


def arquivos_da_pasta(raiz: Path, escopo: str = ".") -> list[Path]:
    if not raiz.is_dir():
        raise ValueError("pasta do caso ausente")
    if escopo not in (".", "originais"):
        raise ValueError("escopo deve ser . ou originais")
    base = raiz if escopo == "." else raiz / escopo
    if not base.is_dir() or base.is_symlink() or base.is_junction():
        raise ValueError("pasta do escopo ausente ou é link simbólico/junção")
    caminhos = list(base.rglob("*"))
    if any(p.is_symlink() or p.is_junction() for p in caminhos):
        raise ValueError("links simbólicos/junções não são aceitos no inventário")
    return sorted((p for p in caminhos if p.is_file() and p != raiz / NOME_MANIFESTO),
                  key=lambda p: p.relative_to(raiz).as_posix())


def gerar(raiz: Path, escopo: str = ".", substituir: bool = False) -> Path:
    raiz = raiz.resolve()
    destino = raiz / NOME_MANIFESTO
    if destino.exists() and not substituir:
        raise ValueError("manifesto já existe; preserve a referência antes de usar --substituir")
    if destino.is_symlink():
        raise ValueError("manifesto não pode ser link simbólico")
    dados = {
        "formato": "manifesto-sha256-caso",
        "versao": 1,
        "escopo": escopo,
        "arquivos": [
            {"caminho": p.relative_to(raiz).as_posix(), "sha256": hash_arquivo(p), "bytes": p.stat().st_size}
            for p in arquivos_da_pasta(raiz, escopo)
        ],
    }
    with destino.open("w", encoding="utf-8", newline="\n") as arquivo:
        arquivo.write(json.dumps(dados, ensure_ascii=False, indent=2) + "\n")
    return destino


def verificar(raiz: Path) -> list[str]:
    raiz = raiz.resolve()
    manifesto = raiz / NOME_MANIFESTO
    if not manifesto.is_file() or manifesto.is_symlink():
        return [f"manifesto ausente: {manifesto}"]
    try:
        dados = json.loads(manifesto.read_text(encoding="utf-8"))
        if (not isinstance(dados, dict) or dados.get("formato") != "manifesto-sha256-caso"
                or type(dados.get("versao")) is not int or dados["versao"] != 1
                or not isinstance(dados.get("arquivos"), list)):
            raise ValueError("esquema inválido")
        escopo = dados.get("escopo", ".")
        atuais = {p.relative_to(raiz).as_posix() for p in arquivos_da_pasta(raiz, escopo)}
        registrados = set()
        for item in dados["arquivos"]:
            if not isinstance(item, dict):
                raise ValueError("registro inválido")
            caminho = item.get("caminho")
            if not isinstance(caminho, str) or not caminho:
                raise ValueError("caminho inválido")
            partes = PurePosixPath(caminho)
            if (partes.is_absolute() or "\\" in caminho or ":" in caminho
                    or ".." in partes.parts or partes.as_posix() != caminho
                    or caminho == NOME_MANIFESTO
                    or (escopo == "originais" and not caminho.startswith("originais/"))
                    or not (raiz / caminho).resolve().is_relative_to(raiz)):
                raise ValueError("caminho fora do escopo ou não canônico")
            if caminho.casefold() in registrados:
                raise ValueError("caminho duplicado")
            registrados.add(caminho.casefold())
            if (not isinstance(item.get("sha256"), str)
                    or not re.fullmatch(r"[0-9a-f]{64}", item["sha256"])
                    or type(item.get("bytes")) is not int or item["bytes"] < 0):
                raise ValueError("hash/tamanho inválido")
    except (OSError, ValueError, TypeError) as erro:
        return [f"manifesto inválido: {erro}"]
    erros: list[str] = []
    esperados = {item["caminho"] for item in dados["arquivos"]}
    for caminho in sorted(atuais - esperados):
        erros.append(f"não registrado: {caminho}")
    for item in dados["arquivos"]:
        arquivo = raiz / item["caminho"]
        if not arquivo.is_file():
            erros.append(f"ausente: {item['caminho']}")
        elif hash_arquivo(arquivo) != item["sha256"]:
            erros.append(f"hash divergente: {item['caminho']}")
        elif arquivo.stat().st_size != item["bytes"]:
            erros.append(f"tamanho divergente: {item['caminho']}")
    return erros


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("acao", choices=("gerar", "verificar"))
    parser.add_argument("--raiz", required=True, type=Path)
    parser.add_argument("--escopo", choices=(".", "originais"), default=".")
    parser.add_argument("--substituir", action="store_true")
    args = parser.parse_args()
    if args.acao == "gerar":
        try:
            print(gerar(args.raiz, args.escopo, args.substituir))
            return 0
        except (OSError, ValueError) as erro:
            print(f"Não foi possível gerar: {erro}")
            return 1
    erros = verificar(args.raiz)
    if erros:
        print("\n".join(erros))
        return 1
    print("Manifesto verificado sem divergências.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
