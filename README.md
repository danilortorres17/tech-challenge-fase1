# Oficina - Sistema Integrado de Atendimento e Execução de Serviços

MVP do back-end de uma oficina mecânica, desenvolvido para o Tech Challenge
(Fase 1 - SOAT). Aplica Domain-Driven Design, arquitetura em camadas, testes
automatizados e boas práticas de segurança.

## Objetivo do projeto

Gerir ordens de serviço, clientes e peças de uma oficina, permitindo acompanhar
o andamento atualizado dos serviços e manter a gestão interna organizada.

## Descrição da solução

A Ordem de Serviço (OS) é o núcleo: o cliente é identificado por CPF/CNPJ, o
veículo é cadastrado, serviços e peças são incluídos, e o orçamento é calculado
automaticamente. A OS percorre uma máquina de status
(Recebida → Em diagnóstico → Aguardando aprovação → Em execução → Finalizada →
Entregue; um orçamento recusado vai para Rejeitada e pode ser reaberto para
ajuste) com regras de transição aplicadas no domínio. A aprovação dá baixa no
estoque das peças dentro de uma transação única (Unit of Work). As rotas
administrativas são protegidas por JWT; a consulta de andamento é pública.

## Arquitetura utilizada

Monolito organizado em camadas (DDD). A dependência aponta sempre para o
domínio; a regra de negócio vive apenas na camada de domínio.

```
app/
  domain/          # entidades, objetos de valor, agregados, regras
  application/     # casos de uso / orquestração
  infrastructure/  # persistência (SQLAlchemy), repositórios, segurança (JWT)
  interfaces/      # rotas HTTP (REST) + Swagger
```

Detalhes em [`docs/guia-do-projeto.md`](docs/guia-do-projeto.md), a modelagem de
domínio em [`docs/ddd/`](docs/ddd/) e as decisões em [`docs/adr/`](docs/adr/).

## Tecnologias utilizadas

- Python 3.13
- FastAPI (REST + Swagger/OpenAPI automático)
- Pydantic v2
- SQLAlchemy 2 + SQLite
- PyJWT (autenticação JWT)
- pytest + pytest-cov
- bandit + pip-audit (análise de segurança)
- Docker + docker-compose

## Pré-requisitos

- Para rodar com Docker: Docker e Docker Compose.
- Para rodar local sem Docker: Python 3.13+.

## Instruções para execução

### Com Docker (recomendado)

```bash
docker compose up --build
```

A API sobe em `http://localhost:8000`.

### Local, sem Docker

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Instruções para execução dos testes

```bash
pip install -r requirements-dev.txt
pytest
```

As dependências de teste (pytest, httpx) ficam em `requirements-dev.txt`, fora do
runtime de produção. A cobertura é exibida no terminal ao final da execução.

## Qualidade e segurança

- **Cobertura de testes:** 95% (mínimo exigido: 80%). Evidência em
  [`docs/qualidade/cobertura.md`](docs/qualidade/cobertura.md).
- **Análise de segurança:** `bandit` (código) e `pip-audit` (dependências),
  ambos sem apontamentos. Relatório em
  [`docs/qualidade/relatorio-seguranca.md`](docs/qualidade/relatorio-seguranca.md).

Para reexecutar:

```bash
pip install -r requirements-dev.txt
bandit -r app
pip-audit -r requirements.txt
```

## Acesso ao Swagger / documentação da API

Com a aplicação no ar, acesse `http://localhost:8000/docs` (Swagger UI) ou
`http://localhost:8000/redoc`.

## Decisão e justificativa do banco de dados

O banco escolhido é o **SQLite**, pela simplicidade de execução local, pelo
baixo custo de configuração e por ser suficiente para o volume do MVP. Como o
acesso a dados é feito por uma porta de repositório no domínio, a troca por
outro banco (ex.: PostgreSQL) não afeta domínio nem casos de uso. Justificativa
completa em [`docs/adr/0001-escolha-do-banco-de-dados.md`](docs/adr/0001-escolha-do-banco-de-dados.md).

## Autenticação (credenciais de demonstração)

As rotas administrativas exigem um token JWT. Para obter o token:

1. `POST /auth/token` com `username=admin` e `password=admin123` (ou, no
   Swagger, use o botão **Authorize**).
2. Envie o token no header `Authorization: Bearer <token>` nas rotas
   administrativas.

As credenciais e o segredo do JWT são configuráveis por variáveis de ambiente
(ver `.env.example`).

## Estrutura dos principais diretórios

- `app/` - código da aplicação, separado por camadas
- `tests/` - testes unitários e de integração
- `docs/` - requisitos, guia do projeto, documentação DDD e ADRs

## Documentação DDD

Ver [`docs/ddd/`](docs/ddd/) - Event Storming, modelagem e linguagem ubíqua.

## Vídeo da entrega

<!-- Preencher na entrega final. -->
