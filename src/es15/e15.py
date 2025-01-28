import json
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
)
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = "your-secret-key-here"  # Change this to a secure secret key


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="x",
        database="ciaramidaro_hotel",
    )


@app.route("/raw")
def list_entries_raw():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM CAMERA")
    entries = cursor.fetchall()
    cursor.close()
    conn.close()
    return entries

@app.route("/")
def list_entries():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM CAMERA")
    entries = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("list.html", entries=entries)

@app.route("/free")
def list_free():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM CAMERA WHERE disponibile = %s", (1,))  # Modificato per usare i parametri corretti
    entries = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("free_list.html", entries=entries)  # Assicurati di avere il template corretto

@app.route("/add", methods=("GET", "POST"))
def add_entries():
    if request.method == "POST":
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # TODO controllo che non esista già una camera 
        # con lo stesso numero
        numero = request.form["numero"]
        tipo = request.form["tipo"]
        disponibile = bool(request.form["disponibile"])
        prezzo = request.form["prezzo"]
        numero_posti = request.form["numero_posti"]

        # Create room
        cursor.execute(
            "INSERT INTO CAMERA (numero, tipo, disponibile, prezzo, numero_posti) VALUES (%s, %s, %s, %s, %s)",
            (numero, tipo, disponibile, prezzo, numero_posti),
        )
        conn.commit()    
        cursor.close()
        conn.close()
        return redirect(url_for("list_entries"))
    return render_template("add.html")

@app.route("/prenotation_room", methods=("GET", "POST"))
def prenotation():
    return render_template("new_prenotation.html")
@app.route("/prenotating", methods=("GET", "POST"))
def prenotation_room():
    if request.method == "POST":
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        data_arrivo = request.form["arrivo"]
        data_partenza = request.form["partenza"]
        nome_cliente = request.form["cliente"]
        numero = request.form["numero"]

    # Passa i parametri come una tupla con una virgola
    cursor.execute("SELECT disponibile FROM CAMERA WHERE numero = %s", (numero,))
    result = cursor.fetchone()
    disponibile = result['disponibile'] if result else 0

    if disponibile == 1:
        cursor.execute(
            "INSERT INTO PRENOTAZIONE (numero, data_arrivo, data_partenza, nome_cliente) VALUES (%s, %s, %s, %s)",
            (numero, data_arrivo, data_partenza, nome_cliente)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return "<h1>Prenotazione Fatta!</h1>"
    else:
        cursor.close()
        conn.close()
        return "<h1>Camera non disponibile</h1>"

@app.route("/prenotations")
def list_prenotations():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM PRENOTAZIONE")
    entries = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("list_prenotations.html", entries=entries)



if __name__ == "__main__":


    app.run(debug=True, port=5678)
