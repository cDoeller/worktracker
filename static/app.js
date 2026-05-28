async function loadEntries() {

    // Daten vom Flask API Endpoint holen
    const response = await fetch("/api/entries");

    const data = await response.json();

    const container = document.getElementById("entries");

    container.innerHTML = "";

    // jeden Eintrag rendern
    data.forEach(entry => {

        const div = document.createElement("div");
        div.className = "entry";

        div.innerHTML = `
            <strong>${entry.customer}</strong> - ${entry.project}<br>
            ${entry.description}<br>
            Dauer: ${entry.duration_seconds} Sekunden<br>
            Start: ${entry.start_time}
        `;

        container.appendChild(div);
    });
}


// beim Laden der Seite ausführen
loadEntries();