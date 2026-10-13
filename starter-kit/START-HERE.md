# Comece aqui — kit integral

Este material é inteiramente fictício e sintético. Use apenas estes dados nos
exercícios. Você não precisa programar. Um hash é uma impressão digital calculada
do arquivo: se os bytes mudarem, o valor calculado também muda.

## Abrir o material

Repositório público: <https://github.com/alandougs/investigacao-criminal-agentica-starter-kit>. No GitHub, escolha **Code → Download ZIP**, extraia tudo e abra a pasta `starter-kit/`. Se usar `git clone`, abra essa mesma subpasta: o manifesto não inclui o diretório Git que fica acima dela.

1. Extraia o ZIP inteiro para uma pasta nova. Não trabalhe dentro do ZIP.
2. No VS Code, escolha **Arquivo → Abrir Pasta** e selecione a pasta que contém
   este `START-HERE.md`. Abra o terminal pelo menu **Terminal → Novo Terminal**.
3. Para os passos com scripts, confira `python --version`: use Python 3.12 ou
   superior. No macOS/Linux, se o comando for `python3`, substitua `python` em
   todos os comandos. O verificador usa só a biblioteca padrão; os laboratórios posteriores têm seus pré-requisitos nos capítulos. Se Python não estiver disponível, faça os passos manuais do Cap. 4.
4. Confira o pacote: `python scripts/gerar_manifesto_caso.py verificar --raiz .`.
   A resposta esperada é "Manifesto verificado sem divergências". Faça isso antes
   de criar seus arquivos. O manifesto da raiz registra o pacote como recebido;
   ele apontará inclusões se você passar a trabalhar dentro dessa mesma pasta.
5. Para usar um agente, siga o guia da sua ferramenta fornecido com o livro.
   Abra o agente somente nesta pasta. Peça: "Leia AGENTS.md e resuma as regras,
   citando linhas. Não altere arquivos". Confira o resumo contra o arquivo.
   Em chat sem acesso à pasta, anexe explicitamente instruções e documentos.

## Exercícios em ordem

- **Cap. 1:** leia `laboratorios/caso-ancora/labs/cap-01-registro-sessao.md` e
  marque P, A, O, V e H. Depois, peça ao agente para comparar
  `laboratorios/caso-ancora/dados/boletim-ocorrencia.md` e
  `laboratorios/caso-ancora/dados/extrato-bancario-vitima.csv`, citando linhas e
  separando relato de documento. Confira datas, valores e lacunas nas fontes.
- **Cap. 2:** diagnostique `laboratorios/caso-ancora/labs/cap-02-prompt-original.md`.
  Reescreva com os sete blocos PTCFREE e salve sua versão em uma cópia de
  `instrucoes/nota-de-triagem.md`. Em conversa nova, anexe essa instrução e o BO;
  peça a nota seguindo o arquivo. Compare com a resposta ao pedido original.
- **Cap. 3:** no terminal da pasta extraída, execute os comandos abaixo. Eles
  registram sua própria cópia local; não enviam material para a internet.
- **Cap. 4:** classifique as seis situações de
  `laboratorios/caso-ancora/labs/cap-04-classificar-dados.md`. Depois copie
  `modelos-de-caso/` para uma pasta nova fora do pacote, por exemplo
  `../caso-marta-helena/`. Ela já contém os dois dados em `originais/` e em
  `trabalho/`, além das regras do caso. Não gere novamente a referência recebida.

```text
git init
git config user.name "Seu Nome"
git config user.email "Seu endereço de commit"
git add .
git commit -m "lab: versão inicial do material do livro"
```

As duas configurações valem apenas para esta pasta. Use o endereço de commit
privado do GitHub se desejar; não use uma credencial no campo de e-mail.
Crie `pratica/notas-cap03.md` pelo editor com nome, data e "bancada montada";
registre com `git add pratica/notas-cap03.md` e
`git commit -m "lab: notas do capítulo 3"`. Apague a linha da data, salve e veja
`git diff`. Execute `git restore pratica/notas-cap03.md` e confirme que voltou.

## Conferir a pasta do caso

Ainda no terminal da pasta do pacote, execute:

```text
python scripts/gerar_manifesto_caso.py verificar --raiz "../caso-marta-helena"
```

Se escolheu outro destino, substitua apenas o caminho entre aspas. Guarde uma
cópia de `manifesto-sha256.json` fora da pasta do caso. Ele registra apenas
`originais/`, portanto permite editar `trabalho/` e `produtos/`. Para criar um
caso seu com outros dados sintéticos, siga `modelos-de-caso/README.md` e gere
seu próprio manifesto depois de copiar os originais, preservando a referência.

Copie e confira antes de travar. No terminal do pacote, no Windows:

```powershell
Get-ChildItem ../caso-marta-helena/originais/* | ForEach-Object { $_.IsReadOnly = $true }
```

No macOS/Linux:

```bash
chmod a-w ../caso-marta-helena/originais/*
```

Anote somente em `trabalho/` e volte a conferir o manifesto. Os hashes devem
continuar iguais. A marca de somente leitura pode ser removida por quem tem
permissão: não é uma garantia de custódia. Teste escrita em cópia descartável,
para não arriscar os originais. Não regenere o manifesto para ocultar divergência.

## Se algo não funcionar

"Arquivo não encontrado": confira que extraiu tudo e que o terminal está na
pasta deste arquivo (`pwd`). "Manifesto já existe": use verificar, não gerar.
"Hash divergente", "ausente" ou "não registrado": pare e compare com a cópia
preservada; não apague o aviso regenerando o registro.

Este kit integral contém os insumos e ferramentas públicos dos laboratórios; não contém gabaritos.
Anote suas respostas; os materiais reservados de conferência ficam fora do kit.
Instalação e permissões específicas do agente continuam no guia do livro.


## Templates e prompts práticos

A pasta templates/ contém modelos de relatório investigativo, ofício, matriz de evidências e selo de transparência sobre uso de IA. A pasta prompts/ contém exemplos PTCFREE para relatório, cronologia e planejamento OSINT.

Fluxo recomendado:

1. copie o template para a pasta de trabalho do caso;
2. preencha a missão e o contexto;
3. escolha/adapte o prompt PTCFREE;
4. faça o agente trabalhar somente sobre as fontes autorizadas;
5. confira cada afirmação contra a fonte;
6. registre no selo de transparência como a IA foi usada.

Esses materiais são modelos didáticos. Não substituem normas, modelos institucionais, autorização, revisão jurídica ou decisão humana.

## Continuar após os capítulos 1–4

Siga os laboratórios na ordem do livro. Use laboratorios/caso-ancora/dados/ e laboratorios/caso-ancora/labs/ para copiar apenas os insumos da missão. Os dados futuros não devem antecipar a análise de uma etapa. Consulte guias/por-ferramenta.md para instalar e conferir seu cliente; o padrão de skills local está em .agents/skills/ e o plugin em plugin/. Confira no cliente o que foi carregado, sem presumir compatibilidade. workflows/ contém a ferramenta de triagem existente e a remissão ao fluxo coordenado. Os gabaritos e arquivos internos de revisão ficam fora da distribuição.
