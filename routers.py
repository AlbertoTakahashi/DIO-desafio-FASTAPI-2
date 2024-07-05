from datetime import datetime
import json
from uuid import uuid4
from fastapi import APIRouter, status, HTTPException
import pandas as pd
import schemas
import models
from json import loads

from SGBD_PostgreSQL import Conexao_BD

roteador = APIRouter()

 

@roteador.get('/', status_code=status.HTTP_200_OK)
def listar_produtos():
    lista_colunas = ",".join(campo for campo in list(models.StoreModel.__fields__.keys()))
    conexao = Conexao_BD()
    sql = f'SELECT {lista_colunas} FROM store;'
    dados = conexao.query_bd(sql)
    conexao.fechar()
    opção = "pandas"
    if opção != "pandas":
        # necessário converter datetime para str pois o método json.dumps() não consegue serializar instancias tipo datetime
        def serialize_datetime(obj): 
            if isinstance(obj, datetime): 
                return obj.strftime("%Y-%m-%d %H:%M:%S")
            raise TypeError("Type not serializable")       
        json_dados = json.dumps(dados, default=serialize_datetime)
        return json_dados
    else:
        aux = models.StoreModel.__fields__.keys()
        colunas = list(aux)
        resp_df = pd.DataFrame(dados, columns=colunas)
        # como a saída é para visualização vamos alterar o tipo datetime para str antes de criar o JSON
        # Obs.: não dá nenhum erro em serializar diretamente o datetime só que é menos inteligível
        resp_df['criado_em'] = resp_df['criado_em'].dt.strftime("%Y-%m-%d %H:%M:%S")
        resp_df['alterado_em'] = resp_df['alterado_em'].dt.strftime("%Y-%m-%d %H:%M:%S")
        return loads(resp_df.to_json(orient='records'))


@roteador.post('/', status_code=status.HTTP_201_CREATED)
def inserir_produto(novo : schemas.SchemaComplementarStore):
    tabela = 'store'
    novo_id = str(uuid4())
    novo_dict = novo.__dict__
    novo_dict.update({"id":novo_id})
    agora = datetime.now().timestamp()
    conexao = Conexao_BD()
    lista_colunas = ",".join(campo for campo in list(novo_dict.keys()))
    valores_colunas = ",".join( 
        ("'"+campo+"'" if type(campo) == str else str(campo)) for campo in list(novo_dict.values())
        )
    sql = f"INSERT INTO {tabela} ({lista_colunas},criado_em, alterado_em) VALUES ({valores_colunas},to_timestamp({agora}),to_timestamp({agora})) RETURNING *;"
    try:
        resp_query = conexao.query_bd(sql)
        teste = resp_query[0]['id']
        # se o "id" não existir na base o mesmo não estará em resp_query e o comando acima dará erro
        conexao.fechar()
        return resp_query
    except:
        resp_query = f"Falha interna (INSERT). Item não adicionado: nome-> {novo.nome}"
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail= f'Produto não inserido (nome= {novo.nome})')
        conexao.fechar()
        return resp_query

@roteador.delete('/', status_code=status.HTTP_200_OK)
def apagar_produto(produto_a_apagar : schemas.SchemaUUID):
    conexao= Conexao_BD()
    sql = f"SELECT id FROM store WHERE id = UUID('{produto_a_apagar.id}');"
    resp_query = conexao.query_bd(sql)
    try:
        teste = resp_query[0]['id']
        # se o "id" não existir na base o mesmo não estará em resp_query e o comando acima dará erro
        sql = f"DELETE FROM store WHERE id = UUID('{produto_a_apagar.id}');"
        resp_query = conexao.query_bd(sql)
    except:
        #raise ErroNoCRUD(f"Falha interna (DELETE). Não localizado produto com id: {produto_a_apagar.id}")
        resp_query = f"Falha interna (DELETE). Não localizado produto com id: {produto_a_apagar.id}"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f'Produto inexistente (id= {produto_a_apagar.id})')
    conexao.fechar()
    return resp_query

@roteador.patch('/', status_code=status.HTTP_200_OK)
def inserir_produto(altera : schemas.SchemaStoreUpdate):
    tabela = 'store'
    conexao= Conexao_BD()
    novo_dict = altera.__dict__
    qual_id = novo_dict['id']    
    sql = f"SELECT id FROM store WHERE id = UUID('{altera.id}');"
    resp_query = conexao.query_bd(sql)
    try:
        teste = resp_query[0]['id']
        # se o "id" não existir na base o mesmo não estará em resp_query e o comando acima dará erro
        novo_dict.pop('id')
        chaves_para_apagar = []
        for chave, valor in novo_dict.items():
            print(f"{chave} : {valor}")
            if valor == None:
                chaves_para_apagar.append(chave)
        if len(chaves_para_apagar) > 0:
            for chave in chaves_para_apagar:
                novo_dict.pop(f'{chave}')
        lista_colunas = ",".join(campo for campo in list(novo_dict.keys()))
        valores_colunas = ",".join( 
            ("'"+campo+"'" if type(campo) == str else str(campo)) for campo in list(novo_dict.values())
            )
        agora = datetime.now().timestamp()
        sql = f"UPDATE {tabela} SET ({lista_colunas},alterado_em) = ({valores_colunas},to_timestamp({agora})) WHERE ID = UUID('{qual_id}') RETURNING *;"
        resp_query = conexao.query_bd(sql)
    except:
        resp_query = f"Falha interna (UPDATE). Não localizado produto com id: {qual_id}"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f'Produto não localizado (id= {qual_id}). Alteração não realizada.')
    conexao.fechar()
    return resp_query

