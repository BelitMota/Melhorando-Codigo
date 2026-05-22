import os

BANCO = os.getenv("DATABASE_PATH", "tarefas.db")

FORMATO_DATA_HORA = "%Y-%m-%d %H:%:%M%S"
FORMATO_DATA = "%Y-%m-%d"
