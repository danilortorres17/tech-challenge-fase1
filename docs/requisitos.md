# Requisitos — Tech Challenge Fase 1 (enunciado destilado)

> Resumo fiel do enunciado oficial, para consulta rápida durante o desenvolvimento.
> Em qualquer divergência, vale o PDF oficial do curso.

## Contexto

Oficina mecânica de médio porte. Hoje o atendimento, diagnóstico, execução e
entrega são feitos em anotações manuais e planilhas, causando: erros de
priorização, falhas no controle de peças/insumos, dificuldade de acompanhar
status, perda de histórico de clientes/veículos e ineficiência no fluxo de
orçamentos e autorizações.

## Proposta

Desenvolver o **MVP do back-end** de um Sistema Integrado de Atendimento e
Execução de Serviços, focado em **gestão de ordens de serviço, clientes e peças**,
aplicando **DDD**, boas práticas de **qualidade** e **segurança**.

## Funcionalidades obrigatórias

### Criação da Ordem de Serviço
- Identificação do cliente por **CPF ou CNPJ**
- Cadastro do veículo: **placa, marca, modelo, ano**
- Inclusão dos **serviços** solicitados (ex.: troca de óleo, alinhamento)
- Inclusão de **peças e insumos**
- **Geração automática do orçamento** (serviços + peças)
- Envio/disponibilização do orçamento para aprovação
- Registro da **aprovação ou rejeição** do orçamento

### Acompanhamento da OS
- Status: **Recebida → Em diagnóstico → Aguardando aprovação → Em execução → Finalizada → Entregue**
- Controlar as alterações de status e **aplicar as regras de transição**
- Alteração automática do status conforme as ações no sistema
- Endpoint **público** para o cliente consultar o andamento via API

### Gestão administrativa
- CRUD de clientes
- CRUD de veículos
- CRUD de serviços
- CRUD de peças e insumos **com controle de estoque**
- Listagem e detalhamento de ordens de serviço
- Monitoramento / cálculo do **tempo médio de execução** dos serviços

## Requisitos técnicos obrigatórios

- Back-end **monolítico**, organizado **em camadas**
- Banco de dados de **livre escolha, com justificativa escrita**
- **APIs RESTful**
- Documentação **Swagger / OpenAPI** ou equivalente
- **Autenticação JWT** para as APIs administrativas
- **Validação de CPF/CNPJ** e **validação de placa**
- **Testes unitários** e **de integração** dos fluxos principais
- Evidência de **cobertura mínima de 80%** nos domínios críticos
- **Dockerfile** para build + **docker-compose.yml** para o ambiente completo
- Execução local simples (documentada no README)
- **Tratamento adequado de transações** nos fluxos principais

## Entregáveis (um único PDF com todos os links clicáveis)

### 1. Identificação (1ª página do PDF)
Curso (SOAT — Software Architecture), Fase (1), número do grupo, nome completo e
RM de todos os integrantes, username do Discord, linguagem e tecnologias.
Informar **branch + hash do commit** da entrega final (a avaliação considera só essa versão).

### 2. Repositório GitHub
Público durante toda a correção; versão identificada por branch/tag/hash; código
igual ao vídeo e à documentação; sem credenciais/tokens; README completo;
instruções de execução local; testes com ≥80%; doc da API (Swagger/OpenAPI);
relatório de análise de vulnerabilidades. **`main` protegida — tudo entra por PR.**

### 3. README (conteúdo mínimo)
Objetivo; descrição da solução; arquitetura; tecnologias; pré-requisitos;
instruções de execução; instruções de execução dos testes; acesso ao Swagger;
decisão e justificativa do banco; usuários/credenciais de demo ou procedimento de
autenticação; estrutura dos diretórios; link para a doc DDD; link para o vídeo.

### 4. Vídeo (YouTube, público, até 15 min)
Demonstra o sistema real do commit informado. Deve mostrar, no mínimo: proposta;
arquitetura; organização do monólito e camadas; escolha/justificativa do banco;
processo de Event Storming; elementos de DDD; fluxo de criação e acompanhamento
da OS; inclusão de serviços/peças/insumos; geração e aprovação do orçamento;
alteração de status; autenticação das APIs; execução da aplicação; Swagger;
testes automatizados; resultado da análise de vulnerabilidades.

### 5. Documentação DDD (Miro ou equivalente)
Link direto, acessível sem pedir permissão, e **exportada para o repo** em `docs/ddd/`
(`event-storming.pdf`, `diagramas.pdf`, `linguagem-ubiqua.md`). Deve conter:
- Event Storming dos 3 fluxos: criação da OS, acompanhamento da OS, gestão de peças/insumos
- Eventos de domínio, comandos, políticas/regras, atores
- Agregados, entidades, objetos de valor
- Bounded Contexts (quando identificados)
- Diagramas solicitados na disciplina de DDD
- Linguagem ubíqua + glossário dos principais termos
- Relação entre a documentação e a implementação no código

> A documentação precisa **representar a solução entregue**. Diagramas genéricos,
> exemplos de aula ou documentação que não corresponda ao código **não contam**
> como evidência completa.

## Observações

- Atividade **em grupo**, **obrigatória**, vale **90% da nota da fase**.
- Correção com base em código-fonte, documentação, vídeo e evidências.
- Responsabilidade do grupo garantir que todos os links estejam corretos e acessíveis.
