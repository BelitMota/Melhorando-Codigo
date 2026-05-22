import os
import sqlite3
from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

from src.config import BANCO
from src.repositories.tarefa_repository import TarefaRepository

# ||| INICIO DA PARTE DO BANCO DE DADOS |||

# Nome do arquivo do banco
# BANCO = "tarefas.db"

def conectar():
    # Função para conectar no banco SQLite
    conexao = sqlite3.connect(BANCO)
    return conexao


def inicializar_banco():
    # Cria o banco e a tabela caso ainda não existam
    conexao = conectar()
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

    
# ||| INICIO DA PARTE DAS ROTAS |||

@app.get("/")
def inicio():
    # Rota inicial só para testar se a API está funcionando
    return jsonify({
        "mensagem": "API de tarefas funcionando"
    })


@app.get("/tarefas")
def listar_tarefas():
    # Pega os filtros da URL
    # exemplo: /tarefas?usuario=yuri&status=pendente
    usuario = request.args.get("usuario")
    status = request.args.get("status")

    repo:TarefaRepository = TarefaRepository()
    return repo.listarTodas(usuario=usuario,status=status)


@app.get("/tarefas/<int:tarefa_id>")
def buscar_tarefa(tarefa_id):
    # Busca uma tarefa pelo ID
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, titulo, descricao, usuario, status, prazo, criado_em, concluido_em
        FROM tarefas
        WHERE id = ?
    """, (tarefa_id,))

    linha = cursor.fetchone()
    conexao.close()

    if linha is None:
        return jsonify({
            "erro": "Tarefa não encontrada"
        }), 404

    tarefa = {
        "id": linha[0],
        "titulo": linha[1],
        "descricao": linha[2],
        "usuario": linha[3],
        "status": linha[4],
        "prazo": linha[5],
        "criado_em": linha[6],
        "concluido_em": linha[7]
    }

    return jsonify(tarefa)


@app.post("/tarefas")
def criar_tarefa():
    # Pega os dados enviados no corpo da requisição
    dados = request.get_json()

    if dados is None:
        return jsonify({
            "erro": "Envie os dados em JSON"
        }), 400

    titulo = dados.get("titulo")
    descricao = dados.get("descricao")
    usuario = dados.get("usuario")
    prazo = dados.get("prazo")

    # Validações básicas
    if titulo is None or titulo.strip() == "":
        return jsonify({
            "erro": "O título é obrigatório"
        }), 400

    if usuario is None or usuario.strip() == "":
        return jsonify({
            "erro": "O usuário é obrigatório"
        }), 400

    # Toda tarefa começa como pendente
    status = "PENDENTE"

    criado_em = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO tarefas (titulo, descricao, usuario, status, prazo, criado_em, concluido_em)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        titulo,
        descricao,
        usuario,
        status,
        prazo,
        criado_em,
        None
    ))

    conexao.commit()

    tarefa_id = cursor.lastrowid

    conexao.close()

    return jsonify({
        "mensagem": "Tarefa criada com sucesso",
        "tarefa": {
            "id": tarefa_id,
            "titulo": titulo,
            "descricao": descricao,
            "usuario": usuario,
            "status": status,
            "prazo": prazo,
            "criado_em": criado_em,
            "concluido_em": None
        }
    }), 201


@app.put("/tarefas/<int:tarefa_id>")
def atualizar_tarefa(tarefa_id):
    # Atualiza todos os dados de uma tarefa
    dados = request.get_json()

    if dados is None:
        return jsonify({
            "erro": "Envie os dados em JSON"
        }), 400

    conexao = conectar()
    cursor = conexao.cursor()

    # Verifica se a tarefa existe
    cursor.execute("""
        SELECT id, titulo, descricao, usuario, status, prazo, criado_em, concluido_em
        FROM tarefas
        WHERE id = ?
    """, (tarefa_id,))

    linha = cursor.fetchone()

    if linha is None:
        conexao.close()
        return jsonify({
            "erro": "Tarefa não encontrada"
        }), 404

    titulo = dados.get("titulo")
    descricao = dados.get("descricao")
    usuario = dados.get("usuario")
    status = dados.get("status")
    prazo = dados.get("prazo")

    # Valida os campos principais
    if titulo is None or titulo.strip() == "":
        conexao.close()
        return jsonify({
            "erro": "O título é obrigatório"
        }), 400

    if usuario is None or usuario.strip() == "":
        conexao.close()
        return jsonify({
            "erro": "O usuário é obrigatório"
        }), 400

    if status is None or status.strip() == "":
        conexao.close()
        return jsonify({
            "erro": "O status é obrigatório"
        }), 400

    # Status aceitos no sistema
    if status != "PENDENTE" and status != "EM_ANDAMENTO" and status != "CONCLUIDA" and status != "CANCELADA":
        conexao.close()
        return jsonify({
            "erro": "Status inválido"
        }), 400

    concluido_em = linha[7]

    # Se concluir, salva a data de conclusão
    if status == "CONCLUIDA":
        concluido_em = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        concluido_em = None

    cursor.execute("""
        UPDATE tarefas
        SET titulo = ?, descricao = ?, usuario = ?, status = ?, prazo = ?, concluido_em = ?
        WHERE id = ?
    """, (
        titulo,
        descricao,
        usuario,
        status,
        prazo,
        concluido_em,
        tarefa_id
    ))

    conexao.commit()
    conexao.close()

    return jsonify({
        "mensagem": "Tarefa atualizada com sucesso",
        "tarefa": {
            "id": tarefa_id,
            "titulo": titulo,
            "descricao": descricao,
            "usuario": usuario,
            "status": status,
            "prazo": prazo,
            "concluido_em": concluido_em
        }
    })


@app.patch("/tarefas/<int:tarefa_id>")
def atualizar_parcialmente_tarefa(tarefa_id):
    # Atualiza somente os campos enviados
    dados = request.get_json()

    if dados is None:
        return jsonify({
            "erro": "Envie os dados em JSON"
        }), 400

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, titulo, descricao, usuario, status, prazo, criado_em, concluido_em
        FROM tarefas
        WHERE id = ?
    """, (tarefa_id,))

    linha = cursor.fetchone()

    if linha is None:
        conexao.close()
        return jsonify({
            "erro": "Tarefa não encontrada"
        }), 404

    # Dados atuais
    titulo = linha[1]
    descricao = linha[2]
    usuario = linha[3]
    status = linha[4]
    prazo = linha[5]
    concluido_em = linha[7]

    # Altera apenas o que veio no JSON
    if "titulo" in dados:
        if dados.get("titulo") is None or dados.get("titulo").strip() == "":
            conexao.close()
            return jsonify({
                "erro": "O título não pode ficar vazio"
            }), 400

        titulo = dados.get("titulo")

    if "descricao" in dados:
        descricao = dados.get("descricao")

    if "usuario" in dados:
        if dados.get("usuario") is None or dados.get("usuario").strip() == "":
            conexao.close()
            return jsonify({
                "erro": "O usuário não pode ficar vazio"
            }), 400

        usuario = dados.get("usuario")

    if "prazo" in dados:
        prazo = dados.get("prazo")

    if "status" in dados:
        novo_status = dados.get("status")

        if novo_status != "PENDENTE" and novo_status != "EM_ANDAMENTO" and novo_status != "CONCLUIDA" and novo_status != "CANCELADA":
            conexao.close()
            return jsonify({
                "erro": "Status inválido"
            }), 400

        status = novo_status

        if status == "CONCLUIDA":
            concluido_em = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            concluido_em = None

    cursor.execute("""
        UPDATE tarefas
        SET titulo = ?, descricao = ?, usuario = ?, status = ?, prazo = ?, concluido_em = ?
        WHERE id = ?
    """, (
        titulo,
        descricao,
        usuario,
        status,
        prazo,
        concluido_em,
        tarefa_id
    ))

    conexao.commit()
    conexao.close()

    return jsonify({
        "mensagem": "Tarefa atualizada",
        "id": tarefa_id,
        "titulo": titulo,
        "descricao": descricao,
        "usuario": usuario,
        "status": status,
        "prazo": prazo,
        "concluido_em": concluido_em
    })


@app.patch("/tarefas/<int:tarefa_id>/concluir")
def concluir_tarefa(tarefa_id):
    # Marca uma tarefa como concluída
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, titulo, descricao, usuario, status, prazo, criado_em, concluido_em
        FROM tarefas
        WHERE id = ?
    """, (tarefa_id,))

    linha = cursor.fetchone()

    if linha is None:
        conexao.close()
        return jsonify({
            "erro": "Tarefa não encontrada"
        }), 404

    status_atual = linha[4]

    # Não deixa concluir se estiver cancelada
    if status_atual == "CANCELADA":
        conexao.close()
        return jsonify({
            "erro": "Tarefa cancelada não pode ser concluída"
        }), 400

    concluido_em = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        UPDATE tarefas
        SET status = ?, concluido_em = ?
        WHERE id = ?
    """, (
        "CONCLUIDA",
        concluido_em,
        tarefa_id
    ))

    conexao.commit()
    conexao.close()

    return jsonify({
        "mensagem": "Tarefa concluída",
        "id": tarefa_id,
        "status": "CONCLUIDA",
        "concluido_em": concluido_em
    })


@app.patch("/tarefas/<int:tarefa_id>/cancelar")
def cancelar_tarefa(tarefa_id):
    # Cancela uma tarefa
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, titulo, descricao, usuario, status, prazo, criado_em, concluido_em
        FROM tarefas
        WHERE id = ?
    """, (tarefa_id,))

    linha = cursor.fetchone()

    if linha is None:
        conexao.close()
        return jsonify({
            "erro": "Tarefa não encontrada"
        }), 404

    status_atual = linha[4]

    # Não deixa cancelar tarefa concluída
    if status_atual == "CONCLUIDA":
        conexao.close()
        return jsonify({
            "erro": "Tarefa concluída não pode ser cancelada"
        }), 400

    cursor.execute("""
        UPDATE tarefas
        SET status = ?, concluido_em = ?
        WHERE id = ?
    """, (
        "CANCELADA",
        None,
        tarefa_id
    ))

    conexao.commit()
    conexao.close()

    return jsonify({
        "mensagem": "Tarefa cancelada",
        "id": tarefa_id,
        "status": "CANCELADA"
    })


@app.delete("/tarefas/<int:tarefa_id>")
def excluir_tarefa(tarefa_id):
    # Exclui uma tarefa pelo ID
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, titulo, descricao, usuario, status, prazo, criado_em, concluido_em
        FROM tarefas
        WHERE id = ?
    """, (tarefa_id,))

    linha = cursor.fetchone()

    if linha is None:
        conexao.close()
        return jsonify({
            "erro": "Tarefa não encontrada"
        }), 404

    cursor.execute("""
        DELETE FROM tarefas
        WHERE id = ?
    """, (tarefa_id,))

    conexao.commit()
    conexao.close()

    return jsonify({
        "mensagem": "Tarefa excluída",
        "id": tarefa_id
    })


@app.get("/relatorio")
def relatorio():
    # Relatório geral das tarefas
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("SELECT COUNT(*) FROM tarefas")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tarefas WHERE status = 'PENDENTE'")
    pendentes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tarefas WHERE status = 'EM_ANDAMENTO'")
    em_andamento = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tarefas WHERE status = 'CONCLUIDA'")
    concluidas = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tarefas WHERE status = 'CANCELADA'")
    canceladas = cursor.fetchone()[0]

    conexao.close()

    return jsonify({
        "total": total,
        "pendentes": pendentes,
        "em_andamento": em_andamento,
        "concluidas": concluidas,
        "canceladas": canceladas
    })


@app.get("/relatorio/usuarios")
def relatorio_por_usuario():
    # Relatório agrupado por usuário
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT usuario, COUNT(*) as total
        FROM tarefas
        GROUP BY usuario
        ORDER BY total DESC
    """)

    linhas = cursor.fetchall()
    conexao.close()

    usuarios = []

    for linha in linhas:
        usuarios.append({
            "usuario": linha[0],
            "total_tarefas": linha[1]
        })

    return jsonify({
        "usuarios": usuarios
    })


@app.get("/tarefas-atrasadas")
def tarefas_atrasadas():
    # Lista tarefas atrasadas
    hoje = datetime.now().strftime("%Y-%m-%d")

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, titulo, descricao, usuario, status, prazo, criado_em, concluido_em
        FROM tarefas
        WHERE prazo < ?
        AND status != 'CONCLUIDA'
        AND status != 'CANCELADA'
        ORDER BY prazo ASC
    """, (hoje,))

    linhas = cursor.fetchall()
    conexao.close()

    tarefas = []

    for linha in linhas:
        tarefas.append({
            "id": linha[0],
            "titulo": linha[1],
            "descricao": linha[2],
            "usuario": linha[3],
            "status": linha[4],
            "prazo": linha[5],
            "criado_em": linha[6],
            "concluido_em": linha[7]
        })

    return jsonify({
        "data_referencia": hoje,
        "total": len(tarefas),
        "tarefas_atrasadas": tarefas
    })


@app.post("/resetar")
def resetar():
    # Reseta o banco para facilitar os testes
    if os.path.exists(BANCO):
        os.remove(BANCO)

    inicializar_banco()

    return jsonify({
        "mensagem": "Banco resetado"
    })


# Inicializa o banco e sobe a aplicação
if __name__ == "__main__":
    inicializar_banco()
    app.run(debug=True)