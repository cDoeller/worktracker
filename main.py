import sqlite3
import sys
import select
import time

from datetime import datetime


# ----------------------------
# DATABASE SETUP
# ----------------------------

def init_db():
    """
    Erstellt die SQLite Verbindung und Tabelle,
    falls sie noch nicht existiert.
    """

    # Verbindung zur SQLite Datei herstellen
    # Falls tracker.db noch nicht existiert:
    # -> wird sie automatisch erstellt
    conn = sqlite3.connect("tracker.db")

    # Cursor = Objekt um SQL Befehle auszuführen
    cursor = conn.cursor()

    # Tabelle erstellen falls sie noch nicht existiert
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

    # Änderungen speichern
    conn.commit()

    # Verbindung schließen
    conn.close()


# ----------------------------
# STATE (läuft nur im Speicher)
# ----------------------------

# Hier speichern wir den aktuellen laufenden Timer
# Das ist quasi unser "RAM State"
current_entry = {
    "customer": None,
    "project": None,
    "description": None,
    "start_time": None
}


# ----------------------------
# TIMER / AUTOSAVE STATE
# ----------------------------

# Hier speichern wir wann zuletzt automatisch gespeichert wurde
# Das brauchen wir für das Arduino millis()-Prinzip
last_autosave_time = None

# Wie oft automatisch gespeichert werden soll
# 300 Sekunden = 5 Minuten
AUTOSAVE_INTERVAL = 300


# ----------------------------
# NON BLOCKING INPUT
# ----------------------------

def get_input_non_blocking():
    """
    Prüft ob im Terminal bereits Input vorhanden ist.

    WICHTIG:
    Normales input() blockiert das komplette Programm.
    Dann könnte unser Timer NICHT weiterlaufen.

    Deshalb nutzen wir select():
    - prüft ob Daten im stdin Buffer liegen
    - falls ja -> lesen wir sie
    - falls nein -> None zurückgeben

    Dadurch kann unsere Main Loop permanent weiterlaufen.
    """

    # select prüft:
    # "Liegt Input im Terminal bereit?"
    #
    # timeout = 0
    # -> sofort zurückkehren
    #
    # [0] enthält die Liste der verfügbaren Inputs
    if select.select([sys.stdin], [], [], 0)[0]:

        # readline liest die komplette Zeile
        # strip entfernt \n und Leerzeichen
        return sys.stdin.readline().strip()

    return None


# ----------------------------
# AUTOSAVE FUNCTION
# ----------------------------

def autosave():
    """
    Führt einen automatischen Zwischen-Save aus.

    WICHTIG:
    Hier wird NICHT der finale Eintrag gespeichert.
    Wir schreiben nur die aktuelle Dauer in die DB.

    So verlieren wir bei Crash / Terminal schließen
    nicht die komplette Session.
    """

    global current_entry

    # Wenn kein aktiver Timer läuft:
    # -> nichts tun
    if current_entry["start_time"] is None:
        return

    # Startzeit zurück in datetime konvertieren
    start_time = datetime.fromisoformat(
        current_entry["start_time"]
    )

    # Aktuelle Zeit holen
    now = datetime.now()

    # Dauer berechnen
    duration = int(
        (now - start_time).total_seconds()
    )

    # Verbindung öffnen
    conn = sqlite3.connect("tracker.db")
    cursor = conn.cursor()

    # WICHTIG:
    # Wir speichern einen temporären Zwischenstand
    #
    # description = AUTOSAVE
    # end_time = aktuelle Zeit
    #
    # Dadurch haben wir IMMER einen aktuellen Stand
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

    print("\n💾 Autosave ausgeführt")


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
    global last_autosave_time

    print("\nStarte neues Tracking ...")

    customer = input("Kunde: ")
    project = input("Projekt: ")

    # Aktuelle Zeit holen
    now = datetime.now()

    # ISO Format:
    # sehr gut speicherbar in SQLite
    start_time = now.isoformat()

    # Werte im RAM speichern
    current_entry["customer"] = customer
    current_entry["project"] = project
    current_entry["start_time"] = start_time

    # Zeitpunkt des letzten Autosaves setzen
    #
    # WICHTIG:
    # Damit startet unser "millis timer"
    last_autosave_time = now

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
    Speichert alles final in SQLite.
    """

    global current_entry

    # Wenn kein Timer aktiv:
    if current_entry["start_time"] is None:
        print("Kein aktiver Timer!")
        return

    # Endzeit holen
    end_time = datetime.now()

    print(f"\n🔴 Tracking gestoppt um {end_time}")

    # Startzeit zurück in datetime konvertieren
    start_time = datetime.fromisoformat(
        current_entry["start_time"]
    )

    # Dauer berechnen
    duration = (
        end_time - start_time
    ).total_seconds()

    # Beschreibung abfragen
    description = input("Aktivitäten: ")

    # Verbindung öffnen
    conn = sqlite3.connect("tracker.db")
    cursor = conn.cursor()

    # FINALEN Eintrag speichern
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

    # State zurücksetzen
    #
    # WICHTIG:
    # Damit weiß das Programm:
    # -> kein Timer läuft mehr
    current_entry = {
        "customer": None,
        "project": None,
        "description": None,
        "start_time": None
    }

    print(
        f"\nTracking gespeichert! "
        f"Dauer: {int(duration)/60:.2f} Minuten\n"
    )


# ----------------------------
# MAIN LOOP (CLI)
# ----------------------------

def main():
    """
    Haupt-Loop der App.

    WICHTIG:
    Das ist jetzt KEIN blockierendes input() System mehr.

    Stattdessen:
    - Loop läuft permanent
    - prüft Input
    - prüft Autosave Timer
    - schläft kurz
    - repeat

    Genau wie Arduino millis().
    """

    global last_autosave_time

    init_db()

    print("\nWorkTracker V1.0")
    print("Befehle: start | stop | exit\n")

    # Endlos Loop
    while True:

        # ----------------------------
        # INPUT CHECK
        # ----------------------------

        # Prüfen ob User etwas eingegeben hat
        command = get_input_non_blocking()

        # Falls Input vorhanden:
        if command:

            # alles lowercase machen
            command = command.strip().lower()

            if command == "start":
                start_tracking()

            elif command == "stop":
                stop_tracking()

                print(
                    "Befehle: start | stop | exit\n"
                )

            elif command == "exit":
                print("WorkTracker beendet.")
                break

            else:
                print(
                    "Unbekannter Befehl. "
                    "Nutze: start | stop | exit"
                )

        # ----------------------------
        # AUTOSAVE CHECK
        # ----------------------------

        # Nur prüfen wenn Tracking aktiv ist
        if current_entry["start_time"] is not None:

            # aktuelle Zeit holen
            now = datetime.now()

            # Sekunden seit letztem Autosave berechnen
            elapsed = (
                now - last_autosave_time
            ).total_seconds()

            # Arduino millis()-Prinzip:
            #
            # Wenn genug Zeit vergangen:
            # -> autosave ausführen
            if elapsed >= AUTOSAVE_INTERVAL:

                autosave()

                # Timer zurücksetzen
                last_autosave_time = now

        # ----------------------------
        # CPU SCHONEN
        # ----------------------------

        # Ohne sleep würde der Loop
        # tausende Male pro Sekunde laufen
        #
        # 0.1 = 100ms
        #
        # Reagiert immer noch instant,
        # spart aber massiv CPU
        time.sleep(0.1)


# ----------------------------
# ENTRY POINT
# ----------------------------

if __name__ == "__main__":
    main()