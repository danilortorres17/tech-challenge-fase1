# Relatório de Segurança

Reexecutável: `pip install -r requirements-dev.txt` então `bandit -r app` e `pip-audit -r requirements.txt`.

Última execução: 2026-10-13 18:13 UTC

## 1. Análise estática (bandit)

```
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

**Resultado:** 0 issues.

## 2. Vulnerabilidades nas dependências (pip-audit)

```
No known vulnerabilities found
```

**Resultado:** nenhuma vulnerabilidade conhecida.

## Decisões de segurança

- JWT (PyJWT) nas rotas administrativas; consulta de andamento pública.
- Validação de CPF/CNPJ e placa nos objetos de valor; estoque nunca fica negativo.
- Baixa de estoque na aprovação com verificação prévia (não aprova se faltar saldo).
- Segredos via variáveis de ambiente (`.env`, ignorado pelo git).
