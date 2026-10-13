# Relatório de Cobertura de Testes

Cobertura dos testes automatizados. Reexecutável com:

```bash
pytest
pytest --cov=app --cov-report=html  # gera htmlcov/ navegável
```

Última execução: 2026-10-13 16:44 UTC

```
_______________ coverage: platform linux, python 3.13.16-final-0 _______________

Name                                           Stmts   Miss  Cover   Missing
----------------------------------------------------------------------------
app/__init__.py                                    0      0   100%
app/application/__init__.py                        0      0   100%
app/application/casos_uso.py                      55      1    98%   93
app/application/casos_uso_cadastros.py            46      2    96%   45, 57
app/config.py                                     12      0   100%
app/domain/__init__.py                             0      0   100%
app/domain/cadastros.py                           42      1    98%   57
app/domain/exceptions.py                          11      0   100%
app/domain/itens.py                               18      0   100%
app/domain/ordem_servico.py                       97      1    99%   95
app/domain/repositorios.py                         8      0   100%
app/domain/status_os.py                           12      0   100%
app/domain/value_objects/__init__.py               4      0   100%
app/domain/value_objects/cpf_cnpj.py              47      1    98%   72
app/domain/value_objects/dinheiro.py              29      1    97%   39
app/domain/value_objects/placa.py                 19      1    95%   34
app/infrastructure/__init__.py                     0      0   100%
app/infrastructure/db/__init__.py                  0      0   100%
app/infrastructure/db/base.py                     15      2    87%   33-35
app/infrastructure/db/models.py                   60      0   100%
app/infrastructure/repositorio_memoria.py         13      0   100%
app/infrastructure/repositorio_sqlalchemy.py      41      0   100%
app/infrastructure/repositorios_crud.py          123     26    79%   52, 79-80, 86, 117-119, 122-123, 126-132, 136, 159-160, 163-169
app/infrastructure/seguranca.py                   10      0   100%
app/interfaces/__init__.py                         0      0   100%
app/interfaces/auth.py                            27      1    96%   50
app/interfaces/cadastros.py                       96     13    86%   98, 110-114, 143, 148, 155-156, 161, 185, 190, 197-198, 203
app/interfaces/dependencias.py                    16      5    69%   21, 25, 29, 33, 37
app/interfaces/health.py                           5      0   100%
app/interfaces/ordens.py                          35      0   100%
app/interfaces/relatorios.py                      17      0   100%
app/interfaces/schemas.py                         41      0   100%
app/interfaces/schemas_cadastros.py               43      0   100%
app/main.py                                       33      2    94%   22-23
----------------------------------------------------------------------------
TOTAL                                            975     57    94%
75 passed, 8 warnings in 2.16s
```

**Cobertura total: 94%** — acima do mínimo de 80% exigido. Os domínios críticos (entidades, objetos de valor, agregado, casos de uso) ficam em 97–100%.
