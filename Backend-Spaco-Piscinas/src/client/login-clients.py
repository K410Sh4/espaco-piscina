import os 
from dotenv import load_dotenv
from typing import Optional
from fastapi import FastAPI, HTTPException, status
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
import aiomysql
import json
import ssl

load_dotenv()
ssl_ctx = ssl.create_default_context()

# Fazer conexao com o banco de dados (SQL)

async def inicializar_banco():

# Atribui uma variavel conn que recbera false ou true conforme a espera do retorno da conexao com o aiomysql
    conn = await aiomysql.connect(
        host = str (os.getenv ("SQL_HOSTNAME")),
        port = int (os.getenv ("SQL_PORT")),
        user =      os.getenv("SQL_USER"),
        password =  os.getenv("SQL_PASSWORD"),

    # Em Python, autocommit (ou auto-confirmação) é um modo de operação nas conexões com bancos de dados onde cada instrução SQL (INSERT, UPDATE, DELETE)
    # é automaticamente confirmada (commitada) no banco de dados assim que é executada. 

        autocommit = True,

    #Em Python, ssl_ctx é uma abreviação comumente usada para uma instância da classe ssl.SSLContext, pertencente ao módulo nativo ssl. Ele funciona como um 
    #contêiner de configuração e políticas de segurança para conexões de rede seguras (SSL/TLS). 

        ssl = ssl_ctx
    )
    
    #CONN
    #Em Python, conn (de connection) é uma variável que representa uma conexão ativa com um recurso externo, como um banco de dados 
    #(MySQL, PostgreSQL, etc.) ou um servidor de rede, permitindo que seu código troque dados com esse recurso, geralmente através de um 
    #"conector" ou "driver" específico. É um objeto que gerencia a comunicação, permitindo executar comandos (como consultas SQL) e receber
    # resultados. 

    #CURSOR
    #cursor é um objeto utilizado para interagir com o banco, permitindo executar comandos SQL e percorrer (iterar) os resultados de uma 
    #consulta. Ele atua como uma ponte ou mediador entre o seu script Python e o banco de dados. 

    cursor = await conn.cursor()

    # A partir daqui os comandos executados dentro do cursor serao programados em sql,já que o cursor serve exatamente para isso, mandar iformacoes
    # de uma linguagem para outra linguagem

    # Aqui ele diz para em sql que se nao houver valor para a variável DB_NAME entâo ela criará a tabela com o nome da variavel
    await cursor.execute(f"CREATE DATABASE IF NOT EXIST {os.getenv('DB_NAME')}")

    # Em sql será dito que será usada a tabela com valor da variavel DB_NAME
    await cursor.execute(f"USE {os.getenv('DB_NAME')}")

    # Se a tabela nao existir o cursor dentro do mysql executará o seguinte comando para a criacao da tabela
    await cursor.execute("""
        CREATE TABLE IF NOT EXIST pedidos (
            id INT ATO_INCREMENT PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            produto JSON NOT NULL,
            quantidade INT NOT NULL,
            valor DECIMAL(10,2) NOT NULL,
            adicionais JSON,
            status VARCHAR(20) DEFAULT 'Pendente'
        )AUTO_INCREMENT = 100000    
""")
    
    # A conexao com o cursor com o sql será fechada 
    await cursor.close()

    # a conexao com o CONN é fechada
    conn.close()

# A funcao de inicializacao de banco de dados é interrompida

# funcao para estabelecer a conexao com o banco de dados, neste caso ela é assincrona ent ela nao precisa necessariamente ser executada 
#primeiramente que o inicializador de banco de dados
async def get_conn ():

    # O aiomysql é uma biblioteca Python utilizada para conectar e interagir com bancos de dados MySQL ou MariaDB de forma assíncrona.
    # utiliza o framework asyncio (PEP-3156) para permitir que as operações de banco de dados não bloqueiem a execução do seu código 
    # Python, tornando-o ideal para aplicações de alto desempenho. 

    # Ela ultilizará o aiomysql e retorna os valores das variaveis a seguir conforme o que foi colocado dentro das seguintes colunas do sql
    return await aiomysql.connect(
        host     = os.getenv("SQL_HOST"),
        port     = os.getenv("SQL_PORT"),
        user     = os.getenv("SQL_USER"),
        password = os.getenv("SQL_PASSWORD"),
        db       = os.getenv("SQL_DB_NAME"),
        autocommit = True,
        ssl      = ssl_ctx
    )
# Como python ultiliza bastante do recurso de identacao entao a funcao é finalizada justamente após o termino de identacao

#O @asynccontextmanager é um decorador no Python, localizado no módulo contextlib (introduzido no Python 3.7+), que facilita 
#a criação de gerenciadores de contexto assíncronos (async with) sem a necessidade de definir classes com métodos mágicos (__aenter__/__aexit__). 
@asynccontextmanager

#O @app.on_event("startup") (geralmente referido no contexto de app_startup ou eventos de inicialização) no Python é um decorador específico do
#framework FastAPI (e também usado no Starlette) que define uma função para ser executada automaticamente antes que a aplicação comece a receber requisições. 
async def app_startup(app: FastAPI):

    #O codigo que ira rodar dentro do FastAPI após o startup
    print("Inicializando Banco...")
    await inicializar_banco()

    #yield em Python é uma palavra-chave que transforma uma função em um gerador, permitindo que ela produza uma sequência de valores sob demanda, 
    #pausando sua execução e mantendo seu estado para retornar valores um de cada vez, de forma preguiçosa, economizando memória, diferentemente de return que encerra a função. É ideal para trabalhar com grandes conjuntos de dados ou fluxos infinitos, pois os valores são gerados "na hora" e não armazenados todos de uma vez na memória. 
    yield

    
    app = FastAPI(

        #Define o título da aplicação. Esse título aparece na documentação automática gerada pelo FastAPI (Swagger UI e Redoc).
        title = "Lanchoete do Bairro",

        #É um resumo curto da aplicação, também exibido na documentação interativa.
        summary = "Aplicação de registro de pedidos da loja",

        #lifespan serve para definir o ciclo de vida da aplicação — ou seja, o que acontece quando ela inicia e quando ela é encerrada.
        lifespan = app_startup
    )

    #Em Python, class é a palavra-chave usada para criar uma classe, que nada mais é do que um "molde" ou "modelo" para construir objetos.
    
    #O BaseModel é uma classe fornecida pela biblioteca Pydantic, que o FastAPI usa para validação e definição de dados.
    # Permite definir atributos com tipos (ex.: str, int, float) e automaticamente valida se os dados recebidos têm o tipo correto.
    class Pedido(BaseModel):
        id :       Optional[int] = None
        nome:      str 
        produto:   list[str]
        quantidade:int
        valor:     float[10,2]

        #aqui se nao for fonecido os valores dos adicionais, por padrao os adicionais serao inexistentes
        adicionais:Optional[list[str]] = None
        status:    str = "Pendente"
    
    @app.post("/pedidos")

    # a seguinte funcao assincrona relaciona a tabela mysql pedido com a formatacao atribuída a classe Pedido do python
    async def criar_pedido(pedido: Pedido)
        
        conn = await get_conn()
        cursor = await conn.cursor()

        #foram utilizadas 6 aspas duplas para indicar fechamento e abertura de códigos em múltiplas linhas
        sql = """
           ISERT INTO pedidos (nome, produto, quantidade, valor, adicionais, status)
           VALUES (%s, %s, %s, %s, %s, %s)
           """
    
        # será esperado que o cursor rodará o executador, que por sua vez executará a variavel sql que recebera os atributos a seguir
    
        #dump → significa "despejar" (to dump). 
        #O s no final vem de string.
        #Então, json.dumps = "despejar em uma string JSON".
        await cursor.execute(sql(
          pedido.nome,
          json.dumps(pedido.produto),
          pedido.quantidade,
          pedido.valor,
          json.dumps(pedido.adicionais),
          pedido.status
        ))

        await cursor.execute("SELECT LAST_INSERT_ID()")

        #cursor.fetchone() retorna uma tupla com a linha obtida (ex.: (123,)).
        pedido_id = (await cursor.fetchone())[0]
        pedido.id = pedido_id
        return JSONResponse(
            status_code = status.HTTP_201_CREATED,

            #jsonable_encoder(pedido) converte o modelo Pydantic (ou objetos complexos 
            #como datetime, UUID) para tipos JSON-compatíveis (dict, str, int, etc.).
            content = jsonable_encoder(pedido)
        )
        
    @app.get("/pedidos")
    async def retornar_pedidos():
        conn = await get_conn()
        
        #DictCursor é um cursor que retorna resultados como dicionários em vez de tuplas, tornando o acesso aos dados mais intuitivo e seguro.
        cursor = (await cursor.execute(aiomysql.DictCursor))
        
        await cursor.execute("SELECT * FROM pedidos")

        #os ressultados passados para a variável resultados após serem retornadas em um dicionário
        #serao lidos pelo metodo for r in resultados onde ele passará por todos os produto e adicionais existentes
        resultados = await cursor.fetchall()

        for r in resultados:
            #se o arquivo json encontrar valor para o produto, ent ele retornará o valor da variável, sen ele nao retornará nada
            r["produto"] = json.loads(r["produto"]) if r ["produto"] else []
            #a mesma coisa com o de cima
            r["adicionais"] = json.loads(r["adicionais"]) if r ["adicionais"] else []

        return JSONResponse(
            status_code = status.HTTP_200_OK,
            #aqui os resultados obtidos passam para uma funcao do fastapi em que trasfroma os valores obtidos em python
            #em valores que sao possiveis serem identificados pelo Json
            content = jsonable_encoder(resultados)
        )
    
    @app.get("/pedidos/{id}")
    async def retorna_pedido

