
from fastapi import HTTPException
import pytest
from routers import inserir_produto
import schemas


def test_insert_return_falha():
    dados = { "nome" : "Iphone 15","quantidade" : 20, "preco" : 6500, "status" : "True"}
    produto = schemas.SchemaComplementarStore(**dados)
    with pytest.raises(HTTPException) as erro:
         inserir_produto(produto)
    assert erro.value.status_code == 406
