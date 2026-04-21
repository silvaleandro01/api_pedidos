import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)


def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NOME"),
        user=os.getenv("DB_USUARIO"),
        password=os.getenv("DB_SENHA"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORTA", 5432)),
    )


def get_db():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()
