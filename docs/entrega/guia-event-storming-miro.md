# Guia — montar o Event Storming no Miro

> Fonte: `docs/ddd/modelagem-ddd.md` (já tem todos os cartões e a ordem).
> O enunciado exige que a documentação **corresponda ao código** — use os mesmos
> nomes que estão no projeto. No fim, exporte para `docs/ddd/`.

## Passo a passo

1. Crie um board no Miro (ou FigJam). Deixe o link **público / qualquer pessoa pode ver** (o avaliador não deve precisar pedir acesso).
2. Crie uma legenda de cores no canto (os tipos de cartão):
   - 🟧 laranja = Evento (verbo no passado)
   - 🟦 azul = Comando (imperativo)
   - 🟨 amarelo = Ator
   - 🟪 roxo = Política / regra
   - 🟩 verde = Read model
   - 🟥 rosa = Sistema externo
3. Monte **três faixas horizontais**, uma por fluxo (está tudo no `modelagem-ddd.md`):
   - **Fluxo 1 — Criação da OS:** Atendente → Identificar cliente → Cliente identificado → ... → Orçamento enviado.
   - **Fluxo 2 — Acompanhamento:** a máquina de status (Recebida → ... → Entregue), com a linha vertical marcando o evento pivotal "Orçamento aprovado".
   - **Fluxo 3 — Peças e insumos:** Estoquista → Cadastrar/Repor peça; política "Orçamento aprovado → baixar estoque".
4. Abaixo dos fluxos, agrupe os **agregados** (`OrdemServico`, `Cliente`, `Veiculo`, `Servico`, `Peca`) e marque os **bounded contexts** (Atendimento, Cadastros, Estoque).
5. Adicione um quadro com a **linguagem ubíqua** (copie de `docs/ddd/linguagem-ubiqua.md`).

## Exportar para o repositório

- Exporte o board em PDF (ou imagem) e salve em `docs/ddd/event-storming.pdf`.
- Se fizer diagramas extras (camadas, C4), salve em `docs/ddd/diagramas.pdf`.
- O `docs/ddd/linguagem-ubiqua.md` já está no repo.
- Suba por um PR (ex.: `feature/doc-ddd-miro`).

## Dica

Como o board precisa "bater com o código", confira que cada agregado/entidade do
Miro existe em `app/domain/` (OrdemServico, Cliente, Veiculo, Servico, Peca) e que
os objetos de valor (CpfCnpj, Placa, Dinheiro) aparecem na modelagem.
