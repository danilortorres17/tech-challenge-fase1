# Modelo do PDF de entrega — Tech Challenge Fase 1

> A entrega é um único PDF. Preencha os campos entre colchetes e gere o PDF
> (pode escrever aqui no Markdown e exportar, ou copiar para o Word/Docs).
> Confira que TODOS os links abrem numa aba anônima antes de enviar.

---

## 1. Identificação da entrega (1ª página — obrigatória)

- **Curso:** SOAT — Software Architecture
- **Fase:** 1
- **Número do grupo:** [preencher]
- **Integrantes e RMs:**
  - Danilo Torres — RM 377478
  - [Integrante 2] — RM [....]
  - [Integrante 3] — RM [....]
- **Username(s) do Discord:** [preencher]
- **Linguagem e principais tecnologias:** Python 3.13, FastAPI, SQLAlchemy, SQLite, PyJWT, Pytest, Docker

## 2. Repositório

- **Link do repositório (público):** https://github.com/danilortorres17/tech-challenge-fase1
- **Branch da entrega:** main
- **Hash do commit da entrega:** [preencher — `git rev-parse HEAD` na main]

> A avaliação considera exclusivamente essa versão. A `main` está protegida e
> todo código entrou via Pull Request.

## 3. Vídeo da entrega

- **Link do vídeo (YouTube, público):** [preencher]
- Duração: até 15 minutos. Corresponde ao commit informado acima.

## 4. Documentação DDD

- **Link do board (Miro, acesso sem solicitar permissão):** [preencher]
- Também exportada no repositório em `docs/ddd/` (event-storming, diagramas, linguagem ubíqua).

## 5. Observações (opcional, mas recomendado)

- **Documentação da API (Swagger):** disponível em `/docs` com a aplicação no ar.
- **Relatório de cobertura:** `docs/qualidade/cobertura.md` (94%).
- **Relatório de análise de vulnerabilidades:** `docs/qualidade/relatorio-seguranca.md` (bandit + pip-audit, sem apontamentos).
- **Credenciais de demonstração:** usuário `admin`, senha `admin123` (rotas administrativas via JWT).

---

## Checklist antes de enviar

- [ ] Primeira página com todos os campos de identificação preenchidos
- [ ] Hash do commit da entrega preenchido e correspondente ao vídeo
- [ ] Link do repositório público e acessível
- [ ] Link do vídeo público e acessível
- [ ] Link do Miro acessível sem pedir permissão
- [ ] `main` protegida (tudo via PR) — já configurado
- [ ] README completo no repositório — já pronto
- [ ] Testes com cobertura ≥ 80% — 94%
- [ ] Relatório de vulnerabilidade no repositório — já pronto
