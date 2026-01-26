import os
import json
import ssl
import aiomysql
from dotenv import load_dotenv
from typing import Optional, List
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()
ssl_ctx = ssl.create_default_context()

# ============================================================
# 1️⃣ FUNÇÃO DE INICIALIZAÇÃO DO BANCO
# ============================================================

async def inicializar_banco():
    conn = await aiomysql.connect(
        host=os.getenv("SQL_HOSTNAME"),
        port=int(os.getenv("SQL_PORT")),
        user=os.getenv("SQL_USER"),
        password=os.getenv("SQL_PASSWORD"),
        autocommit=True,
        ssl=ssl_ctx
    )
    cursor = await conn.cursor()

    await cursor.execute(f"CREATE DATABASE IF NOT EXISTS {os.getenv('DB_NAME')}")
    await cursor.execute(f"USE {os.getenv('DB_NAME')}")

    await cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            produto JSON NOT NULL,
            quantidade INT NOT NULL,
            valor DECIMAL(10,2) NOT NULL,
            adicionais JSON,
            status VARCHAR(20) DEFAULT 'Pendente'
        ) AUTO_INCREMENT = 100000
    """)

    await cursor.close()
    conn.close()


# ============================================================
# 2️⃣ FUNÇÃO DE CONEXÃO AO BANCO
# ============================================================

async def get_conn():
    return await aiomysql.connect(
        host=os.getenv("SQL_HOSTNAME"),
        port=int(os.getenv("SQL_PORT")),
        user=os.getenv("SQL_USER"),
        password=os.getenv("SQL_PASSWORD"),
        db=os.getenv("DB_NAME"),
        autocommit=True,
        ssl=ssl_ctx
    )


# ============================================================
# 3️⃣ CONFIGURAÇÃO DO FASTAPI
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Inicializando Banco...")
    await inicializar_banco()
    yield


app = FastAPI(
    title="Lanchonete do Bairro",
    summary="Aplicação de registro de pedidos da loja",
    lifespan=lifespan
)


# ============================================================
# 4️⃣ MODELO DE DADOS
# ============================================================

class Pedido(BaseModel):
    id: Optional[int] = None
    nome: str
    produto: List[str]
    quantidade: int
    valor: float
    adicionais: Optional[List[str]] = None
    status: str = "Pendente"


# ============================================================
# 5️⃣ ROTAS
# ============================================================

# Criar novo pedido
@app.post("/pedidos", status_code=status.HTTP_201_CREATED)
async def criar_pedido(pedido: Pedido):
    conn = await get_conn()
    cursor = await conn.cursor()

    sql = """
        INSERT INTO pedidos (nome, produto, quantidade, valor, adicionais, status)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    await cursor.execute(sql, (
        pedido.nome,
        json.dumps(pedido.produto),
        pedido.quantidade,
        pedido.valor,
        json.dumps(pedido.adicionais),
        pedido.status
    ))

    await cursor.execute("SELECT LAST_INSERT_ID()")
    pedido.id = (await cursor.fetchone())[0]

    await cursor.close()
    conn.close()

    return JSONResponse(content=jsonable_encoder(pedido))


# Listar todos os pedidos
@app.get("/pedidos", status_code=status.HTTP_200_OK)
async def retornar_pedidos():
    conn = await get_conn()
    cursor = await conn.cursor(aiomysql.DictCursor)

    await cursor.execute("SELECT * FROM pedidos")
    resultados = await cursor.fetchall()

    for r in resultados:
        r["produto"] = json.loads(r["produto"]) if r["produto"] else []
        r["adicionais"] = json.loads(r["adicionais"]) if r["adicionais"] else []

    await cursor.close()
    conn.close()

    return JSONResponse(content=jsonable_encoder(resultados))


# Buscar pedido por ID
@app.get("/pedidos/{id}", status_code=status.HTTP_200_OK)
async def buscar_pedido(id: int):
    conn = await get_conn()
    cursor = await conn.cursor(aiomysql.DictCursor)

    await cursor.execute("SELECT * FROM pedidos WHERE id = %s", (id,))
    pedido = await cursor.fetchone()

    if not pedido:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado.")

    pedido["produto"] = json.loads(pedido["produto"]) if pedido["produto"] else []
    pedido["adicionais"] = json.loads(pedido["adicionais"]) if pedido["adicionais"] else []

    await cursor.close()
    conn.close()

    return JSONResponse(content=jsonable_encoder(pedido))


# Atualizar um pedido existente
@app.put("/pedidos/{id}", status_code=status.HTTP_200_OK)
async def atualizar_pedido(id: int, pedido: Pedido):
    conn = await get_conn()
    cursor = await conn.cursor(aiomysql.DictCursor)

    await cursor.execute("SELECT * FROM pedidos WHERE id = %s", (id,))
    existente = await cursor.fetchone()

    if not existente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado.")

    sql = """
        UPDATE pedidos
        SET nome=%s, produto=%s, quantidade=%s, valor=%s, adicionais=%s, status=%s
        WHERE id=%s
    """
    await cursor.execute(sql, (
        pedido.nome,
        json.dumps(pedido.produto),
        pedido.quantidade,
        pedido.valor,
        json.dumps(pedido.adicionais),
        pedido.status,
        id
    ))

    await cursor.close()
    conn.close()

    pedido.id = id
    return JSONResponse(content=jsonable_encoder(pedido))


# Excluir pedido
@app.delete("/pedidos/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def excluir_pedido(id: int):
    conn = await get_conn()
    cursor = await conn.cursor()

    await cursor.execute("SELECT * FROM pedidos WHERE id = %s", (id,))
    existente = await cursor.fetchone()

    if not existente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado.")

    await cursor.execute("DELETE FROM pedidos WHERE id = %s", (id,))

    await cursor.close()
    conn.close()

    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={"mensagem": "Pedido excluído com sucesso."})
