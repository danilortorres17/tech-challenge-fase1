# Relatório de Segurança

Análise automática de segurança do projeto. Reexecutável:

```bash
pip install -r requirements-dev.txt
bandit -r app
pip-audit -r requirements.txt
```

Última execução: 2026-10-13 16:44 UTC

## 1. Análise estática do código (bandit)

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

**Resultado:** nenhum problema de segurança identificado (0 issues).

## 2. Vulnerabilidades nas dependências (pip-audit)

```
No known vulnerabilities found
```

**Resultado:** nenhuma vulnerabilidade conhecida.

## Decisões de segurança relevantes

- Autenticação **JWT** (PyJWT) nas rotas administrativas e de cadastro; consulta de andamento pública.
- Escolha do **PyJWT** em vez de python-jose, que arrastava a dependência `ecdsa` (vulnerabilidade sem correção).
- Validação de CPF/CNPJ e placa nos objetos de valor; estoque nunca fica negativo (regra de domínio).
- Segredos e credenciais fora do código, via variáveis de ambiente (`.env`, ignorado pelo git).
