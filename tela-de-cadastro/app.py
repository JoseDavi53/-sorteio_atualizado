from flask import Flask, jsonify, render_template, request
import mysql.connector
from escpos.printer import Win32Raw
import time

app = Flask(__name__)

# 🔌 conexão com banco
def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="cadastro_integrador"
    )

# 🖨️ impressão térmica
def imprimir_termica(id, nome, sobrenome, tipo):
    try:
        p = Win32Raw("ELGIN i8 USB")
        p.hw('INIT')

        p.text("\n\n")

        p.set(align='center', bold=True, width=2, height=2)
        p.text("EMPRESA XYZ\n")

        p.set(align='center')
        p.text("Sistema de Cadastro\n")
        p.text("------------------------------\n")

        p.text(time.strftime("%d/%m/%Y %H:%M") + "\n")
        p.text("------------------------------\n")

        p.set(align='center', bold=True, width=1, height=2)
        p.text("\nCADASTRO REALIZADO\n\n")

        p.set(align='center', bold=True, width=3, height=3)
        p.text(f"{id}\n\n")

        p.set(align='center')
        p.text("Guarde seu numero\npara o sorteio\n\n")

        p.text("------------------------------\n")

        p.set(align='left')
        p.text(f"Nome : {nome} {sobrenome}\n")
        p.text(f"Tipo : {tipo}\n")

        p.text("------------------------------\n")

        p.set(align='center')
        p.text("\nObrigado pela visita!\n")
        p.text("Boa sorte!\n")

        p.text("\n\n\n\n\n\n")
        p.cut()

    except Exception as e:
        print("Erro:", e)


# 🏠 página inicial
@app.route("/")
def index():
    return render_template("index.html")


# 🎰 página do sorteio (ESSA FALTAVA)
@app.route("/realizar-sorteio")
def realizar_sorteio():
    return render_template("sorteio.html")


# 💾 salvar + imprimir
@app.route("/salvar", methods=["POST"])
def salvar():
    try:
        primeiro_nome = request.form["primeiro_nome"]
        sobrenome = request.form["sobrenome"]
        data_nascimento = request.form["data_nascimento"]
        tipo_usuario = request.form["tipo_usuario"]

        conn = conectar()
        cursor = conn.cursor()

        sql = """
            INSERT INTO usuarios 
            (primeiro_nome, sobrenome, tipo_usuario, data_nascimento) 
            VALUES (%s, %s, %s, %s)
        """

        valores = (primeiro_nome, sobrenome, tipo_usuario, data_nascimento)

        cursor.execute(sql, valores)
        conn.commit()

        sorteio_id = cursor.lastrowid

        cursor.close()
        conn.close()

        imprimir_termica(sorteio_id, primeiro_nome, sobrenome, tipo_usuario)

        return render_template("sucesso.html", numero_sorteio=sorteio_id)

    except Exception as e:
        return f"Erro ao salvar: {e}"


# 🎲 API sorteio
@app.route("/api/sortear")
def api_sortear():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id, primeiro_nome, sobrenome FROM usuarios ORDER BY RAND() LIMIT 1")
    ganhador = cursor.fetchone()

    cursor.close()
    conn.close()

    return jsonify(ganhador)


# 🚀 iniciar servidor
if __name__ == "__main__":
    app.run(debug=True)
