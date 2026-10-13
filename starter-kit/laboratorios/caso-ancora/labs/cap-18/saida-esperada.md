# Relatório do analisador de extrato telefônico/ERB

> Resultado determinístico sobre dado sintético. Não conclui localização, identidade ou conduta.

- **Ferramenta:** `analisador_erb.py` v1.1.1
- **Entrada:** `extrato-telefonico-erb.csv`
- **SHA-256 da entrada:** `9da3f1ae1fc63723ed8806e387b8b0b248efd9e1c730089a0eae0d5d90569b62`
- **Linhas lidas / processadas / não processadas:** 7 / 7 / 0

> Coluna observacao presente e ignorada.

## Eventos por ERB

| ERB | Nome | Eventos | Primeiro | Último |
|---|---|---:|---|---|
| ERB-VRC-01 | Torre Centro | 1 | 2026-07-30 09:18:00 | 2026-07-30 09:18:00 |
| ERB-VRC-02 | Torre Bairro Industrial | 3 | 2026-08-03 18:40:00 | 2026-08-05 16:02:18 |
| ERB-VRC-03 | Torre Rodovia Fictícia | 2 | 2026-08-06 10:15:04 | 2026-08-06 17:30:00 |
| ERB-VRC-04 | Torre Terminal | 1 | 2026-08-07 08:55:45 | 2026-08-07 08:55:45 |

## Linha do tempo

| Data/hora | Tipo | Origem normalizada | Destino normalizado | ERB | Origem original | Destino original |
|---|---|---|---|---|---|---|
| 2026-07-30 09:18:00 | ATIVACAO_SIM | +5514900000042 |  | ERB-VRC-01 | +55-14-90000-0042 |  |
| 2026-08-03 18:40:00 | DADOS | +5514900000042 | +5514900000002 | ERB-VRC-02 | +55-14-90000-0042 | +55-14-90000-0002 |
| 2026-08-04 09:40:12 | DADOS | +5514900000042 | +5514900000001 | ERB-VRC-02 | +55-14-90000-0042 | +55-14-90000-0001 |
| 2026-08-05 16:02:18 | DADOS | +5514900000042 | +5514900000001 | ERB-VRC-02 | +55-14-90000-0042 | +55-14-90000-0001 |
| 2026-08-06 10:15:04 | DADOS | +5514900000042 | +5514900000001 | ERB-VRC-03 | +55-14-90000-0042 | +55-14-90000-0001 |
| 2026-08-06 17:30:00 | DADOS | +5514900000042 | +5514900000002 | ERB-VRC-03 | +55-14-90000-0042 | +55-14-90000-0002 |
| 2026-08-07 08:55:45 | DADOS | +5514900000042 |  | ERB-VRC-04 | +55-14-90000-0042 |  |

## Contatos por frequência

| Contraparte | Eventos | Primeiro | Último |
|---|---:|---|---|
| +5514900000001 | 3 | 2026-08-04 09:40:12 | 2026-08-06 10:15:04 |
| +5514900000002 | 2 | 2026-08-03 18:40:00 | 2026-08-06 17:30:00 |

## Primeiro e último evento por linha de origem

| Linha | Eventos | Primeiro | Tipo | ERB | Último | Tipo | ERB |
|---|---:|---|---|---|---|---|---|
| +5514900000042 | 7 | 2026-07-30 09:18:00 | ATIVACAO_SIM | ERB-VRC-01 | 2026-08-07 08:55:45 | DADOS | ERB-VRC-04 |

## Linhas não processadas

| Linha CSV | data_hora recebida |
|---:|---|

## Avisos

- A ERB indica a antena que atendeu o evento, não a posição exata do aparelho.
- O fuso horário é o do arquivo; confirme com a operadora.
- O titular de uma linha não é, por isso, quem a usava.
