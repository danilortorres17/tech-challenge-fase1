# Modelagem DDD - Oficina Mecânica (Event Storming)

> Este documento é o roteiro do Event Storming: cada linha é um cartão a colocar
> no board do Miro. Depois de montar o board, exporte-o para
> `docs/ddd/event-storming.pdf`. O modelo abaixo deve corresponder ao código em `app/`.

## Legenda dos cartões

| Cor | Elemento | Como escrever |
|-----|----------|---------------|
| 🟧 Laranja | Evento de domínio | verbo no **passado** ("Orçamento gerado") |
| 🟦 Azul | Comando | verbo no **imperativo** ("Gerar orçamento") |
| 🟨 Amarelo | Ator | quem dispara o comando ("Atendente") |
| 🟪 Roxo | Política / regra | automação que reage a um evento e dispara um comando |
| 🟩 Verde | Read model | dado consultado antes de um comando |
| 🟥 Rosa | Sistema externo | fora do domínio |

Gramática: **Ator → Comando → Evento**. Sem ator, **Política → Comando → Evento**.

---

## Fluxo 1 - Criação da Ordem de Serviço

| # | Ator / Gatilho | Comando (🟦) | Evento (🟧) | Observações |
|---|----------------|--------------|-------------|-------------|
| 1 | 🟨 Atendente | Identificar cliente | Cliente identificado | por CPF ou CNPJ (valida o documento) |
| 2 | 🟨 Atendente | Cadastrar veículo | Veículo cadastrado | placa, marca, modelo, ano |
| 3 | 🟨 Atendente | Abrir ordem de serviço | OS aberta | status inicial: **Recebida** |
| 4 | 🟨 Atendente | Incluir serviços | Serviços incluídos | ex.: troca de óleo, alinhamento |
| 5 | 🟨 Atendente | Incluir peças e insumos | Peças incluídas | 🟩 consulta saldo de estoque antes |
| 6 | 🟪 Política: serviços/peças definidos | Gerar orçamento | Orçamento gerado | **automático**, sem ator |
| 7 | 🟨 Atendente | Enviar orçamento ao cliente | Orçamento enviado | → status **Aguardando aprovação** |

Regras: não gerar orçamento sem ao menos 1 serviço ou peça; orçamento = soma(serviços) + soma(peças).

---

## Fluxo 2 - Acompanhamento da Ordem de Serviço (máquina de status)

```
Recebida → Em diagnóstico → Aguardando aprovação → Em execução → Finalizada → Entregue
                                   │
                                   └── (rejeitada) → Rejeitada → (reabrir) → Em diagnóstico
```

| # | Ator / Gatilho | Comando (🟦) | Evento (🟧) | Transição de status |
|---|----------------|--------------|-------------|---------------------|
| 1 | 🟨 Mecânico | Registrar diagnóstico | Diagnóstico registrado | Recebida → Em diagnóstico |
| 2 | 🟪 Política: orçamento enviado | - | - | Em diagnóstico → Aguardando aprovação |
| 3 | 🟨 Cliente | Aprovar orçamento | Orçamento aprovado | Aguardando aprovação → Em execução |
| 3b | 🟨 Cliente | Rejeitar orçamento | Orçamento rejeitado | Aguardando aprovação → **Rejeitada** |
| 3c | 🟨 Atendente | Reabrir para ajuste | OS reaberta | Rejeitada → Em diagnóstico (ajusta e reenvia) |
| 4 | 🟪 Política: orçamento aprovado | Baixar peças do estoque | Estoque baixado | em **transação única** com a aprovação (Unit of Work) |
| 5 | 🟨 Mecânico | Concluir serviços | Serviços concluídos | Em execução → Finalizada |
| 6 | 🟨 Atendente | Entregar veículo | Veículo entregue | Finalizada → Entregue |
| 7 | 🟨 Cliente | Consultar andamento | - | 🟩 read model: status da OS - **endpoint público** |

Regras: só entra em "Em execução" após orçamento aprovado; transições só na ordem acima (pular etapa = erro de domínio). Uma OS rejeitada pode ser reaberta para ajuste do orçamento e reenvio.

**Evento pivotal:** `Orçamento aprovado` marca a virada de negociação → execução. Forte indicador de fronteira de contexto.

---

## Fluxo 3 - Gestão de Peças e Insumos

| # | Ator / Gatilho | Comando (🟦) | Evento (🟧) | Observações |
|---|----------------|--------------|-------------|-------------|
| 1 | 🟨 Estoquista | Cadastrar peça | Peça cadastrada | nome, preço, saldo inicial |
| 2 | 🟨 Estoquista | Repor estoque | Estoque reposto | aumenta o saldo |
| 3 | 🟪 Política: orçamento aprovado | Baixar peças do estoque | Estoque baixado | diminui o saldo (vem do Fluxo 2) |
| 4 | 🟪 Política: saldo abaixo do mínimo | Alertar estoque baixo | Estoque baixo sinalizado | 🟩 read model: saldo x mínimo (opcional) |

Regra: não aprovar orçamento se alguma peça estiver sem saldo suficiente.

---

## Agregados, Entidades e Objetos de Valor

### Agregado `OrdemServico` (raiz) - núcleo do sistema
- **Entidades internas:** `ItemServico`, `ItemPeca`
- **Objetos de valor:** `StatusOS`, `Orcamento`
- **Responsabilidade:** só o agregado altera o próprio status e aplica as regras de transição. Quem está fora solicita via comando.

### Agregado `Cliente` (raiz)
- **Objeto de valor:** `CpfCnpj` (valida o documento)

### Agregado `Veiculo` (raiz)
- **Objeto de valor:** `Placa` (valida o formato)

### Agregado `Peca` (raiz)
- Controla o próprio **saldo de estoque** (reposição e baixa)

### Agregado `Servico` (raiz)
- Catálogo de serviços com preço de mão de obra

### Objetos de valor transversais
- `Dinheiro` (valor + moeda; evita float solto para preços)

---

## Bounded Contexts (identificados)

| Contexto | Tipo | O que contém |
|----------|------|--------------|
| **Atendimento** | Principal (core) | OrdemServico, Orçamento, máquina de status |
| **Cadastros / Catálogo** | Suporte | Cliente, Veículo, Serviço |
| **Estoque** | Suporte | Peça, saldo, reposição e baixa |

Conexão entre contextos: a política `Orçamento aprovado` (Atendimento) dispara a baixa no **Estoque**. No MVP tudo vive no mesmo monolito, mas a separação lógica em módulos espelha esses contextos.

---

## Regras de negócio consolidadas (políticas)

1. Orçamento = soma dos serviços + soma das peças.
2. Não gerar orçamento sem ao menos um serviço ou peça.
3. Transições de status só na ordem definida - pular etapa lança exceção de domínio.
4. OS só vai para "Em execução" depois do orçamento aprovado.
5. Rejeição leva a OS ao status **Rejeitada**; dela é possível reabrir para "Em diagnóstico", ajustar o orçamento e reenviar.
6. Serviços e peças só podem ser incluídos ou removidos enquanto a OS está editável (Recebida ou Em diagnóstico).
7. A baixa de estoque acontece na aprovação do orçamento, dentro de uma **transação única** (padrão Unit of Work): baixa de todas as peças + aprovação são confirmadas juntas ou desfeitas juntas; não aprova se faltar saldo em qualquer peça.
8. CPF/CNPJ e placa precisam ser válidos antes de persistir (validação no objeto de valor).
9. CPF/CNPJ (cliente) e placa (veículo) são **únicos**: cadastrar um já existente retorna conflito (HTTP 409).
10. O ano do veículo deve estar numa faixa plausível (1900 até o ano seguinte ao atual).
11. Ao abrir uma OS, se o veículo pertence a um cliente, deve ser o mesmo cliente da OS.

## Relação documentação ↔ código

| Elemento do modelo | Onde está no código |
|--------------------|---------------------|
| Máquina de status (incl. Rejeitada) | `app/domain/status_os.py` |
| Agregado e regras da OS | `app/domain/ordem_servico.py` |
| Objetos de valor (CpfCnpj, Placa, Dinheiro) | `app/domain/value_objects/` |
| Estoque da peça (saldo, baixa, reposição) | `app/domain/cadastros.py` (`Peca`) |
| Transação única da aprovação (Unit of Work) | `app/domain/repositorios.py` (porta) + `app/infrastructure/unit_of_work.py` |
| Unicidade de CPF/placa e validações | `app/application/casos_uso_cadastros.py`, `app/domain/cadastros.py` |
| Fluxos expostos (REST) | `app/interfaces/ordens.py`, `app/interfaces/cadastros.py` |
