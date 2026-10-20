# Linguagem Ubíqua - Oficina Mecânica

> Glossário dos termos do domínio. É a linguagem única usada no negócio, na
> documentação e no código (nomes de classes, métodos e endpoints). Sempre que
> surgir um termo novo durante o desenvolvimento, registre-o aqui.

## Glossário

| Termo | Definição | No código |
|-------|-----------|-----------|
| **Cliente** | Pessoa física (CPF) ou jurídica (CNPJ) dona de um ou mais veículos. | `Cliente` |
| **Veículo** | Automóvel atendido pela oficina, identificado pela placa. | `Veiculo` |
| **Placa** | Identificador único do veículo; formato validado. | `Placa` (VO) |
| **CPF/CNPJ** | Documento do cliente; validado antes de persistir. | `CpfCnpj` (VO) |
| **Ordem de Serviço (OS)** | Registro central do atendimento: reúne veículo, serviços, peças, orçamento e status. | `OrdemServico` (agregado) |
| **Serviço** | Trabalho executado no veículo (ex.: troca de óleo), com preço de mão de obra. | `Servico` |
| **Peça / Insumo** | Item físico consumido no serviço; tem preço e saldo em estoque. | `Peca` |
| **Estoque** | Saldo disponível de uma peça/insumo. | parte do agregado `Peca` |
| **Orçamento** | Soma dos serviços e peças da OS, submetida ao cliente para aprovação. | `Orcamento` (VO) |
| **Aprovação** | Decisão do cliente que autoriza a execução e destrava a mudança de status. | evento `Orçamento aprovado` |
| **Status da OS** | Situação atual da ordem no fluxo de atendimento. | `StatusOS` (VO) |
| **Diagnóstico** | Avaliação técnica do veículo pelo mecânico. | - |
| **Tempo médio de execução** | Indicador: média de tempo entre início e fim da execução das OS. | consulta/relatório |

## Status da Ordem de Serviço

| Status | Significado |
|--------|-------------|
| **Recebida** | OS aberta; veículo deu entrada. |
| **Em diagnóstico** | Mecânico avaliando o veículo. |
| **Aguardando aprovação** | Orçamento enviado; esperando decisão do cliente. |
| **Em execução** | Orçamento aprovado; serviços em andamento. |
| **Finalizada** | Serviços concluídos. |
| **Entregue** | Veículo devolvido ao cliente. |
| **Rejeitada** | Cliente recusou o orçamento; pode ser reaberta para ajuste e reenvio. |

## Atores

| Ator | Papel |
|------|-------|
| **Atendente** | Abre a OS, cadastra cliente/veículo, monta e envia o orçamento, entrega o veículo. |
| **Mecânico** | Faz o diagnóstico e executa os serviços. |
| **Estoquista** | Cadastra e repõe peças e insumos. |
| **Cliente** | Aprova ou rejeita o orçamento e consulta o andamento da OS. |
