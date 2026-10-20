# Relatório de Cobertura de Testes

Reexecutável com `pytest` (ou `pytest --cov=app --cov-report=html`).

Última execução: 2026-10-14 12:04 UTC

```
_______________ coverage: platform linux, python 3.13.16-final-0 _______________

Name                                           Stmts   Miss  Cover   Missing
----------------------------------------------------------------------------
app/__init__.py                                    0      0   100%
app/application/__init__.py                        0      0   100%
app/application/casos_uso.py                     118      6    95%   72, 98, 116, 157, 170, 213
app/application/casos_uso_cadastros.py            56      3    95%   43, 69, 81
app/config.py                                     12      0   100%
app/domain/__init__.py                             0      0   100%
app/domain/cadastros.py                           50      1    98%   72
app/domain/exceptions.py                          13      0   100%
app/domain/itens.py                               21      0   100%
app/domain/ordem_servico.py                      115      2    98%   104, 146
app/domain/repositorios.py                        17      0   100%
app/domain/status_os.py                           13      0   100%
app/domain/value_objects/__init__.py               4      0   100%
app/domain/value_objects/cpf_cnpj.py              47      1    98%   72
app/domain/value_objects/dinheiro.py              29      1    97%   39
app/domain/value_objects/placa.py                 19      1    95%   34
app/infrastructure/__init__.py                     0      0   100%
app/infrastructure/db/__init__.py                  0      0   100%
app/infrastructure/db/base.py                     31      2    94%   69-71
app/infrastructure/db/models.py                   64      0   100%
app/infrastructure/repositorio_memoria.py         33      5    85%   48, 51-54
app/infrastructure/repositorio_sqlalchemy.py      40      0   100%
app/infrastructure/repositorios_crud.py          110     18    84%   46, 79, 110-111, 114-119, 142-143, 146-151
app/infrastructure/seguranca.py                   10      0   100%
app/infrastructure/unit_of_work.py                23      0   100%
app/interfaces/__init__.py                         0      0   100%
app/interfaces/auth.py                            27      1    96%   50
app/interfaces/cadastros.py                      100     12    88%   106, 118-122, 151, 156, 163-164, 169, 193, 205-206, 211
app/interfaces/dependencias.py                    19      6    68%   26, 30, 34, 38, 42, 46
app/interfaces/health.py                           5      0   100%
app/interfaces/ordens.py                          45      0   100%
app/interfaces/relatorios.py                      17      0   100%
app/interfaces/schemas.py                         41      0   100%
app/interfaces/schemas_cadastros.py               43      0   100%
app/main.py                                       36      3    92%   26-27, 56
----------------------------------------------------------------------------
TOTAL                                           1158     62    95%
92 passed in 6.38s
```

**Cobertura total: 95%** - acima do mínimo de 80%. Domínios críticos (entidades,
objetos de valor, agregado, casos de uso) em 95-100%.

## Composição dos testes (pirâmide)

- **Unitários** (domínio e casos de uso): objetos de valor (CPF/CNPJ, placa,
  dinheiro), máquina de status, cálculo de orçamento, estoque, validações e os
  casos de uso com repositórios em memória.
- **Integração** (API + repositório): sobem a aplicação com um banco SQLite em
  memória (o "fake" rápido das aulas) e exercitam os endpoints de ponta a ponta,
  incluindo o fluxo completo da OS, a baixa de estoque transacional na aprovação
  (com teste de rollback), a rejeição/reabertura e as validações de cadastro.
