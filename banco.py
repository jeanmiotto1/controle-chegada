import sqlite3

def criar_banco():
    conexao = sqlite3.connect('controle.db')
    cursor = conexao.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            data_evento TEXT NOT NULL,
            data_criacao TEXT NOT NULL
            )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS convidados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evento_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            mesa TEXT NOT NULL,
            grupo_familiar TEXT NOT NULL,
            chegou INTEGER NOT NULL DEFAULT 0,
            data_hora_chegada TEXT,
            FOREIGN KEY (evento_id) REFERENCES eventos (id)
            )
        ''')
    conexao.commit()
    conexao.close()

def criar_evento(nome, data_evento):
    conexao = sqlite3.connect('controle.db')
    cursor = conexao.cursor()
    cursor.execute('''
        INSERT INTO eventos (nome, data_evento, data_criacao)
        VALUES (?, ?, datetime('now', 'localtime'))
    ''', (nome, data_evento))
    conexao.commit()
    conexao.close()

def listar_eventos():
    conexao = sqlite3.connect('controle.db')
    cursor = conexao.cursor()
    cursor.execute('''
        SELECT id, nome, data_evento, data_criacao
        FROM eventos
        WHERE data_evento >= date('now', 'localtime')
        ORDER BY data_evento ASC
    ''')
    eventos = cursor.fetchall()
    conexao.close()
    return eventos

def buscar_evento(id_evento):
    conexao = sqlite3.connect('controle.db')
    cursor = conexao.cursor()
    cursor.execute('''
        SELECT id, nome, data_evento
        FROM eventos
        WHERE id = ?
    ''', (id_evento,))
    evento = cursor.fetchone()
    conexao.close()
    return evento

def excluir_evento(id_evento):
    conexao = sqlite3.connect('controle.db')
    cursor = conexao.cursor()
    cursor.execute('''
        DELETE FROM eventos
        WHERE id = ?
    ''', (id_evento,))
    conexao.commit()
    conexao.close()

def adicionar_convidado(evento_id, nome, mesa):
    conexao = sqlite3.connect('controle.db')
    cursor = conexao.cursor()
    cursor.execute('''
        INSERT INTO convidados (
            evento_id, 
            nome, 
            mesa, 
            grupo_familiar,
            chegou
        ) VALUES (?, ?, ?, ?, ?)
    ''', (evento_id, nome, mesa, '', 0))
    conexao.commit()
    conexao.close()

def listar_convidados(evento_id):
    conexao = sqlite3.connect('controle.db')
    cursor = conexao.cursor()
    cursor.execute('''
        SELECT id, nome, mesa, grupo_familiar, chegou, data_hora_chegada
        FROM convidados
        WHERE evento_id = ?
        ORDER BY nome
    ''', (evento_id,))
    convidados = cursor.fetchall()
    conexao.close()
    return convidados

def listar_eventos_passados():
    conexao = sqlite3.connect('controle.db')
    cursor = conexao.cursor()
    cursor.execute('''
        SELECT id, nome, data_evento, data_criacao
        FROM eventos
        WHERE data_evento < date('now', 'localtime')
        ORDER BY data_evento DESC
    ''')
    eventos = cursor.fetchall()
    conexao.close()
    return eventos


def confirmar_chegada(id_convidado):
    conexao = sqlite3.connect('controle.db')
    cursor = conexao.cursor()
    cursor.execute('''
        UPDATE convidados
        SET chegou = 1,
        data_hora_chegada = datetime('now', 'localtime')
        WHERE id = ?
    ''', (id_convidado,))
    conexao.commit()
    conexao.close()

def desmarcar_chegada(id_convidado):
    conexao = sqlite3.connect('controle.db')
    cursor = conexao.cursor()
    cursor.execute('''
        UPDATE convidados
        SET chegou = 0,
        data_hora_chegada = NULL
        WHERE id = ?
    ''', (id_convidado,))
    conexao.commit()
    conexao.close()

def excluir_convidado(id_convidado):
    conexao = sqlite3.connect('controle.db')
    cursor = conexao.cursor()
    cursor.execute('''
        DELETE FROM convidados
        WHERE id = ?
    ''', (id_convidado,))
    conexao.commit()
    conexao.close()

def evento_tem_convidados(id_evento):
    conexao = sqlite3.connect('controle.db')
    cursor = conexao.cursor()
    cursor.execute('''
        SELECT COUNT(*)
        FROM convidados
        WHERE evento_id = ?
    ''', (id_evento,))
    quantidade = cursor.fetchone()[0]
    conexao.close()
    return quantidade > 0

def evento_passado(id_evento):
    conexao = sqlite3.connect('controle.db')
    cursor = conexao.cursor()
    cursor.execute('''
        SELECT data_evento
        FROM eventos
        WHERE id = ?
    ''', (id_evento,))
    resultado = cursor.fetchone()
    conexao.close()
    if resultado is None:
        return False
    data_evento = resultado[0]
    return data_evento < __import__('datetime').datetime.now().strftime('%Y-%m-%d')

def buscar_evento_do_convidado(id_convidado):
    conexao = sqlite3.connect('controle.db')
    cursor = conexao.cursor()
    cursor.execute('''
        SELECT evento_id
        FROM convidados
        WHERE id = ?
    ''', (id_convidado,))
    resultado = cursor.fetchone()
    conexao.close()
    if resultado is None:
        return None
    return resultado[0]
