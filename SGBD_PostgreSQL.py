from config import bd_banco, bd_endereco, bd_usuario_api, bd_usuario_pw
import psycopg2
import psycopg2.extras

class Conexao_BD(object):

    def __init__(self, nome_host = bd_endereco, nome_db = bd_banco, usr = bd_usuario_api, pwd = bd_usuario_pw):
        '''
        Os métodos do Cursor fetch, por padrão, retornam os registros recebidos do banco de dados como tuplas. 
        Isso pode ser alterado para melhor atender às necessidades do programador usando row factories personalizadas
        '''
        self._db = psycopg2.connect(host=nome_host,                                    
                                    database=nome_db, 
                                    user=usr,  
                                    password=pwd)
        # neste formato a conversão da saída para dicionário era feito pelo código abaixo
        self._cur=self._db.cursor()
        # neste formato a conversão da saída para dicionário é feito diretamente pelo "cursor_factory"
        # self._cur=self._db.cursor(cursor_factory = psycopg2.extras.DictCursor)

    def query_bd(self, sql):
        try:
            self._cur.execute(sql)
            dados = 'OK'
            if ('INSERT' in sql) or ('SELECT' in sql) or ('UPDATE' in sql):
                dados = self._cur.fetchall()

            if ('INSERT' in sql) or ('UPDATE' in sql) or ('DELETE' in sql) or ('UPDATE' in sql):
                self._db.commit()
            #return dados

            # com o "cursor_factory" "dados" já está no formato de dicionário

            # obs.: não sei porque mas consultando este dicionário ("dados") este não é impresso como chave:valor
            # Mas é uma lista de dicionários pois o mesmo pode ser chamado por dados[0]['nome da chave']
                
            # sem o "cursor_factory" é necessário o código abaixo para conversão para o formato de dicionário
            # mas aqui a apresentação é no formato chave : valor
            columns = list(self._cur.description)
            dados_dicionario = []
            for row in dados:
                row_dict = {}
                for i, col in enumerate(columns):
                    row_dict[col.name] = row[i]
                dados_dicionario.append(row_dict) 
            return dados_dicionario               
            
                # fazer o fetchall() em uma query que não tem retorno (INSERT, DELETE, UPDATE) gera erro e encaminha
                # o código para o except
                # Obs.: INSERT no postgreSQL pode opcionalmente ter retorno ('returning ...'). Porém como não é uma
                #       cláusula obrigatória, não consideraremos...
        except:
            self._db.rollback()
            return f'Não executado. Verifique os dados e tente novamente: {sql}'
      
    def fechar(self):
        self._cur.close()
        self._db.close()
