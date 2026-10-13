# Requisitos — Analisador de extrato telefônico (ERB), versão 1.2 — revisão 12/10/2026

> Documento de requisitos do laboratório do Cap. 18. Entregue-o ao agente e peça **primeiro o plano**, sem código. Dados 100% sintéticos (P10). Modo B: a ferramenta roda localmente e não usa modelo de linguagem. A implementação fornecida 1.1.1 exige Python 3.12 ou superior para cumprir também a conferência de junções NTFS. Verifique a versão e teste a recusa no Windows; não presuma esse controle em versões anteriores.

## 1. Objetivo
Ler um extrato telefônico em CSV e gerar um relatório em Markdown com: (a) eventos por ERB, (b) linha do tempo, (c) contatos por frequência, (d) primeiro e último evento por linha. O relatório deve ser idêntico para os mesmos bytes, versão, configuração e ambiente relevantes; início e fim de execução ficam apenas no log.

## 2. Entrada
Arquivo CSV, UTF-8, com cabeçalho, no formato de `dados/extrato-telefonico-erb.csv`.

**Colunas obrigatórias:** `data_hora`, `tipo_evento`, `linha_origem`, `linha_destino`, `identificador_dispositivo_sintetico`, `erb_id`, `erb_nome`, `municipio_ficticio`, `latitude_aproximada`, `longitude_aproximada`, `duracao_segundos`.
**Coluna opcional:** `observacao`. É texto livre do arquivo: **não entra em nenhuma análise**. Se existir, o relatório avisa que ela foi ignorada.

## 3. Validações
- **R1.** Se faltar coluna obrigatória: encerrar com mensagem que nomeia a(s) coluna(s) e código de saída 2. Não gerar relatório.
- **R2.** `data_hora` no formato `AAAA-MM-DD hh:mm:ss`. Linha com formato diferente **não é descartada em silêncio**: vai para a seção "Linhas não processadas", com o número da linha e o valor.
- **R3.** Arquivo vazio (só cabeçalho): relatório com 0 eventos e aviso. Arquivo ausente: mensagem clara e código de saída 1.

## 4. Normalização de telefone
- **R4.** O mesmo número escrito de formas diferentes (`+55-14-90000-0042`, `+55 14 90000 0042`, `(14) 90000-0042`) conta como **uma** linha. A forma normalizada é `+55` seguido só de dígitos. O relatório mostra a forma normalizada e, na linha do tempo, o texto original.

## 5. Saídas do relatório (Markdown)
- **R5. Cabeçalho:** nome e **versão** da ferramenta; **SHA-256 do arquivo de entrada**; número de linhas lidas, processadas e não processadas. **Não** inclui data e hora da execução (para o relatório ser idêntico a cada rodada); data e hora vão para o log.
- **R6. Eventos por ERB:** para cada `erb_id` (com `erb_nome`): quantidade de eventos, primeiro e último evento. Ordenar por `erb_id`.
- **R7. Linha do tempo:** todos os eventos ordenados por `data_hora`; empate mantém a ordem do arquivo. Colunas: data e hora, tipo, linha de origem (normalizada), contraparte (normalizada ou vazio), `erb_id`.
- **R8. Contatos por frequência:** para cada contraparte (`linha_destino` não vazia): quantidade de eventos, primeiro e último. Ordenar por quantidade decrescente e, em empate, pelo número normalizado crescente.
- **R9. Primeiro e último evento por linha de origem:** com tipo e `erb_id`. Ordenar pelo número normalizado.
- **R10. Avisos obrigatórios** no fim do relatório, com este texto: "A ERB indica a antena que atendeu o evento, não a posição exata do aparelho." · "O fuso horário é o do arquivo; confirme com a operadora." · "O titular de uma linha não é, por isso, quem a usava."

## 6. Log
- **R11.** Gravar `log.txt` na pasta de saída, com data e hora de início e de fim, nome e versão da ferramenta, SHA-256 da entrada, linhas lidas, processadas e não processadas.

## 7. Restrições
- **R12.** Sem acesso à rede; só a biblioteca padrão da linguagem; não usar modelo de linguagem.
- **R13.** Não alterar o arquivo de entrada; escrever só na pasta de saída informada; **recusar** gravar sobre relatório existente (sem opção de sobrescrever).
- **R14.** A ferramenta **não conclui** localização, identidade nem conduta: só descreve o que o arquivo contém.

## 8. Testes com resposta conhecida
Crie estes testes **antes** de usar a ferramenta em qualquer outro arquivo.

**Amostra `amostra-teste.csv`** (5 linhas, dados inventados; uma fora de ordem e um telefone em formato diferente):

```text
data_hora,tipo_evento,linha_origem,linha_destino,identificador_dispositivo_sintetico,erb_id,erb_nome,municipio_ficticio,latitude_aproximada,longitude_aproximada,duracao_segundos
2026-01-10 08:00:00,DADOS,+55-14-90000-0042,+55-14-90000-0001,IMEI-SINTETICO-9001,ERB-T-01,Torre A,Cidade Teste,-22.0000,-47.0000,
2026-01-10 08:05:00,DADOS,+55 14 90000 0042,+55-14-90000-0001,IMEI-SINTETICO-9001,ERB-T-01,Torre A,Cidade Teste,-22.0000,-47.0000,
2026-01-10 09:30:00,VOZ,+55-14-90000-0042,+55-14-90000-0002,IMEI-SINTETICO-9001,ERB-T-02,Torre B,Cidade Teste,-22.0100,-47.0100,60
2026-01-10 07:50:00,DADOS,+55-14-90000-0001,,IMEI-SINTETICO-9002,ERB-T-02,Torre B,Cidade Teste,-22.0100,-47.0100,
2026-01-11 10:00:00,VOZ,+55-14-90000-0042,+55-14-90000-0002,IMEI-SINTETICO-9001,ERB-T-03,Torre C,Cidade Teste,-22.0200,-47.0200,120
```

**Resultado esperado para a amostra:**

| Item | Esperado |
|---|---|
| Linhas lidas / processadas / não processadas | 5 / 5 / 0 |
| Eventos por ERB | `ERB-T-01`: 2 (08:00:00 a 08:05:00) · `ERB-T-02`: 2 (07:50:00 a 09:30:00) · `ERB-T-03`: 1 (11/01 10:00:00) |
| Linha do tempo (ordem) | 07:50 (`…0001`, `ERB-T-02`) → 08:00 → 08:05 → 09:30 → 11/01 10:00 (as quatro últimas da linha `…0042`) |
| Contatos por frequência | `+5514900000001`: 2 (08:00 a 08:05) · `+5514900000002`: 2 (09:30 a 11/01 10:00); empate resolvido pelo número crescente |
| Primeiro e último por linha | `+5514900000001`: 1 evento (07:50, `DADOS`, `ERB-T-02`) · `+5514900000042`: 4 eventos, primeiro 08:00 (`DADOS`, `ERB-T-01`), último 11/01 10:00 (`VOZ`, `ERB-T-03`) |
| Telefones | `+55 14 90000 0042` e `+55-14-90000-0042` contados como **uma** linha |

**Outros testes obrigatórios:** (1) coluna obrigatória ausente → código 2 e mensagem com o nome da coluna; (2) uma `data_hora` inválida → a linha aparece em "Linhas não processadas"; (3) arquivo só com cabeçalho → relatório com 0 eventos; (4) **a mesma entrada duas vezes → relatórios idênticos, byte a byte**; (5) tentativa de gravar sobre relatório existente → recusa.

## 9. Separação do modo B e verificações de proteção

Desenvolvimento recebe só este documento e a amostra sintética. Dado real e derivados ficam fora do alcance efetivo do modelo, inclusive logs/erros. Execução posterior usa a ferramenta conferida, sem cliente de IA e com rede impedida e conferida no ambiente autorizado. Não devolver resultado ao modelo.

Além das contraprovas acima, conferir largura de cada linha, origem/destino iguais, relatório/log existentes e caminhos por link, junção, alias ou travessia. Nas recusas, os hashes de entrada e arquivos existentes permanecem iguais. Esses testes preservam o contrato reforçado da referência 1.1.1; não certificam isolamento do ambiente por si.
