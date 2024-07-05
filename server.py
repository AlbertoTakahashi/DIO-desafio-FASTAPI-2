from time import time, ctime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request

# pacotes desenvolvidos na aplicação
import routers

app = FastAPI(title="Store_Api")

origins = ["http://127.0.0.1"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# lembrando que "roteador = APIRouter()" dentro do pacote "routers.py" importado acima
app.include_router(routers.roteador, prefix="/store")

@app.middleware('http')
async def calcula_tempo_execucao(requisicao_entrada: Request, next):
    # next indica encaminhar o código interceptado para execução
    print()
    print('------------------------------------------')
    horario_inicio = time()
    print('Início de execucao: ', end='')
    print(ctime())
    print('Tipo da requisição: ' + requisicao_entrada.method)
    # if requisicao_entrada.method == 'GET':
    #     print('Recebi uma requisição tipo GET')
    # print()
    # print('HEADERS da requisição:')
    # print(requisicao_entrada.headers)
    print()
    print('Requisição: ', end='')
    print(requisicao_entrada.url)
    print()
    print('Header authorization: ', requisicao_entrada.headers.get('authorization'))
    print()
    #breakpoint()    
    # o tratamento dos tokens poderia ser realizado aqui caso desejado...
    print('Enviando para tratamento pelo backend...')

    resposta_do_backend = await next(requisicao_entrada)

    print('Recebida resposta do backend...')
    horario_termino = time()
    print('Final de execução: ', end='')
    print(ctime())

    duracao = horario_termino - horario_inicio
    print('Duração total: ' + str(duracao))
    print('Response code = ' + str(resposta_do_backend.status_code))
    print('------------------------------------------')
    print()
    return resposta_do_backend




