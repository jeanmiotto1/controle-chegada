import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')


def conectar():
    return psycopg2.connect(DATABASE_URL)


def criar_banco():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS eventos (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            data_evento TEXT NOT NULL,
            data_criacao TIMESTAMP NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS convidados (
            id SERIAL PRIMARY KEY,
            evento_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            mesa TEXT NOT NULL,
            grupo_familiar TEXT NOT NULL,
            chegou INTEGER NOT NULL DEFAULT 0,
            data_hora_chegada TIMESTAMP,
            FOREIGN KEY (evento_id) REFERENCES eventos (id)
        )
    ''')

    conexao.commit()
    conexao.close()


def criar_evento(nome, data_evento):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute('''
        INSERT INTO eventos (nome, data_evento, data_criacao)
        VALUES (%s, %s, CURRENT_TIMESTAMP)
    ''', (nome, data_evento))

    conexao.commit()
    conexao.close()


def listar_eventos():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute('''
        SELECT id, nome, data_evento, data_criacao
        FROM eventos
        WHERE data_evento >= CURRENT_DATE::text
        ORDER BY data_evento ASC
    ''')

    eventos = cursor.fetchall()
    conexao.close()

    return eventos


def buscar_evento(id_evento):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute('''
        SELECT id, nome, data_evento
        FROM eventos
        WHERE id = %s
    ''', (id_evento,))

    evento = cursor.fetchone()
    conexao.close()

    return evento


def excluir_evento(id_evento):
    conexao = conectar()
    cursor = conexao.cursor()

    try:
        cursor.execute('''
            DELETE FROM convidados
            WHERE evento_id = %s
        ''', (id_evento,))

        cursor.execute('''
            DELETE FROM eventos
            WHERE id = %s
        ''', (id_evento,))

        conexao.commit()

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()


def adicionar_convidado(evento_id, nome, mesa):
    conexao = conectar()
    cursor = conexao.cursor()

    try:
        cursor.execute('''
            INSERT INTO convidados (
                evento_id,
                nome,
                mesa,
                grupo_familiar,
                chegou
            )
            VALUES (%s, %s, %s, %s, %s)
        ''', (evento_id, nome, mesa, '', 0))

        conexao.commit()

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()


def importar_convidados(evento_id, convidados):
    conexao = conectar()
    cursor = conexao.cursor()

    try:
        dados = [
            (evento_id, nome, mesa, '', 0)
            for nome, mesa in convidados
        ]

        cursor.executemany('''
            INSERT INTO convidados (
                evento_id,
                nome,
                mesa,
                grupo_familiar,
                chegou
            )
            VALUES (%s, %s, %s, %s, %s)
        ''', dados)

        conexao.commit()

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()


def listar_convidados(evento_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute('''
        SELECT id, nome, mesa, grupo_familiar, chegou, data_hora_chegada
        FROM convidados
        WHERE evento_id = %s
        ORDER BY nome
    ''', (evento_id,))

    convidados = cursor.fetchall()
    conexao.close()

    return convidados


def listar_eventos_passados():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute('''
        SELECT id, nome, data_evento, data_criacao
        FROM eventos
        WHERE data_evento < CURRENT_DATE::text
        ORDER BY data_evento DESC
    ''')

    eventos = cursor.fetchall()
    conexao.close()

    return eventos


def confirmar_chegada(id_convidado):
    conexao = conectar()
    cursor = conexao.cursor()

    try:
        cursor.execute('''
            UPDATE convidados
            SET chegou = 1,
                data_hora_chegada =
                    CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo'
            WHERE id = %s
        ''', (id_convidado,))

        conexao.commit()

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()


def desmarcar_chegada(id_convidado):
    conexao = conectar()
    cursor = conexao.cursor()

    try:
        cursor.execute('''
            UPDATE convidados
            SET chegou = 0,
                data_hora_chegada = NULL
            WHERE id = %s
        ''', (id_convidado,))

        conexao.commit()

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()


def excluir_convidado(id_convidado):
    conexao = conectar()
    cursor = conexao.cursor()

    try:
        cursor.execute('''
            DELETE FROM convidados
            WHERE id = %s
        ''', (id_convidado,))

        conexao.commit()

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()


def evento_tem_convidados(id_evento):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute('''
        SELECT COUNT(*)
        FROM convidados
        WHERE evento_id = %s
    ''', (id_evento,))

    quantidade = cursor.fetchone()[0]
    conexao.close()

    return quantidade > 0


def evento_passado(id_evento):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute('''
        SELECT data_evento
        FROM eventos
        WHERE id = %s
    ''', (id_evento,))

    resultado = cursor.fetchone()
    conexao.close()

    if resultado is None:
        return False

    data_evento = resultado[0]

    return data_evento < __import__('datetime').datetime.now().strftime('%Y-%m-%d')


def buscar_evento_do_convidado(id_convidado):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute('''
        SELECT evento_id
        FROM convidados
        WHERE id = %s
    ''', (id_convidado,))

    resultado = cursor.fetchone()
    conexao.close()

    if resultado is None:
        return None

    return resultado[0]