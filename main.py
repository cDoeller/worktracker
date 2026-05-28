import sqlite3
from datetime import datetime

# ----------------------------
# DATABASE SETUP
# ----------------------------

def init_db():
    """
    Erstellt die SQLite Verbindung und Tabelle,
    falls sie noch nicht existiert.
    """
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
# STATE (läuft nur im Speicher)
# ----------------------------

# Hier speichern wir den aktuellen laufenden Timer
current_entry = {
    "customer": None,
    "project": None,
    "description": None,
    "start_time": None
}


# ----------------------------
# START FUNCTION
# ----------------------------

def start_tracking():
    """
    Startet eine neue Zeiterfassung.
    Fragt Benutzer nach Kunde + Projekt.
    Speichert Startzeit im RAM.
    """

    global current_entry

    print("\nStarte neues Tracking ...")

    customer = input("Kunde: ")
    project = input("Projekt: ")

    # Startzeit im ISO Format (gut speicherbar)
    start_time = datetime.now().isoformat()

    # In Memory speichern
    current_entry["customer"] = customer
    current_entry["project"] = project
    current_entry["start_time"] = start_time

    print(f"\n🟢 Tracking gestartet um {start_time}")
    print("Tippe 'stop' um zu beenden.\n")


# ----------------------------
# STOP FUNCTION
# ----------------------------

def stop_tracking():
    """
    Beendet aktuelle Zeiterfassung.
    Fragt Beschreibung ab.
    Berechnet Dauer.
    Speichert alles in SQLite.
    """

    global current_entry

    if current_entry["start_time"] is None:
        print("Kein aktiver Timer!")
        return

    end_time = datetime.now()

    print(f"\n🔴 Tracking gestoppt um {end_time}")

    # Startzeit zurück in datetime konvertieren
    start_time = datetime.fromisoformat(current_entry["start_time"])

    # Dauer berechnen in Sekunden
    duration = (end_time - start_time).total_seconds()

    description = input("Aktivitäten: ")

    # In DB speichern
    conn = sqlite3.connect("tracker.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO entries (customer, project, description, start_time, end_time, duration_seconds)
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

    # Reset (wichtig!)
    current_entry = {
        "customer": None,
        "project": None,
        "description": None,
        "start_time": None
    }

    print(f"\nTracking gespeichert! Dauer: {int(duration)/60} Minuten\n")


# ----------------------------
# MAIN LOOP (CLI)
# ----------------------------

def main():
    """
    Einfache Kommando-Schleife:
    - start → startet Timer
    - stop → beendet Timer
    - exit → beendet Programm
    """

    init_db()

    print("\nWorkTracker V1.0")
    print("Befehle: start | stop | exit\n")

    while True:
        command = input("> ").strip().lower()

        if command == "start":
            start_tracking()

        elif command == "stop":
            stop_tracking()
            print("Befehle: start | stop | exit\n")

        elif command == "exit":
            print("WorkTracker beendet.")
            break

        else:
            print("Unbekannter Befehl. Nutze: start | stop | exit")


# ----------------------------
# ENTRY POINT
# ----------------------------

if __name__ == "__main__":
    main()