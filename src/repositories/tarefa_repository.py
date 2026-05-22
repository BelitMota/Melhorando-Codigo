
import os
import sqlite3
from datetime import datetime

from src.models.tarefa import Tarefa, StatusTarefa
from src.config import BANCO, FORMATO_DATA, FORMATO_DATA_HORA

# ----------------------------------------------------------------------------------


# Lmbre-se ! Repository == banco
class TarefaRepository:
    def __init__(self) -> None:
        self.banco = BANCO

    def conectar(self):
        # Função para conectar no banco SQLite
        conexao = sqlite3.connect(self.banco)

        # permite acessar os resultados como DICT
        conexao.row_factory = sqlite3.Row
        return conexao

# ----------------------------------------------------------------------------------

    # Criando SEED = Semente, dados inciais para teste do sistema
    def inicializar_banco(self):
        # Cria o banco e a tabela caso ainda não existam
        conexao = self.conectar()
        cursor = conexao.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tarefas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descricao TEXT,
                usuario TEXT NOT NULL,
                status TEXT NOT NULL,
                prazo TEXT,
                criado_em TEXT NOT NULL,
                concluido_em TEXT
            )
        """)

        # Verificando se já tem dados cadastrados
        cursor.execute("SELECT COUNT(*) FROM tarefas")
        total = cursor.fetchone()[0]

        # Inserindo alguns dados iniciais para teste
        if total == 0:
            agora = datetime.now().strftime(FORMATO_DATA_HORA)

            cursor.execute("""
                INSERT INTO tarefas (titulo, descricao, usuario, status, prazo, criado_em, concluido_em)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                "Estudar Flask",
                "Revisar rotas, JSON e métodos HTTP",
                "ana",
                StatusTarefa.PENDENTE,
                "2026-05-25",
                agora,
                None
            ))

            cursor.execute("""
                INSERT INTO tarefas (titulo, descricao, usuario, status, prazo, criado_em, concluido_em)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                "Publicar API no Render",
                "Testar publicação da API em ambiente online",
                "bruno",
                StatusTarefa.PENDENTE,
                "2026-05-28",
                agora,
                None
            ))

            cursor.execute("""
                INSERT INTO tarefas (titulo, descricao, usuario, status, prazo, criado_em, concluido_em)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                "Revisar SQLite",
                "Entender comandos básicos de banco de dados",
                "ana",
                StatusTarefa.CONCLUIDA,
                "2026-05-20",
                agora,
                agora
            ))

        conexao.commit()
        conexao.close()

# ----------------------------------------------------------------------------------

    # METODO LISTAR
    def listarTodas(self, usuario:str|None=None, status:str|None=None) => list[Tarefa]:
        conexao = self.conectar()
        cursor = conexao.cursor()

        # Faz os filtros de acordo com o que foi passado
        if usuario and status:
            cursor.execute("""
                SELECT id, titulo, descricao, usuario, status, prazo, criado_em, concluido_em
                FROM tarefas
                WHERE usuario = ? AND status = ?
                ORDER BY id DESC
            """, (usuario, status))
        elif usuario:
            cursor.execute("""
                SELECT id, titulo, descricao, usuario, status, prazo, criado_em, concluido_em
                FROM tarefas
                WHERE usuario = ?
                ORDER BY id DESC
            """, (usuario,))
        elif status:
            cursor.execute("""
                SELECT id, titulo, descricao, usuario, status, prazo, criado_em, concluido_em
                FROM tarefas
                WHERE status = ?
                ORDER BY id DESC
            """, (status,))
        else:
            cursor.execute("""
                SELECT id, titulo, descricao, usuario, status, prazo, criado_em, concluido_em
                FROM tarefas
                ORDER BY id DESC
            """)

        linhas = cursor.fetchall()
        conexao.close()

        tarefas:list[Tarefa] = []

    # Monta a lista de tarefas para retornar em JSON
        for linha in linhas:
            dados = dict(linha)
            tarefa:Tarefa = Tarefa.from_dict(dados)
            tarefas.append(tarefa)

        return tarefas