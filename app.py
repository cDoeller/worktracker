import sqlite3
import webbrowser
from flask import Flask, render_template, jsonify

app = Flask(__name__)


# ----------------------------
# HOME PAGE
# ----------------------------
@app.route("/")
def home():
    return render_template("index.html")


# ----------------------------
# API: ALLE EINTRÄGE HOLEN
# ----------------------------
@app.route("/api/entries")
def get_entries():

    conn = sqlite3.connect("tracker.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, customer, project, description, start_time, end_time, duration_seconds
        FROM entries
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    # in JSON umwandeln
    entries = []

    for row in rows:
        entries.append({
            "id": row[0],
            "customer": row[1],
            "project": row[2],
            "description": row[3],
            "start_time": row[4],
            "end_time": row[5],
            "duration_seconds": row[6],
        })

    return jsonify(entries)


# ----------------------------
# START SERVER
# ----------------------------
if __name__ == "__main__":
    # webbrowser.open("http://127.0.0.1:5000")

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )