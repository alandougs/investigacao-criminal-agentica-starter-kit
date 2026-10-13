# Cap. 7 — Checklist de risco de plugin de terceiros

Preencha **antes de instalar**, abrindo os arquivos do pacote (não confie no anúncio). Uma resposta "sim" na coluna *Alerta* é motivo para parar e consultar o administrador de TI ou de segurança da unidade.

| # | Pergunta | Onde olhar | Resposta | Alerta? |
|---|---|---|---|---|
| 1 | Há autor ou organização identificável, com contato e repositório? | manifesto, README | | |
| 2 | Há histórico de manutenção (versões, datas, correções)? | repositório, manifesto | | |
| 3 | Existe README que explica o que cada componente executa? | raiz do pacote | | |
| 4 | A descrição corresponde ao comportamento, incluindo componentes convencionais? | manifesto, documentação e pastas; enumeração completa não é obrigatória | | |
| 5 | As instruções das skills pedem algo além da tarefa (ignorar regras, enviar, ocultar do usuário)? | `skills/*/SKILL.md` | | |
| 6 | Há hooks? Que comando cada um executa e quando dispara? | pasta de hooks | | |
| 7 | Algum comando baixa e executa arquivo de fora, ou envia conteúdo para fora? | hooks, scripts | | |
| 8 | Há servidor MCP? É local ou remoto? Para onde vai o dado? | `.mcp.json` | | |
| 9 | Há credencial, token ou chave escrita nos arquivos? | todos os arquivos | | |
| 10 | Pede acesso além da pasta do exercício (pasta pessoal, chaves)? | skills, permissões | | |
| 11 | Há arquivo executável sem código-fonte? | scripts | | |
| 12 | Existe portão humano antes de qualquer ato externo (envio, publicação)? | skills, README | | |

**Decisão (instalar / não instalar / só em ambiente isolado, com dado sintético):** ______

**Quem aprovou e quando:** ______

Critérios revistos em 12/10/2026. Não confundir ausência de enumeração com comportamento ocultado.
