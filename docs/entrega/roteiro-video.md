# Roteiro do Vídeo — Tech Challenge Fase 1 (máx. 15 min)

> Objetivo: cobrir todos os "mínimos demonstráveis" que o enunciado exige, sem
> estourar 15 minutos. Tempos são sugestões; ensaie uma vez para calibrar.
> Deixe a API já rodando (`uvicorn app.main:app --reload`) e o Swagger aberto
> antes de gravar. Faça login (Authorize → admin/admin123) antes de demonstrar.

| Tempo | Bloco | O que mostrar / falar |
|-------|-------|------------------------|
| 0:00–1:00 | **Abertura** | Nome do grupo e integrantes. A proposta: MVP do back-end de uma oficina mecânica, focado em ordens de serviço, clientes e peças. |
| 1:00–2:30 | **Arquitetura** | Mostrar a estrutura de pastas (`app/domain`, `application`, `infrastructure`, `interfaces`). Explicar o monolito em camadas e a regra de ouro do DDD: a dependência aponta para o domínio; a regra de negócio vive só nele. |
| 2:30–3:30 | **Banco de dados** | Abrir `docs/adr/0001-escolha-do-banco-de-dados.md`. Justificar o SQLite (simplicidade, suficiente para o MVP) e citar que a porta de repositório deixa a troca barata. |
| 3:30–5:00 | **Event Storming + DDD** | Mostrar o board no Miro. Apontar: eventos (laranja), comandos (azul), políticas (roxo); o agregado `OrdemServico`, objetos de valor (`CpfCnpj`, `Placa`, `Dinheiro`), e os bounded contexts (Atendimento, Cadastros, Estoque). |
| 5:00–9:30 | **Demonstração (Swagger)** | 1) **Authorize** (admin/admin123 — JWT). 2) Cadastrar: cliente, veículo (placa/marca/modelo/ano), serviço, peça (com estoque). 3) Criar OS (`POST /ordens-servico`) referenciando `cliente_id` e `veiculo_id`. 4) Incluir serviço e peça na OS por id → orçamento automático. 5) Avançar status: diagnóstico → aprovação → **aprovar (mostrar que baixa o estoque da peça)** → concluir → entregar. 6) Consultar andamento (GET público, sem token). 7) `GET /relatorios/tempo-medio-execucao`. |
| 9:30–10:30 | **Execução & segurança** | Mostrar que a API sobe (uvicorn ou `docker compose up`). Mostrar o Swagger (`/docs`). Mostrar uma rota admin dando 401 sem token (prova do JWT). |
| 10:30–12:30 | **Testes automatizados** | Rodar `pytest` no terminal. Mostrar os 75 testes passando e a cobertura de 94% (acima dos 80%). Abrir `docs/qualidade/cobertura.md`. |
| 12:30–13:30 | **Análise de vulnerabilidade** | Mostrar `docs/qualidade/relatorio-seguranca.md`: bandit (0 issues) e pip-audit (sem vulnerabilidades). Citar a troca de python-jose por PyJWT. |
| 13:30–15:00 | **Fechamento** | Mostrar o repositório no GitHub (main protegida, PRs). Resumir: DDD + camadas + testes + segurança + Docker. Agradecer. |

## Dicas de gravação
- Áudio compreensível é requisito — teste o microfone antes.
- Cada integrante pode narrar um bloco (o enunciado pede identificação/participação dos integrantes).
- Publique no YouTube como **público** e confirme que o link abre numa aba anônima.
- O vídeo deve corresponder ao **commit informado no PDF** — grave depois de fixar a versão de entrega.
