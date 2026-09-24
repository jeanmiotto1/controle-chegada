from flask import Flask, render_template, request, redirect, send_file
from banco import criar_banco, criar_evento, listar_eventos, buscar_evento, excluir_evento, adicionar_convidado, listar_convidados, confirmar_chegada, desmarcar_chegada, excluir_convidado, evento_tem_convidados, listar_eventos_passados, evento_passado, buscar_evento_do_convidado
import pandas as pd
from datetime import datetime
from io import BytesIO

app = Flask(__name__)

criar_banco()

@app.route("/")
def inicio():
    eventos = listar_eventos()
    return render_template("upload.html", eventos=eventos)

@app.route("/historico")
def historico():
    eventos =listar_eventos_passados()
    return render_template("historico.html", eventos=eventos)

@app.route("/historico/<int:id_evento>/relatorio")
def baixar_relatorio(id_evento):
    evento = buscar_evento(id_evento)
    convidados = listar_convidados(id_evento)
    dados = []
    for convidado in convidados:
        dados.append({
            "Nome": convidado[1],
            "Mesa": convidado[2],
            "Chegou": "Sim" if convidado[4] == 1 else "Não",
            "Horário da chegada": convidado[5] if convidado[5] else ""
        })
    tabela = pd.DataFrame(dados)
    arquivo = BytesIO()
    with pd.ExcelWriter(arquivo, engine="openpyxl") as writer:
        tabela.to_excel(writer, index=False, sheet_name="Convidados")
    arquivo.seek(0)
    nome_arquivo = f"relatorio_{evento[1]}.xlsx"
    return send_file(
        arquivo,
        as_attachment=True,
        download_name=nome_arquivo,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.route("/novo-evento", methods=["GET", "POST"])
def novo_evento():
    if request.method == "POST":
        nome = request.form["nome_evento"]
        data_evento = request.form["data_evento"]
        criar_evento(nome, data_evento)
        print("Evento criado:", nome, data_evento)
        return redirect("/")
    return render_template("novo_evento.html")

@app.route("/evento/<int:id_evento>")
def evento(id_evento):
    mensagem = request.args.get("mensagem")
    evento = buscar_evento(id_evento)
    convidados = listar_convidados(id_evento)
    tem_convidados = evento_tem_convidados(id_evento)
    data_formatada = datetime.strptime(evento[2],"%Y-%m-%d").strftime("%d/%m/%Y")
    evento_passado = datetime.strptime(evento[2], "%Y-%m-%d").date() < datetime.now().date()
    nao_chegaram = []
    ja_chegaram = []

    for convidado in convidados:
        if convidado[4] ==0:
            nao_chegaram.append(convidado)
        else:
            ja_chegaram.append(convidado)
    return render_template(
        "evento.html",
        evento=evento,
        convidados=convidados,
        nao_chegaram=nao_chegaram,
        ja_chegaram=ja_chegaram,
        data_formatada=data_formatada,
        mensagem=mensagem,
        tem_convidados=tem_convidados,
        evento_passado=evento_passado
    )

@app.route("/confirmar-chegada/<int:id_convidado>")
def confirmar(id_convidado):
    id_evento = buscar_evento_do_convidado(id_convidado)
    if id_evento is None:
        return redirect ("/")
    if evento_passado(id_evento):
        return redirect(f"/evento/{id_evento}")
    confirmar_chegada(id_convidado)
    return redirect(request.referrer)

@app.route("/desmarcar-chegada/<int:id_convidado>")
def desmarcar(id_convidado):
    id_evento = buscar_evento_do_convidado(id_convidado)
    if id_evento is None:
        return redirect ("/")
    if evento_passado(id_evento):
        return redirect(f"/evento/{id_evento}")
    desmarcar_chegada(id_convidado)
    return redirect(request.referrer)

@app.route("/evento/<int:id_evento>/upload", methods=["GET", "POST"])
def upload_convidados(id_evento):
    evento = buscar_evento(id_evento)
    if evento_passado(id_evento):
        return redirect(f"/evento/{id_evento}")
    if request.method == "POST":
        arquivo = request.files["arquivo"]
        tabela = pd.read_excel(arquivo)
        for _, linha in tabela.iterrows():
            adicionar_convidado(
                id_evento,
                linha["Nome"],
                linha["Mesa"],
            )
        print("Convidados importados:", len(tabela))
    return render_template(
        "upload_convidados.html",
        evento=evento
    )

@app.route("/evento/<int:id_evento>/adicionar-convidado", methods=["POST"])
def adicionar_convidado_manual(id_evento):
    if evento_passado(id_evento):
        return redirect(f"/evento/{id_evento}")
    nome = request.form["nome"]
    mesa = request.form["mesa"]

    adicionar_convidado(
        id_evento,
        nome,
        mesa
    )
    return redirect(f"/evento/{id_evento}?mensagem=adicionado")

@app.route("/excluir-evento/<int:id_evento>")
def excluir(id_evento):
    excluir_evento(id_evento)
    return redirect("/")

@app.route("/excluir-convidado/<int:id_convidado>")
def excluir_convidado_rota(id_convidado):
    id_evento = buscar_evento_do_convidado(id_convidado)
    if id_evento is None:
        return redirect ("/")
    if evento_passado(id_evento):
        return redirect(f"/evento/{id_evento}")
    excluir_convidado(id_convidado)
    return redirect(request.referrer.split("?")[0] + "?mensagem=excluido")

if __name__ == "__main__":
    app.run()