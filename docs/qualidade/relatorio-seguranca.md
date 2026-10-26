# Relatório de Segurança

Reexecutável: `pip install -r requirements-dev.txt` então `bandit -r app` e `pip-audit -r requirements.txt`.

Última execução: 2026-10-26 11:35 UTC

## 1. Análise estática (bandit)

```
Test results:
	No issues identified.

Code scanned:
	Total lines of code: 2173
	Total lines skipped (#nosec): 0
	Total potential issues skipped due to specifically being disabled (e.g., #nosec BXXX): 1

Run metrics:
	Total issues (by severity):
		Undefined: 0
		Low: 0
		Medium: 0
		High: 0
	Total issues (by confidence):
		Undefined: 0
		Low: 0
		Medium: 0
		High: 0
Files skipped (0):
```

**Resultado:** 0 issues. O único apontamento desabilitado por `#nosec` é a
string literal `"bearer"` (tipo de token padrão do OAuth2, não um segredo).

## 2. Vulnerabilidades nas dependências (pip-audit)

```
No known vulnerabilities found
```

**Resultado:** nenhuma vulnerabilidade conhecida.

## Decisões de segurança

- **Senha em hash (bcrypt).** As senhas nunca são guardadas em texto puro; o
  usuário administrativo é semeado no primeiro boot já com o hash. A verificação
  no login usa comparação resistente a timing do próprio bcrypt.
- **Segredo do JWT obrigatório em produção.** Com `APP_ENV=production`, a
  aplicação recusa subir (falha explícita) enquanto o `JWT_SECRET` estiver no
  valor padrão ou vazio, evitando assinar tokens com um segredo conhecido.
- **Identificador único de sessão e logout.** Cada token carrega `jti` e `iat`
  além de `sub`/`papel`/`exp`. O `POST /auth/logout` registra o `jti` numa
  denylist e as rotas passam a recusar aquele token, permitindo encerrar a
  sessão antes de expirar.
- **Baixa de estoque atômica.** A aprovação dá baixa por um `UPDATE` condicional
  (`estoque >= quantidade`) que só efetiva se houver saldo, impedindo baixa dupla
  ou estoque negativo mesmo sob concorrência (anti-TOCTOU).
- **Trilha de auditoria e log estruturado.** Eventos sensíveis (login, criação
  de OS, mudanças de status) são registrados numa tabela de auditoria, consultável
  em `GET /auditoria` (rota autenticada). Os logs da aplicação saem em formato
  JSON. O registro de auditoria é best-effort e nunca interrompe o fluxo principal.
- JWT (PyJWT) nas rotas administrativas; consulta de andamento pública.
- Validação de CPF/CNPJ e placa nos objetos de valor; estoque nunca fica negativo.
- Consulta pública mascara o documento do cliente (LGPD), expondo só os 2 últimos dígitos.
- Segredos via variáveis de ambiente (`.env`, ignorado pelo git).
