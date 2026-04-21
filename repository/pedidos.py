import psycopg2.extras
from datetime import datetime, timezone


def inserir_pedido(db, cliente: str, total: float) -> dict:
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM fn_inserir_pedido(%s, %s)", (cliente, total))
    return dict(cur.fetchone())


def inserir_item(db, pedido_id: int, produto: str, quantidade: int, preco: float) -> dict:
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM fn_inserir_item(%s, %s, %s, %s)", (pedido_id, produto, quantidade, preco))
    return dict(cur.fetchone())


def inserir_historico(db, pedido_id: int, status: str, alterado_por: str) -> None:
    cur = db.cursor()
    cur.execute("CALL pr_inserir_historico(%s, %s, %s, %s)", (pedido_id, status, alterado_por, datetime.now(timezone.utc)))


def buscar_pedido(db, pedido_id: int) -> dict | None:
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM fn_buscar_pedido(%s)", (pedido_id,))
    row = cur.fetchone()
    return dict(row) if row else None


def atualizar_status_pedido(db, pedido_id: int, novo_status: str) -> None:
    cur = db.cursor()
    cur.execute("CALL pr_atualizar_status_pedido(%s, %s)", (pedido_id, novo_status))


def buscar_historico(db, pedido_id: int) -> list:
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM fn_buscar_historico(%s)", (pedido_id,))
    return [dict(h) for h in cur.fetchall()]
