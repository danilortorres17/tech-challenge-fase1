"""Testes do objeto de valor CpfCnpj."""
import pytest

from app.domain.exceptions import DocumentoInvalido
from app.domain.value_objects import CpfCnpj


def test_cpf_valido_normaliza_digitos() -> None:
    doc = CpfCnpj("111.444.777-35")
    assert doc.valor == "11144477735"
    assert doc.tipo == "CPF"
    assert doc.formatado() == "111.444.777-35"


def test_cnpj_valido_normaliza_digitos() -> None:
    doc = CpfCnpj("11.222.333/0001-81")
    assert doc.valor == "11222333000181"
    assert doc.tipo == "CNPJ"
    assert doc.formatado() == "11.222.333/0001-81"


@pytest.mark.parametrize(
    "invalido",
    [
        "111.444.777-00",   # dígito verificador errado
        "11.222.333/0001-00",
        "123",              # curto demais
        "00000000000",      # todos iguais
        "abc",              # sem dígitos
        "",                 # vazio
    ],
)
def test_documento_invalido_lanca_erro(invalido: str) -> None:
    with pytest.raises(DocumentoInvalido):
        CpfCnpj(invalido)


def test_igualdade_por_valor() -> None:
    assert CpfCnpj("111.444.777-35") == CpfCnpj("11144477735")
