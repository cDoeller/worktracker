import sqlite3
import time
from datetime import datetime

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter


# ----------------------------
# DATABASE SETUP
# ----------------------------

def init_db():

    conn = sqlite3.connect("tracker.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer TEXT,
        project TEXT,
        description TEXT,
        start_time TEXT,
        end_time TEXT,
        duration_seconds INTEGER
    )
    """)

    conn.commit()
    conn.close()


# ----------------------------
# STATE
# ----------------------------

current_entry = {
    "customer": None,
    "project": None,
    "description": None,
    "start_time": None
}

last_autosave_time = None
AUTOSAVE_INTERVAL = 300


# ----------------------------
# LOAD AUTOCOMPLETE DATA
# ----------------------------

def load_words():

    conn = sqlite3.connect("tracker.db")
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT customer FROM entries")
    customers = [r[0] for r in cursor.fetchall() if r[0]]

    cursor.execute("SELECT DISTINCT project FROM entries")
    projects = [r[0] for r in cursor.fetchall() if r[0]]

    conn.close()

    return customers, projects


# ----------------------------
# AUTOSAVE (unverändert)
# ----------------------------

def autosave():

    global current_entry

    if current_entry["start_time"] is None:
        return

    start_time = datetime.fromisoformat(current_entry["start_time"])
    now = datetime.now()

    duration = int((now - start_time).total_seconds())

    conn = sqlite3.connect("tracker.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO entries (
        customer,
        project,
        description,
        start_time,
        end_time,
        duration_seconds
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        current_entry["customer"],
        current_entry["project"],
        "AUTOSAVE",
        current_entry["start_time"],
        now.isoformat(),
        duration
    ))

    conn.commit()
    conn.close()

    print("\n💾 Autosave")


# ----------------------------
# START TRACKING (🔥 NEU MIT AUTOCOMPLETE)
# ----------------------------

def start_tracking():

    global current_entry
    global last_autosave_time

    print("\nStarte neues Tracking ...")

    customers, projects = load_words()

    # 🔥 AUTOCOMPLETE BUILDER
    customer_completer = WordCompleter(customers, ignore_case=True)
    project_completer = WordCompleter(projects, ignore_case=True)

    # ----------------------------
    # LIVE INPUT (MIT AUTOCOMPLETE)
    # ----------------------------

    customer = prompt("Kunde: ", completer=customer_completer)
    project = prompt("Projekt: ", completer=project_completer)

    now = datetime.now()

    current_entry["customer"] = customer
    current_entry["project"] = project
    current_entry["start_time"] = now.isoformat()

    last_autosave_time = now

    print(f"\n🟢 Tracking gestartet: {customer} / {project}")


# ----------------------------
# STOP TRACKING
# ----------------------------

def stop_tracking():

    global current_entry

    if current_entry["start_time"] is None:
        print("Kein aktiver Timer!")
        return

    end_time = datetime.now()
    start_time = datetime.fromisoformat(current_entry["start_time"])

    duration = (end_time - start_time).total_seconds()

    description = input("Aktivitäten: ")

    conn = sqlite3.connect("tracker.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO entries (
        customer,
        project,
        description,
        start_time,
        end_time,
        duration_seconds
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        current_entry["customer"],
        current_entry["project"],
        description,
        current_entry["start_time"],
        end_time.isoformat(),
        int(duration)
    ))

    conn.commit()
    conn.close()

    current_entry = {
        "customer": None,
        "project": None,
        "description": None,
        "start_time": None
    }

    print(f"\n✔ gespeichert: {int(duration/60)} min")


# ----------------------------
# MAIN LOOP (einfach gehalten)
# ----------------------------

def main():

    init_db()

    print("\nWorkTracker V2 (autocomplete enabled)")
    print("start | stop | exit\n")

    while True:

        cmd = input("> ").strip().lower()

        if cmd == "start":
            start_tracking()

        elif cmd == "stop":
            stop_tracking()

        elif cmd == "exit":
            break

        else:
            print("unknown command")


if __name__ == "__main__":
    main()