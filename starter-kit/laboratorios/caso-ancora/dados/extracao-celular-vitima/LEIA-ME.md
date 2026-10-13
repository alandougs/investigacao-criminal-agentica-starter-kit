# Pacote sintético de extração do celular da vítima

> DOCUMENTO INTEGRALMENTE FICTÍCIO E SINTÉTICO - USO DIDÁTICO. Formato genérico, desenhado para o livro; não imita o layout de nenhuma ferramenta comercial.

- **Aparelho:** VITIMA-DEVICE-0001 (sintético), entregue voluntariamente por Marta Helena Bezerra.
- **Relatório devolvido pelo setor técnico em:** 08/09/2026 (cânone, Cap. 13).
- **Gerador:** `scripts/gerar_datasets_v2.py` v2.0.0 (semente 20260908).

| Arquivo | Conteúdo |
|---|---|
| `mensagens.csv` | 150 mensagens de 8 conversas; `anexo_sha256` preenchido quando a mensagem tem mídia |
| `contatos.csv` | agenda do aparelho |
| `midias.csv` | mídias recebidas nas conversas, com SHA-256 do arquivo em `../` |
| `urls.csv` | endereços abertos no aplicativo da ElosNet |
| `chamadas.csv` | registro de chamadas (metadado: não traz o conteúdo da conversa) |

O pacote organiza o que estava no aparelho. Não autentica mensagens, voz, imagem, conta ou pessoa.
