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