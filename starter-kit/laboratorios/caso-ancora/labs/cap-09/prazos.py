#!/usr/bin/env python3
"""Painel de prazos do caso — laboratório do Cap. 9 (ferramenta determinística).

Lê procedimentos.csv e registro-expedicao.csv e calcula, para uma data de
referência, o vencimento e a situação de cada prazo. Contagem conforme o
CPP, art. 798: não se computa o dia do começo, inclui-se o do vencimento
(§ 1º); o prazo que termina em domingo ou feriado prorroga-se até o dia
útil imediato (§ 3º). Feriados: informe-os em feriados.txt (uma data
AAAA-MM-DD por linha), se houver.

A ferramenta APOIA o controle; não substitui a certificação do prazo nos
autos pelo escrivão (CPP, art. 798, § 2º) nem as normas da unidade.
Perfil didático: prazo positivo em dias corridos, domingo/feriado informado
prorrogado e sábado mantido. A seleção do regime, termo inicial, calendário
e suspensões exige conferência humana anterior; não calcula prescrição nem
implementa impedimentos, art. 798-A ou todos os regimes de prazo.

Uso:
    python prazos.py [data-de-referencia AAAA-MM-DD] [pasta-dos-csv]
Exemplo:
    python prazos.py 2026-09-03
"""

import csv
import sys
from datetime import date, timedelta
from pathlib import Path

VERSAO = "1.0.1"


def vencimento(inicio: date, dias: int, feriados: set) -> date:
    if type(dias) is not int or dias <= 0:
        raise ValueError("prazo_dias deve ser inteiro positivo neste perfil didático")
    fim = inicio + timedelta(days=dias)  # exclui o dia do começo, inclui o do vencimento
    while fim.weekday() == 6 or fim in feriados:  # domingo ou feriado
        fim += timedelta(days=1)
    return fim


def situacao(venc: date, ref: date, resposta: str) -> str:
    if resposta and date.fromisoformat(resposta) <= ref:
        r = date.fromisoformat(resposta)
        return "respondido no prazo" if r <= venc else f"respondido com {(r - venc).days} dia(s) de atraso"
    if ref > venc:
        return f"VENCIDO há {(ref - venc).days} dia(s)"
    return f"em aberto, vence em {(venc - ref).days} dia(s)"


def executar(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ref = date.fromisoformat(argv[0]) if argv else date.today()
    if len(argv) > 2:
        raise ValueError("uso: prazos.py [AAAA-MM-DD] [pasta-dos-csv]")
    pasta = Path(argv[1]) if len(argv) > 1 else Path(__file__).parent
    fer_arq = pasta / "feriados.txt"
    feriados = {date.fromisoformat(l.strip()) for l in fer_arq.read_text(encoding="utf-8").splitlines()
                if l.strip()} if fer_arq.exists() else set()

    linhas = []
    with (pasta / "procedimentos.csv").open(encoding="utf-8", newline="") as f:
        for p in csv.DictReader(f):
            v = vencimento(date.fromisoformat(p["instauracao"]), int(p["prazo_dias"]), feriados)
            linhas.append({"item": f"Prazo do {p['procedimento']} ({p['base_legal_prazo']})",
                           "inicio": p["instauracao"], "prazo_dias": p["prazo_dias"],
                           "vencimento": v.isoformat(), "resposta": "",
                           "situacao": situacao(v, ref, "")})
    with (pasta / "registro-expedicao.csv").open(encoding="utf-8", newline="") as f:
        for o in csv.DictReader(f):
            v = vencimento(date.fromisoformat(o["data_expedicao"]), int(o["prazo_resposta_dias"]), feriados)
            resposta = o["data_resposta"]
            if resposta and date.fromisoformat(resposta) < date.fromisoformat(o["data_expedicao"]):
                raise ValueError(f"{o['documento']}: resposta anterior à expedição")
            # O corte histórico não deve apresentar recebimentos futuros.
            recebida = resposta if resposta and date.fromisoformat(resposta) <= ref else ""
            linhas.append({"item": f"{o['documento']} — {o['destinatario']}",
                           "inicio": o["data_expedicao"], "prazo_dias": o["prazo_resposta_dias"],
                           "vencimento": v.isoformat(), "resposta": recebida,
                           "situacao": situacao(v, ref, o["data_resposta"])})

    for linha in linhas:
        if date.fromisoformat(linha["inicio"]) > ref:
            linha["situacao"] = "ainda não iniciado na data de referência"

    saida = pasta / "painel-prazos.csv"
    with saida.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["item", "inicio", "prazo_dias", "vencimento", "resposta", "situacao"],
                           lineterminator="\n")
        w.writeheader()
        w.writerows(linhas)

    print(f"Painel de prazos — referência {ref.isoformat()} — prazos.py v{VERSAO}")
    for l in linhas:
        print(f"- {l['item']}: vence {l['vencimento']} → {l['situacao']}")
    print(f"Gravado em {saida}")
    return 0


def main(argv):
    try:
        return executar(argv)
    except (OSError, ValueError, KeyError, OverflowError) as erro:
        print(f"Entrada recusada; painel não gerado: {erro}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
