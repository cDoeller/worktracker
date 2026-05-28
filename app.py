from flask import Flask

# Flask App erstellen
app = Flask(__name__)


# Route:
# Was soll passieren wenn jemand "/" aufruft?
@app.route("/")
def home():

    return """
    <h1>WorkTracker läuft</h1>
    <p>Die lokale Web-App funktioniert.</p>
    """


# Server starten
app.run(debug=True)