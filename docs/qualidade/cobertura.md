# Relatório de Cobertura de Testes

Reexecutável com `pip install -r requirements-dev.txt` e `pytest` (ou
`pytest --cov=app --cov-report=html`).

Última execução: 2026-10-26

```
_______________ coverage: platform linux, python 3.13.16-final-0 _______________

Name                                           Stmts   Miss  Cover   Missing
----------------------------------------------------------------------------
app/application/casos_uso.py                     116      7    94%   73, 99, 117, 158, 171, 179, 217
app/application/casos_uso_cadastros.py            56      3    95%   43, 69, 81
app/config.py                                     24      0   100%
app/domain/cadastros.py                           50      1    98%   72
app/domain/exceptions.py                          13      0   100%
app/domain/itens.py                               21      0   100%
app/domain/ordem_servico.py                      120      2    98%   105, 149
app/domain/repositorios.py                        19      0   100%
app/domain/status_os.py                           13      0   100%
app/domain/usuario.py                             10      0   100%
app/domain/value_objects/cpf_cnpj.py              47      1    98%   72
app/domain/value_objects/dinheiro.py              29      1    97%   39
app/domain/value_objects/placa.py                 19      1    95%   34
app/infrastructure/db/base.py                     31      2    94%   69-71
app/infrastructure/db/models.py                   82      0   100%
app/infrastructure/observabilidade.py             32      3    91%   35, 67-68
app/infrastructure/repositorio_auditoria.py       13      0   100%
app/infrastructure/repositorio_memoria.py         40      6    85%   48, 51-54, 83
app/infrastructure/repositorio_sqlalchemy.py      40      0   100%
app/infrastructure/repositorio_usuario.py         28      0   100%
app/infrastructure/repositorios_crud.py          110     18    84%   46, 79, 110-111, 114-119, 142-143, 146-151
app/infrastructure/seguranca.py                   12      0   100%
app/infrastructure/senhas.py                       9      0   100%
app/infrastructure/startup.py                     10      1    90%   19
app/infrastructure/unit_of_work.py                29      0   100%
app/interfaces/auditoria.py                        9      0   100%
app/interfaces/auth.py                            49      4    92%   62-63, 86, 99
app/interfaces/cadastros.py                      106     13    88%   116, 131-136, 165, 170, 177-178, 183, 207, 219-220, 225
app/interfaces/dependencias.py                    27      9    67%   31, 35, 39, 43, 47, 51, 55, 59, 63
app/interfaces/health.py                           5      0   100%
app/interfaces/ordens.py                          60      0   100%
app/interfaces/relatorios.py                      17      0   100%
app/interfaces/schemas.py                         51      0   100%
app/interfaces/schemas_cadastros.py               44      0   100%
app/main.py                                       45      5    89%   29-31, 62, 71
----------------------------------------------------------------------------
TOTAL                                           1390     77    94%
109 passed
```

**Cobertura total: 94%** - acima do mínimo de 80%. Domínios críticos (entidades,
objetos de valor, agregado, casos de uso) em 94-100%.

## Composição dos testes (pirâmide)

- **Unitários** (domínio e casos de uso): objetos de valor (CPF/CNPJ, placa,
  dinheiro), máquina de status, cálculo de orçamento, estoque, validações, os
  casos de uso com repositórios em memória, o hash/verificação de senha (bcrypt)
  e a validação de configuração que impede subir em produção com segredo padrão.
- **Integração** (API + repositório): sobem a aplicação com um banco SQLite em
  memória (o "fake" rápido das aulas) e exercitam os endpoints de ponta a ponta,
  incluindo o fluxo completo da OS, a baixa de estoque transacional na aprovação
  (com teste de rollback e de recusa atômica quando falta saldo), a rejeição/
  reabertura, as validações de cadastro, a recusa de id inválido (422), a
  divergência de moeda, a máscara do documento na consulta pública, o login com
  senha em hash, a revogação de token no logout e o registro da trilha de auditoria.
