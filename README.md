# Oficina — Sistema Integrado de Atendimento e Execução de Serviços

MVP do back-end de uma oficina mecânica, desenvolvido para o Tech Challenge
(Fase 1 — SOAT). Aplica Domain-Driven Design, arquitetura em camadas, testes
automatizados e boas práticas de segurança.

> Documento em evolução — as seções são preenchidas conforme o projeto avança.

## Objetivo do projeto

Gerir ordens de serviço, clientes e peças de uma oficina, permitindo acompanhar
o andamento dos serviços em tempo real e manter a gestão interna organizada.

## Arquitetura utilizada

Monolito organizado em camadas (DDD). A dependência aponta sempre para o
domínio; a regra de negócio vive apenas na camada de domínio.

```
app/
  domain/          # entidades, objetos de valor, agregados, regras
  application/     # casos de uso / orquestração
  infrastructure/  # persistência, repositórios, autenticação
  interfaces/      # rotas HTTP (REST) + Swagger
```

Detalhes em [`docs/guia-do-projeto.md`](docs/guia-do-projeto.md) e a modelagem
de domínio em [`docs/ddd/`](docs/ddd/).

## Tecnologias utilizadas

- Python 3.12
- FastAPI (REST + Swagger/OpenAPI automático)
- Pydantic v2
- pytest + pytest-cov

## Pré-requisitos

- Python 3.12+

## Instruções para execução

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

A API sobe em `http://localhost:8000`.

## Instruções para execução dos testes

```bash
pytest
```

A cobertura é exibida no terminal ao final da execução.

## Acesso ao Swagger / documentação da API

Com a aplicação no ar, acesse `http://localhost:8000/docs` (Swagger UI) ou
`http://localhost:8000/redoc`.

## Decisão e justificativa do banco de dados

<!-- Preencher na etapa 5 (ADR da escolha do banco). -->

## Usuários / credenciais de demonstração

<!-- Preencher na etapa 7 (autenticação JWT). -->

## Estrutura dos principais diretórios

- `app/` — código da aplicação, separado por camadas
- `tests/` — testes unitários e de integração
- `docs/` — requisitos, guia do projeto e documentação DDD

## Documentação DDD

Ver [`docs/ddd/`](docs/ddd/) — Event Storming, modelagem e linguagem ubíqua.

## Vídeo da entrega

<!-- Preencher na entrega final. -->
