#!/usr/bin/env python3
"""Hook de exemplo (Cap. 8): bloqueia escrita e edição em arquivos dentro de originais/.

Feito para o evento PreToolUse do Claude Code (verificado em out/2026): o agente
envia, pela entrada padrão, um JSON com tool_name e tool_input.file_path.
Saída com código 2 = a ação é bloqueada e a mensagem de stderr volta ao agente.

Limite importante: o filtro "Edit|Write" não dispara para comandos de terminal.
Por isso este hook complementa — não substitui — a trava de somente leitura
dos originais no sistema operacional (Cap. 4), cuja eficácia depende dos privilégios.
Falha de inicialização/timeout é controlada pelo cliente: use onFailure:block
no hook de comando, em Claude Code 2.1.295+. O retorno 2 do script não testa essa camada.
"""

import json
import sys
from pathlib import Path

PROTEGIDO = "originais"


def main():
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    try:
        evento = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeError):
        # Trava de segurança falha FECHADA: se não entende a entrada, bloqueia.
        print("Bloqueado pelo hook: entrada não reconhecida.", file=sys.stderr)
        return 2
    if (not isinstance(evento, dict) or not isinstance(evento.get("tool_input"), dict)
            or not isinstance(evento['tool_input'].get('file_path'), str)
            or not evento['tool_input']['file_path'].strip()
            or not isinstance(evento.get('cwd', '.'), str)):
        print("Bloqueado pelo hook: entrada não reconhecida.", file=sys.stderr)
        return 2
    caminho = evento['tool_input']['file_path']
    partes = caminho.replace("\\", "/").casefold().split("/")
    try:
        resolvido = (Path(evento.get('cwd', '.')) / caminho).resolve()
    except (OSError, ValueError, RuntimeError):
        print("Bloqueado pelo hook: caminho não reconhecido.", file=sys.stderr)
        return 2
    if PROTEGIDO in partes or PROTEGIDO in [p.casefold() for p in resolvido.parts]:
        print(f"Bloqueado pelo hook: '{caminho}' está em {PROTEGIDO}/, que é somente leitura. "
              f"Trabalhe na cópia em trabalho/.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
