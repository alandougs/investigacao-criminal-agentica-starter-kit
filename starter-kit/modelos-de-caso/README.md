# Modelo de pasta de caso

Copie esta pasta para cada caso. Preserve `originais/` como somente leitura;
faça análises em `trabalho/` e coloque entregáveis em `produtos/`.

Copie os dados sintéticos para `originais/` e depois para `trabalho/`.
Só então gere o manifesto. Os comandos abaixo são executados na raiz do
repositório ou do Starter Kit, apontando para a **cópia do caso**, não o modelo:

```text
python scripts/gerar_manifesto_caso.py gerar --raiz "CAMINHO/DO/SEU/CASO" --escopo originais
python scripts/gerar_manifesto_caso.py verificar --raiz "CAMINHO/DO/SEU/CASO"
```

O manifesto registra hashes, não substitui cadeia de custódia, autorização ou
revisão humana. Não inclua dado real neste modelo.

`--escopo originais` preserva a referência dos originais, permitindo editar
trabalho e produtos. Sem essa opção, o inventário abrange toda a pasta.
O verificador detecta alterações, ausências e inclusões no escopo registrado.
Guarde uma cópia do manifesto fora do caso antes de trabalhar. Confira contra
essa referência; não gere novamente para esconder uma divergência. Substituição
intencional exige `--substituir` e preservação prévia do registro anterior.
O script não trava arquivos: aplique a marca de somente leitura do Cap. 4
depois de fazer as cópias. Quem pode remover a trava ainda pode alterá-los.
Manifesto vazio de modelo não verifica originais que você acrescentar depois.
