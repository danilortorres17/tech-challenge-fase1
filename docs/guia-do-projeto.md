# Guia do Projeto — Tech Challenge Fase 1

> **Fonte da verdade do projeto.** Este guia define como o código é organizado e
> o que conta como "pronto". Em caso de dúvida sobre o que o desafio exige, vale
> o enunciado destilado em `docs/requisitos.md`.

## Stack

- **Python 3.12** + **FastAPI** (REST)
- **Pydantic v2** — schemas de entrada/saída e validação dos objetos de valor
- **SQLAlchemy** — persistência
- **pytest** + **pytest-cov** — testes e cobertura
- **JWT** (`python-jose` + `passlib`) — autenticação das rotas administrativas
- **Swagger / OpenAPI** — gerado automaticamente pelo FastAPI em `/docs`

## Arquitetura: monolito em camadas

A dependência sempre aponta **para dentro**. Nada de fora conhece detalhe de
implementação; o núcleo não conhece ninguém.

```
interfaces  →  application  →  domain  ←  infrastructure
```

- `app/domain/` — não importa nenhuma outra camada. Python puro.
- `app/application/` — importa só `domain`.
- `app/infrastructure/` — importa `domain` (implementa as interfaces que ele define).
- `app/interfaces/` — importa `application`.

**Regra de ouro:** regra de negócio vive **só** em `domain`. Controller não decide
nada de negócio; repositório não tem regra. Se bateu vontade de colocar um `if` de
negócio num controller, ele pertence a uma entidade ou ao agregado.

## O que vai em cada camada

- **domain/**
  - Entidades: `Cliente`, `Veiculo`, `OrdemServico`, `Servico`, `Peca`
  - Objetos de valor: `CpfCnpj`, `Placa`, `Dinheiro`, `Orcamento`
  - Agregado: `OrdemServico` é a raiz — só ela altera o próprio estado
  - Regras de transição de status
- **application/** — casos de uso: `CriarOrdemServico`, `IncluirServicosEPecas`,
  `GerarOrcamento`, `AprovarOrcamento`, `AvancarStatus`, CRUDs...
- **infrastructure/** — modelos SQLAlchemy, repositórios, config de banco, auth JWT
- **interfaces/** — rotas FastAPI, schemas de request/response, dependências de segurança

## Máquina de status da Ordem de Serviço

```
Recebida → Em diagnóstico → Aguardando aprovação → Em execução → Finalizada → Entregue
```

- As transições válidas são definidas **no agregado** `OrdemServico`.
- Pular etapa é erro de domínio (lança exceção), não um estado que o banco aceita.
- A aprovação/rejeição do orçamento é o que destrava a saída de "Aguardando aprovação".

## Definition of Done (vale para TODA feature)

Uma tarefa só está pronta quando:

1. O código está na camada certa (respeitando a direção de dependência).
2. Tem teste unitário no domínio e, se for um fluxo, teste de integração.
3. A cobertura dos domínios críticos continua **≥ 80%**.
4. Se surgiu um termo novo do negócio, ele foi registrado em
   `docs/ddd/linguagem-ubiqua.md` (glossário sempre atualizado).
5. Entrou na `main` por **Pull Request** (nunca commit direto).

## Convenções

- Linguagem ubíqua em **português** nos nomes do domínio: `OrdemServico`,
  `Orcamento`, `Peca`, `avancar_status()`. O código fala a língua do negócio.
- Validação de CPF/CNPJ e placa acontece **no objeto de valor** — falha cedo,
  antes de virar entidade.
- Nenhum segredo no repositório. Variáveis sensíveis vão em `.env`
  (que está no `.gitignore`); `.env.example` documenta as chaves necessárias.

## Fluxo de Git

- `main` protegida; todo trabalho em branch `feature/<nome>`.
- Merge só por PR, usando o template de `.github/pull_request_template.md`.
- Commits pequenos e descritivos, em português.
