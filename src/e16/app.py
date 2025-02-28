import json
import sqlite3
from flask import Flask, g, jsonify, render_template
import os


app = Flask(__name__)
app.secret_key = "your-secret-key-here"

with open("config.json") as config_file:
    config = json.load(config_file)
    DATABASE = config["DATABASE"]
    INITIALIZATION = config["INITIALIZATION"]


def get_db():
    """Connessione al database"""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


def init_db():
    """Inizializza il database"""
    with app.app_context():
        db = get_db()
        # Load schema from queries folder
        with app.open_resource(INITIALIZATION) as f:
            db.executescript(f.read().decode("utf8"))
        db.commit()


@app.teardown_appcontext
def close_db(error):
    """Chiude la connessione al database"""
    if hasattr(g, "db"):
        g.db.close()

@app.route("/raw_giocatori")
def raw_giocatori():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM GIOCATORE")
    entries = cursor.fetchall()
    cursor.close()
    return jsonify([dict(row) for row in entries])

@app.route("/")  # Add default route
@app.route("/giocatori")
def giocatori():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT g.*, a.nome as allenatore_nome, a.cognome as allenatore_cognome 
        FROM GIOCATORE g 
        LEFT JOIN ALLENATORE a ON g.allenatore_id = a.id
    """)
    entries = cursor.fetchall()
    cursor.close()
    return render_template("giocatori.html", entries=entries)



@app.route("/allenatori")
def allenatori():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT * FROM ALLENATORE
    """)
    entries = cursor.fetchall()
    cursor.close()
    return render_template("allenatori.html", entries=entries)


@app.route("/partite")
def partite():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT p.id, p.data, 
               g.id as giocatore_id, g.nome, g.cognome, gp.ha_segnato
        FROM PARTITA p
        LEFT JOIN GIOCATORE_PARTITA gp ON p.id = gp.partita_id
        LEFT JOIN GIOCATORE g ON gp.giocatore_id = g.id
    """)
    rows = cursor.fetchall()
    cursor.close()

    partite_dict = {}
    for row in rows:
        partita_id = row['id']
        if partita_id not in partite_dict:
            partite_dict[partita_id] = {
                'id': partita_id,
                'data': row['data'],
                'giocatori': []
            }
        partite_dict[partita_id]['giocatori'].append({
            'id': row['giocatore_id'],
            'nome': row['nome'],
            'cognome': row['cognome'],
            'ha_segnato': row['ha_segnato']
        })

    entries = list(partite_dict.values())
    return render_template("partite.html", entries=entries)

if __name__ == "__main__":
    # check if the file database exists
    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True, port=50840)
