# ADR 0001 — Escolha do banco de dados

- **Status:** Aceito
- **Data:** 2026-10-13
- **Decisão por:** equipe do Tech Challenge (Fase 1)

## Contexto

O MVP do back-end da oficina precisa persistir ordens de serviço, clientes,
veículos e peças. O Tech Challenge exige que a escolha do banco seja livre, mas
**justificada**. Os critérios para esta fase são: simplicidade de execução
local (um `docker compose up` deve bastar), baixo esforço de configuração,
suporte a transações e facilidade para os testes automatizados.

## Decisão

Adotar **SQLite** como banco de dados do MVP.

## Alternativas consideradas

- **PostgreSQL** — robusto e padrão de mercado para produção, mas exige um
  container/serviço adicional, configuração de credenciais e mais tempo de
  setup do que o MVP justifica nesta fase.
- **MySQL** — semelhante ao PostgreSQL em custo de setup, sem vantagem clara
  para o escopo atual.

## Justificativa

- **Zero configuração:** é um arquivo único, sem servidor separado; o ambiente
  sobe inteiro com um só serviço no `docker-compose`.
- **Suficiente para o MVP:** o volume de dados e a concorrência esperados nesta
  fase são baixos.
- **Ótimo para testes:** permite rodar a suíte contra um banco SQLite em
  memória, rápido e isolado.
- **Troca barata no futuro:** o acesso a dados é feito por uma *porta* de
  repositório (`OrdemServicoRepositorio`) no domínio, com a implementação em
  SQLAlchemy isolada na infraestrutura. Migrar para PostgreSQL significa trocar
  o `DATABASE_URL` e, se preciso, a implementação do repositório — **sem tocar
  no domínio nem nos casos de uso**.

## Consequências

**Positivas**
- Setup e execução local simples; menos partes móveis.
- Testes de integração rápidos (SQLite em memória).

**Negativas / limitações**
- Concorrência de escrita limitada; não é adequado para produção de alta carga.
- Alguns recursos de bancos servidor (tipos avançados, replicação) não estão
  disponíveis.

**Plano de evolução:** para produção, migrar para PostgreSQL ajustando o
`DATABASE_URL` e revisando a implementação do repositório. A arquitetura em
camadas já isola essa mudança.
