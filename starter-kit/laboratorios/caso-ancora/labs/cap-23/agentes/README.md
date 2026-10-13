# Cap. 23 — Instruções dos papéis do sistema multiagente

Oito instruções permanentes no formato PTCFREE (Cap. 2), uma por papel, escritas para o laboratório do Cap. 23. São texto: valem em qualquer agente que aceite instruções de papel ou de subagente. Como declarar cada papel no seu agente (formato, pasta, restrição de ferramentas) está no Apêndice A.

| Arquivo | Papel | Lê | Escreve |
|---|---|---|---|
| `01-coordenador.md` | planeja | inventário | `trabalho/plano.md` |
| `02-osint.md` | fontes abertas | perfil e capturas | `trabalho/achados-osint.md` |
| `03-documental.md` | documental | termos, operadora, extração, mídias | `trabalho/achados-documental.md` |
| `04-financeiro.md` | financeiro | extratos, bancos, `fluxo.py` | `trabalho/achados-financeiro.md` |
| `05-analista.md` | cruza | achados aprovados | `trabalho/vinculos.csv`, `matriz-hipoteses.md` |
| `06-defensor.md` | defensor | vínculos e matriz | `trabalho/relatorio-defensor.md` |
| `07-redator.md` | redige | achados e matriz aprovados | `produtos/relatorio-final-rascunho.md` |
| `08-auditor.md` | audita | rascunho e fontes | `trabalho/parecer-auditor.md` |

Os três **portões humanos** ficam entre o plano e os especialistas, entre os achados e o analista/redator, e entre o rascunho e a assinatura. Esses textos não configuram permissões de caminho, acesso à rede, leitores de aprovação nem continuidade de estado. O investigador deve efetivar controles no ambiente ou conduzir manualmente as etapas.

Dados 100% sintéticos (P10). Gabarito: o material reservado de conferência (fora deste pacote), fora do Starter Kit.

## Execução manual dos portões (referência deste laboratório)

Use sessões separadas para cada papel. Abra apenas os arquivos necessários ao papel em uma cópia de trabalho sintética. Desative ferramentas de envio, rede e escrita em originais pelas configurações de permissão realmente disponíveis no ambiente. Se o ambiente não puder impor uma restrição, registre a limitação e mantenha essa ação sob execução exclusiva do investigador.

1. Coordenador entrega plano e encerra a sessão. O investigador registra aprovação com data e ajustes; só então inicia especialistas.
2. Especialistas entregam achados e encerram. O investigador confere fontes, registra aprovação/recusa e só encaminha achados aprovados ao analista, defensor e redator, em novas sessões.
3. O auditor recebe rascunho e fontes em sessão distinta da redação e não reescreve. O investigador confere parecer e peça integralmente, documenta decisão, remove canário e preenche selo somente após essa conferência.
4. Antes de suspender, preserve arquivos e registre no plano a etapa, produtos, hashes, aprovações e próxima ação. Retomada lê o registro antes de iniciar outra etapa. Mensagem "aprovado" emitida pelo agente não substitui decisão registrada do investigador.
5. Teste de interrupção/envio só conta quando executado no ambiente escolhido e registrado; o pacote de instruções não prova o bloqueio. Sem ferramenta de envio habilitada, registre sua indisponibilidade; isso não testa o bloqueio de uma ferramenta habilitada. Preserve o estado. Não envie nada para testar.

As dez unidades de avaliação estão no bloco JSON do gabarito MD já existente. O avaliador do Cap. 22 lê esse bloco diretamente; a extração para arquivo novo é opcional. O avaliador humano converte a peça, registra equivalências e confirma cada componente e fonte; o agente gerador não recebe o gabarito para copiar respostas.

## Contrato de entrega manual —12/10/2026

Cada resposta é texto; o operador preserva o bruto e grava em caminho novo. Na receita principal, ferramentas de leitura/escrita/envio ficam indisponíveis; só o operador fornece insumos e inicia a etapa após conferir. O registro de aprovação não é leitor automático de estado. Produtos parciais só existem se foram efetivamente salvos. Sem ferramenta habilitada, a recusa do pedido de envio não prova bloqueio de operação habilitada. Todos os juízos do auditor e graus são propostas rotuladas. Para a autoconferência pública, use os dez critérios e o contrato do capítulo; o gabarito MD é controle interno, excluído do Kit.
