#!/usr/bin/env python3
"""Fluxo financeiro do caso — laboratório do Cap. 11 (ferramenta determinística).

Lê CSVs previamente compatibilizados às colunas do laboratório e normaliza cada lançamento como
uma transferência (data, hora, origem, destino, valor), elimina duplicatas
— o mesmo PIX aparece no extrato de quem pagou e no de quem recebeu — e
calcula, por conta: entradas, saídas observadas, valor não explicado nos dados e
tempo de repasse (da entrada mais recente até a primeira saída).

Se receber também a resposta do banco, confere cada transferência contra
ela (mesma conta, mesma contraparte, mesmo valor) e marca correspondência parcial.
A resposta do banco do caso não traz data de lançamento: a conferência é
feita sem data, e isso fica dito no resultado.

Preserva EndToEndId/end_to_end_id/id_transacao quando recebido. Sem ID,
colisões são recusadas; --espelhos-sinteticos é exceção limitada aos dois
nomes de extrato do caso-âncora, após conferência manual documentada.

Não usa modelo de linguagem. Grava fluxo.csv, contas.csv e fluxo.mmd
(grafo em Mermaid).

Uso:
    python fluxo.py <extrato1.csv> [<extrato2.csv> ...] [--resposta resposta.csv] [--saida pasta]
"""

import argparse
import csv
import sys
from collections import defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

VERSAO = "1.1.0"


def moeda(texto):
    """Contrato CSV: ponto decimal, valor finito, exatamente representável em centavos."""
    valor = Decimal(texto)
    if not valor.is_finite() or valor != valor.quantize(Decimal('0.01')):
        raise ValueError(f"valor monetário inválido: {texto!r}")
    return valor


def ler_extrato(caminho: Path):
    with caminho.open(encoding="utf-8", newline="") as f:
        for i, l in enumerate(csv.DictReader(f), start=2):
            valor = abs(moeda(l["valor"]))
            datetime.fromisoformat(f"{l['data']}T{l['hora']}")
            identificadores = {l[c].strip() for c in ("EndToEndId", "end_to_end_id", "id_transacao") if l.get(c, "").strip()}
            if len(identificadores) > 1:
                raise ValueError(f"{caminho.name}:{i}: identificadores conflitantes")
            yield {
                "data": l["data"], "hora": l["hora"],
                "origem": l["conta_origem"], "destino": l["conta_destino"],
                "valor": valor,
                "id_transacao": next(iter(identificadores), ""),
                "banco_destino": l.get("banco_destino", ""),
                "fonte": f"{caminho.name}:{i}",
            }


def ler_resposta(caminho: Path):
    with caminho.open(encoding="utf-8", newline="") as f:
        return [dict(l, _linha=i) for i, l in enumerate(csv.DictReader(f), start=2)]


def corroborada(t, resposta):
    fontes = []
    for r in resposta:
        v = moeda(r["valor"])
        if r["conta"] == t["destino"] and r["contraparte"] == t["origem"] and v == t["valor"]:
            fontes.append(f"resposta:{r['_linha']} (recebido)")
        if r["conta"] == t["origem"] and r["contraparte"] == t["destino"] and v == -t["valor"]:
            fontes.append(f"resposta:{r['_linha']} (enviado)")
    return fontes


def executar(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('extratos', nargs='+', type=Path)
    parser.add_argument('--resposta', type=Path)
    parser.add_argument('--saida', type=Path, default=Path('.'))
    parser.add_argument('--espelhos-sinteticos', action='store_true', help='convenção conferida somente para os dois extratos do caso-âncora')
    args = parser.parse_args(argv)
    extratos, resposta_arq, saida = args.extratos, args.resposta, args.saida
    nomes = [a.name for a in extratos]
    if len({a.resolve() for a in extratos}) != len(extratos):
        raise ValueError('mesmo extrato informado mais de uma vez')
    if args.espelhos_sinteticos and (len(extratos) != 2 or set(nomes) != {'extrato-bancario-vitima.csv', 'extrato-bancario-contas-passagem.csv'}):
        raise ValueError('--espelhos-sinteticos limitado aos dois extratos nomeados do caso-âncora; confira seu conteúdo antes de usar')

    # 1. normalizar e eliminar duplicatas
    unicas, ids_por_campos = {}, defaultdict(set)
    for arq in extratos:
        for t in ler_extrato(arq):
            campos = (t['data'], t['hora'], t['origem'], t['destino'], t['valor'])
            ident = t['id_transacao']
            vistos = ids_por_campos[campos]
            if vistos and ((ident and '' in vistos) or (not ident and any(vistos))):
                raise ValueError(f"colisão entre lançamento com e sem ID: {t['fonte']}; conferência manual necessária")
            vistos.add(ident)
            chave = ('id', ident) if ident else ('campos', campos)
            if chave in unicas:
                anterior = unicas[chave]
                campos_anteriores = (anterior['data'], anterior['hora'], anterior['origem'], anterior['destino'], anterior['valor'])
                if campos != campos_anteriores:
                    raise ValueError(f"mesmo ID com dados diferentes: {anterior['fonte']} e {t['fonte']}")
                if not ident and (not args.espelhos_sinteticos or arq.name in anterior['_arquivos']):
                    raise ValueError(f"pendência de colisão sem identificador: {anterior['fonte']} e {t['fonte']}; não houve fusão")
                if anterior['banco_destino'] and t['banco_destino'] and anterior['banco_destino'] != t['banco_destino']:
                    raise ValueError(f"instituição de destino conflitante: {anterior['fonte']} e {t['fonte']}")
                unicas[chave]["fonte"] += " · " + t["fonte"]
                unicas[chave]["banco_destino"] = unicas[chave]["banco_destino"] or t["banco_destino"]
                anterior['_arquivos'].add(arq.name)
            else:
                t['_arquivos'] = {arq.name}
                unicas[chave] = t
    transf = sorted(unicas.values(), key=lambda t: (t["data"], t["hora"]))

    resposta = ler_resposta(resposta_arq) if resposta_arq else []
    for t in transf:
        c = corroborada(t, resposta) if resposta else []
        t["resposta_banco"] = "correspondência parcial SEM data: " + " · ".join(c) if c else ("não consta correspondência parcial" if resposta else "não conferida")

    # 2. Somas observadas não certificam saldo nem cobertura integral da conta.
    contas = defaultdict(lambda: {"entradas": Decimal(0), "saidas": Decimal(0), "momentos_entrada": [], "primeira_saida": None})
    for t in transf:
        quando = datetime.fromisoformat(f"{t['data']}T{t['hora']}")
        o, d = contas[t["origem"]], contas[t["destino"]]
        o["saidas"] += t["valor"]
        d["entradas"] += t["valor"]
        o["primeira_saida"] = o["primeira_saida"] or quando
        d["momentos_entrada"].append(quando)

    saida.mkdir(parents=True, exist_ok=True)
    with (saida / "fluxo.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["data", "hora", "origem", "destino", "valor", "banco_destino",
                                          "id_transacao", "fonte", "resposta_banco"], lineterminator="\n")
        w.writeheader()
        w.writerows([{k: (f"{t['valor']:.2f}" if k == 'valor' else t[k]) for k in w.fieldnames} for t in transf])

    with (saida / "contas.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["conta", "entradas", "saidas", "valor_nao_explicado", "repasse_minutos", "cobertura_saidas"])
        for nome, c in sorted(contas.items()):
            repasse = ""
            anteriores = [m for m in c["momentos_entrada"] if c["primeira_saida"] and m <= c["primeira_saida"]]
            if anteriores:
                repasse = round((c["primeira_saida"] - max(anteriores)).total_seconds() / 60, 1)
            diferenca = f"{c['entradas'] - c['saidas']:.2f}" if c["entradas"] else ""
            w.writerow([nome, f"{c['entradas']:.2f}", f"{c['saidas']:.2f}", diferenca, repasse, 'não determinada'])

    with (saida / "fluxo.mmd").open("w", encoding="utf-8") as f:
        f.write("flowchart LR\n")
        for t in transf:
            rot = f"R$ {t['valor']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            f.write(f'    {t["origem"].replace("-", "_")}["{t["origem"]}"] -->|"{t["data"][8:10]}/{t["data"][5:7]} {t["hora"][:5]} · {rot}"| '
                    f'{t["destino"].replace("-", "_")}["{t["destino"]}"]\n')

    print(f"fluxo.py v{VERSAO} — {len(transf)} transferência(s) única(s)")
    for t in transf:
        print(f"- {t['data']} {t['hora']}  {t['origem']} → {t['destino']}  R$ {t['valor']:.2f}  [{t['resposta_banco']}]")
    print("Contas:")
    with (saida / "contas.csv").open(encoding="utf-8") as f:
        for l in list(csv.DictReader(f)):
            print(f"- {l['conta']}: entradas {l['entradas']} · saídas {l['saidas']} · "
                  f"valor não explicado {l['valor_nao_explicado'] or '—'} · repasse {l['repasse_minutos'] or '—'} min · cobertura {l['cobertura_saidas']}")
    if resposta:
        print("Atenção: a conferência com a resposta do banco é feita SEM data (a resposta não traz data de lançamento).")
    print(f"Gravados fluxo.csv, contas.csv e fluxo.mmd em {saida}")
    return 0


def main(argv):
    try:
        return executar(argv)
    except (OSError, ValueError, KeyError, InvalidOperation) as erro:
        print(f"Entrada recusada; novos produtos não gerados: {erro}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
