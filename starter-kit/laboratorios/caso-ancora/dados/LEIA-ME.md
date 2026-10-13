# Dados do caso-âncora — estado dos arquivos (09/10/2026)

> DADOS INTEGRALMENTE FICTÍCIOS E SINTÉTICOS — USO DIDÁTICO (P10).

Todos os arquivos seguem o cânone v2 (`../ENREDO.md` e `../CRONOLOGIA.md`): Marta, a vítima, é a compradora; Valdir, dono do veículo, é testemunha.

| Arquivo | Chega ao caso em | Capítulos | Gerador |
|---|---|---|---|
| `boletim-ocorrencia.md` | 08/08/2026 | 1, 2, 4, 5, 9, 10, 22 | escrito à mão (v2) |
| `extrato-bancario-vitima.csv` | 08/08/2026 (entregue pela vítima) | 1, 4, 10, 11 | `gerar_datasets_pendentes.py` |
| `termos-declaracao.md` / `.docx` | 08/08/2026 | 10, 16 | `gerar_datasets_v2.py` |
| `perfil-osint-ricardo-autos-premium.md` | capturas de 07/08; coleta policial de 12/08 | 10, 12, 16 | `gerar_datasets_v2.py` |
| `oficio-banco-trilha.pdf`, `oficio-conecta-movel.pdf` | expedidos em 14/08/2026 | 9 | `gerar_datasets_pendentes.py` |
| `extrato-bancario-contas-passagem.csv` | 20/08/2026 (adiantamento do Banco Trilha) | 8, 10, 11 | `gerar_datasets_pendentes.py` |
| `resposta-banco-trilha.csv` | 28/08/2026 (resposta formal, parcial) | 9, 10, 11 | `gerar_datasets_v2.py` |
| `resposta-conecta-movel.csv` | 02/09/2026 | 9, 16 | `gerar_datasets_v2.py` |
| `extrato-telefonico-erb.csv` | 02/09/2026 (normalizado da resposta) | 9, 10, 12, 16, 18 | `gerar_datasets_v2.py` |
| `oficio-banco-horizonte-019-2026.pdf` | expedido em 04/09/2026 | 9, 11 | `gerar_datasets_v2.py` |
| `extracao-celular-vitima.html` e `extracao-celular-vitima/` | 08/09/2026 | 13 | `gerar_datasets_v2.py` |
| `audio-reserva-sintetico.wav`, `comprovante-reserva-sintetico.png` | recebidos por Marta em 05/08; ao caderno em 09/09 | 14 | `gerar_midias_sinteticas.py` |
| `midia-original-sintetica.png`, `midia-manipulada-sintetica.png` | 15/09/2026 | 15 | `gerar_midias_sinteticas.py` |
| `resposta-banco-horizonte-digital.csv` | 18/09/2026 | 11, 16, 23 | `gerar_datasets_v2.py` |
| `documento-teste-prompt-injection.pdf` | 01/10/2026 | 20 | `gerar_datasets_pendentes.py` |

Para regenerar os arquivos do cânone v2: `python scripts/gerar_datasets_v2.py` (na raiz do repositório). O áudio exige eSpeak NG com voz `pt-br` (`python scripts/gerar_midias_sinteticas.py --motor espeak`).
