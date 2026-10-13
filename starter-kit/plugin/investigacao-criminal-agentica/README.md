# Plugin mínimo — Investigação Criminal Agêntica

Versão 0.1.0, documentação conferida em 04/10/2026. Este plugin contém oito
procedimentos (skills), um para cada etapa: receber, planejar, coletar insumos
locais, tratar, analisar, validar, produzir e arquivar. Usa as ferramentas de
leitura e cálculo já disponíveis no agente e somente dados sintéticos do livro.

Os portões humanos estão nas instruções. Esta versão não inclui travas técnicas,
hooks, servidor MCP, conexão remota nem envio de dados. A operação de um modelo
em nuvem segue as condições do cliente; plugin local não significa modelo local.

## Preparar a pasta

Use os dados do pacote dos capítulos 1–4. O pacote deste plugin é complementar:
extraia-o inteiro para uma pasta nova, preservando arquivos ocultos. Ele contém
um catálogo local e `plugin/investigacao-criminal-agentica/`. Mantenha essa
estrutura. Abra o agente na pasta dos exercícios, jamais na pasta pessoal inteira.

O pacote registra SHA-256 dos arquivos efetivamente copiados em
`manifesto-sha256.json`. Confira com o verificador da primeira entrega, apontando
`--raiz` para a pasta extraída deste complemento, antes de instalar.

## Adicionar o marketplace local no Codex

No terminal, estando na pasta extraída que contém `.agents/` e `plugin/`:

```text
codex plugin marketplace add .
codex plugin marketplace list
```

A documentação oficial consultada em 04/10/2026 confirma o cadastro e a
listagem de marketplaces locais. A instalação/ativação do plugin pode depender
da superfície e da versão do cliente; em ChatGPT/Codex com diretório de Plugins,
selecione o marketplace cadastrado e instale a partir da interface disponível.

Conferência de 12/10/2026: a documentação oficial descreve cadastro e listagem
CLI de marketplace e instalação/teste do plugin local no aplicativo desktop.
Instalação direta por CLI não foi confirmada nos ensaios deste livro.
O carregamento no Claude Code 2.1.287 foi testado com `--plugin-dir`; isso não
certifica instalação ou execução no Codex.

Neste projeto apenas preparamos os arquivos. Não alteramos configuração pessoal
do leitor. O catálogo de repositório pode aparecer em superfícies compatíveis;
confirme sempre na documentação da versão em uso.

## Carregar no Claude Code

Para testar sem cadastro permanente, use um caminho absoluto para o plugin:

```text
claude --plugin-dir "CAMINHO/DA/PASTA/plugin/investigacao-criminal-agentica"
```

Execute no diretório do seu exercício. Para instalar pelo catálogo local, siga
o guia da ferramenta; o arquivo `.claude-plugin/marketplace.json` fornecido tem
o mesmo plugin. O manifesto foi validado com `claude plugin validate`.

## Missão curta do capítulo 7

Em uma sessão nova, peça:

```text
Use a skill receber-documentos do plugin Investigação Criminal Agêntica.
Inventarie apenas boletim-ocorrencia.md e extrato-bancario-vitima.csv de
laboratorios/caso-ancora/dados/. Não altere nada. Informe limitações de leitura.
```

Confira se os dois arquivos foram identificados. Depois peça `produzir-nota`
para o BO: ela deve entregar identificação, fatos relatados, valores/datas,
lacunas e até três sugestões, citando linhas e aguardando revisão humana.
Recalcule os hashes dos originais após a sessão. Uma invocação que não encontrar
a skill deve informar a limitação, nunca fingir que carregou o plugin.

**Alternativa manual:** abra `skills/produzir-nota/SKILL.md` e
`references/regras.md`, anexe ambos e o BO ao chat, e peça a execução da nota.
Isso executa as instruções, mas não comprova instalação ou descoberta automática.

## Documentação oficial e limites da verificação

- [OpenAI: empacotar plugin](https://developers.openai.com/plugins/build/plugins)
  fundamenta manifesto portátil, overlay Codex e catálogo local.
- [OpenAI: construir skills](https://developers.openai.com/plugins/build/skills)
  fundamenta procedimentos empacotados sem servidor novo.
- [Claude Code: plugins](https://code.claude.com/docs/en/plugins) e
  [referência](https://code.claude.com/docs/en/plugins-reference) fundamentam
  manifesto Claude, descoberta de `skills/` e carregamento de desenvolvimento.
- [Claude Code: catálogos](https://code.claude.com/docs/en/plugin-marketplaces)
  fundamenta o catálogo com caminho relativo.

Os arquivos de estrutura, caminhos e oito skills foram verificados. Isso não
comprova a qualidade de respostas de todos os modelos, instalação em dois
clientes, nem aplicação automática das restrições. Conferência de comportamento
em sessão nova continua parte do exercício e da revisão do integrador.
As linhas para incorporação na matriz do livro estão em `fontes-para-integrador.csv`.
