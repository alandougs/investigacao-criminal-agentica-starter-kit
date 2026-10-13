
# Apêndice A — Guias por ferramenta

> **Nota de método.** Esta é a consulta volátil do livro. As fontes oficiais abaixo foram consultadas em **12/10/2026**. Conferência documental demonstra o que o fabricante descreve; ensaio registra uma execução em determinada versão. Nenhum dos dois promete suporte universal. O caminho de uma skill pode ser portável e sua ativação ainda depender do cliente, da configuração e da superfície usada.

## Como usar este apêndice

Baixe os arquivos do [repositório público do Starter Kit](https://github.com/alandougs/investigacao-criminal-agentica-starter-kit). Abra `starter-kit/START-HERE.md` e trabalhe somente com os insumos sintéticos da missão. O guia não promete descoberta automática de skills em qualquer cliente.

1. Identifique cliente, versão, sistema e forma de acesso: CLI, extensão ou aplicação.
2. Abra a fonte indicada antes de instalar. Use a autenticação do fornecedor; nunca cole credenciais no projeto ou na conversa.
3. Confira a descoberta e a leitura das instruções no cliente. Regras em Markdown orientam o modelo; permissões e controles do ambiente precisam ser configurados e testados separadamente.
4. Execute primeiro com material sintético. Registre pedido, resposta, ferramentas disponíveis, falhas e limites. Se usar texto fornecido como contexto, registre essa modalidade.

## A bancada comum (Cap. 3)

| Peça | Uso no livro | Fonte oficial consultada em 12/10/2026 |
|---|---|---|
| VS Code | Editor e terminal integrado; confirme a pasta atual antes de executar comandos | <https://code.visualstudio.com/docs/terminal/basics> |
| Git | Versões registradas; `git restore` documentado desde 2.23.0 | <https://git-scm.com/docs/git-restore/2.23.0> |
| GitHub | Hospedagem com controle de acesso; privado não significa autorização para sigilo policial | <https://docs.github.com/en/repositories/creating-and-managing-repositories/about-repositories> |
| Python | Scripts de laboratório; o verificador do livro exige Python 3.12 ou posterior | <https://docs.python.org/3.12/library/pathlib.html> |
| PowerShell | Terminal do Windows. Confira a versão; passagem de argumentos a executáveis difere entre versões | <https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_parsing?view=powershell-5.1> |

### Fim de linha e hash

LF e CRLF são bytes diferentes e produzem hashes diferentes. O livro fixa LF por `.gitattributes`; confira a política de conversão antes de comparar um arquivo clonado com o manifesto. Não normalize originais para fazê-los coincidir. Fonte: <https://git-scm.com/docs/gitattributes>.

| Sistema | SHA-256 | Conferência |
|---|---|---|
| Windows / PowerShell | `Get-FileHash -LiteralPath arquivo -Algorithm SHA256` | compare com o valor registrado; esse comando não verifica sozinho toda a lista |
| Linux com GNU Coreutils | `sha256sum arquivo` | `sha256sum -c lista.txt` |
| Sistema com `shasum`, incluindo instalações usuais de macOS | `shasum -a 256 arquivo` | `shasum -a 256 -c lista.txt` |

Disponibilidade do comando depende da instalação. Documentação: Microsoft `Get-FileHash`, GNU Coreutils `sha256sum` e Perl `shasum`, nas referências. Não basta obter um hash para provar origem, legalidade ou histórico de custódia (Cap. 21).

### Argumento vazio no Windows

O Cap. 6 tem receitas distintas de terminal. Em PowerShell 5.1, `--tools ""` pode perder o argumento vazio ao chamar um executável. A receita ensaiada usa `--tools '""'`: aspas simples envolvendo duas aspas duplas. Em shell POSIX usa-se `--tools ""`. Em PowerShell 7, confira versão e modo de passagem; não transplante a receita sem testar. Desativar ferramentas nativas dessa sessão não constitui confinamento de todos os componentes do computador.

## Padrões abertos e suporte concreto

| Padrão | O que padroniza | Fonte |
|---|---|---|
| AGENTS.md | Instruções de projeto | <https://agents.md/> |
| Agent Skills | Pasta com `SKILL.md`, metadados e instruções; descoberta e carregamento dependem do cliente | <https://agentskills.io/specification> |
| MCP | Comunicação entre aplicação e servidor, incluindo tools, resources e prompts | <https://modelcontextprotocol.io/specification/2025-11-25> |

As listas de clientes nessas páginas indicam participação ou compatibilidade declarada; não demonstram que toda aplicação carrega o mesmo arquivo por padrão. O Cap. 25 separa integridade da cópia, descoberta, ativação e qualidade da execução.

## Fichas por agente

### Claude Code (Anthropic)

| Peça | Rota documentada em 12/10/2026 |
|---|---|
| Instrução | `CLAUDE.md`; importação explícita `@AGENTS.md` quando aplicável. Leitura direta de `AGENTS.md` exige versão 2.1.277 ou posterior e depende de arquivos concorrentes, configuração e suporte da sessão. Confira `/memory` e a documentação de memória |
| Skill | `.claude/skills/<nome>/SKILL.md`; confira descoberta e ativação |
| Subagente | `.claude/agents/<nome>.md`, com contexto separado e ferramentas configuráveis; nomes de ferramentas não impõem todos os limites de caminho |
| Hook | Configurações do cliente; o exemplo do Cap. 8 trata `Edit`/`Write`, inclui falha fechada e depende de versão compatível. Terminal exige controle separado |
| Plugin | Manifesto `.claude-plugin/plugin.json`; desenvolvimento com `--plugin-dir`, conforme documentação |
| MCP | Servidor e permissões configurados no cliente; receita de leitura restrita do Cap. 6 |

Fontes: <https://code.claude.com/docs/en/memory>, <https://code.claude.com/docs/en/skills>, <https://code.claude.com/docs/en/sub-agents>, <https://code.claude.com/docs/en/hooks>, <https://code.claude.com/docs/en/plugins>, <https://code.claude.com/docs/en/permissions>.

### Codex (OpenAI)

| Peça | Rota documentada em 12/10/2026 |
|---|---|
| Instrução | `AGENTS.md`; há precedência, arquivos de substituição e limites de leitura. Confira quais instruções foram incorporadas |
| Skill | `.agents/skills/<nome>/SKILL.md`; o cliente procura nos diretórios aplicáveis. A configuração pode desabilitar uma skill; mudanças podem exigir reinício |
| Plugin do kit | Variante `.codex-plugin/plugin.json`; use a rota documentada no README do pacote para a superfície escolhida. Manifesto presente não comprova instalação |
| Controles | Sandbox e aprovações são distintos das instruções. Uma leitura pode ser rejeitada por revisão automática mesmo com skill descoberta |
| Demais peças | Confira a documentação específica da superfície; o livro não ensaiou todas as combinações |

Fontes: <https://learn.chatgpt.com/docs/agent-configuration/agents-md>, <https://learn.chatgpt.com/docs/build-skills>, <https://learn.chatgpt.com/docs/agent-approvals-security>.

### OpenCode

| Peça | Rota documentada em 12/10/2026 |
|---|---|
| Instrução | `AGENTS.md` de projeto; `CLAUDE.md` pode ser fallback, conforme configuração |
| Skill | Rota própria `.opencode/skills/<nome>/SKILL.md`; a documentação também descreve rotas compatíveis `.agents/skills/` e `.claude/skills/`. Confira permissões e descoberta |
| Demais peças | Consulte os guias oficiais; não há ensaio deste cliente registrado nesta etapa |

Fontes: <https://opencode.ai/docs/rules/> e <https://opencode.ai/docs/skills/>.

### Gemini CLI (Google)

A instrução padrão documentada usa `GEMINI.md`. Para outro nome, como `AGENTS.md`, a documentação descreve `context.fileName`. Compatibilidade declarada não torna AGENTS.md o padrão de todas as sessões. Skills e demais recursos devem ser conferidos na superfície escolhida antes do laboratório. Fonte: <https://geminicli.com/docs/cli/gemini-md/>. Sem ensaio deste cliente nesta etapa.

### GitHub Copilot, VS Code e outros clientes

Consulte <https://docs.github.com/copilot> e <https://code.visualstudio.com/docs>. Listas dos padrões não substituem instruções específicas do editor, agente ou integração. O livro não certifica a execução dessas superfícies. Antes de usá-las, confirme arquivo de instrução, pasta de skills, ferramentas expostas e controles efetivos. Quando não conseguir restringir uma ação, mantenha-a sob execução exclusiva do operador.

## Quando o agente não tem o recurso

| Recurso ausente | Rota de adaptação e limite |
|---|---|
| Leitura de AGENTS.md | Forneça o texto explicitamente e registre seu hash; não alegue leitura automática |
| Skills | Use o procedimento como contexto; não alegue instalação ou ativação nativa |
| Subagente | Sessão distinta com os insumos selecionados, sem contexto do redator; operador decide a transição |
| Hook | Permissão efetiva do sistema de arquivos e conferência de integridade; hash detecta diferenças, não impede escrita |
| Plugin | Forneça as instruções necessárias separadamente e teste; copiar arquivos não reproduz todos os recursos |
| MCP | Operador seleciona e fornece cópias sintéticas. A pasta organiza os insumos; para restringir leitura pelo disco são necessários controles efetivos de ferramentas e ambiente |

## Registro de execução e verificação

Em **12/10/2026**, o kit provisório foi ensaiado pelo coordenador com BO e extrato sintéticos em Claude Code **2.1.296** e Codex CLI **0.162.0-alpha.17.2**. No Claude, o trace registrou ativação da skill e leitura dos dois arquivos. No Codex, a descoberta ocorreu, mas a leitura nativa foi rejeitada pela revisão automática. Uma segunda rota, com os textos explicitamente fornecidos e sem leitura por ferramenta, gerou nota delimitada. Essa rota demonstra uso de contexto; não aprova a leitura nativa rejeitada nem certifica o kit inteiro.

Confira versão, modalidade, entradas e limites no seu ensaio. Não tente vencer uma rejeição mudando controles sem autorização. A documentação pode descrever um recurso que o ambiente da sessão não permite executar. O livro distingue essa situação de uma falha na análise do conteúdo.

## Referências

Fontes consultadas em **12 out. 2026**: páginas oficiais vinculadas nas fichas e tabelas; para hashes, <https://learn.microsoft.com/powershell/module/microsoft.powershell.utility/get-filehash?view=powershell-5.1>, <https://www.gnu.org/software/coreutils/manual/html_node/sha2-utilities.html> e <https://perldoc.perl.org/shasum>. A indisponibilidade temporária de uma página é registrada na matriz; não equivale a retirada do comando. Os ensaios de produção ficam no controle de qualidade do projeto; não são promessa de suporte futuro.
