let allEntries = [];

// ----------------------------
// ZEITFORMATIERUNG
// ----------------------------

function formatDuration(seconds) {

    if (!seconds || seconds <= 0) return "0 min";

    const totalMinutes = Math.floor(seconds / 60);

    // unter 1 Stunde → nur Minuten
    if (totalMinutes < 60) {
        return `${totalMinutes} min`;
    }

    // Stunden + Restminuten
    const hours = Math.floor(totalMinutes / 60);
    const minutes = totalMinutes % 60;

    return `${hours}.${String(minutes).padStart(2, "0")} h`;
}


// ----------------------------
// DATUM FORMATIERUNG
// ----------------------------

function formatDateTime(isoString) {

    if (!isoString) return "";

    const date = new Date(isoString);

    if (isNaN(date.getTime())) return isoString;

    const day = String(date.getDate()).padStart(2, "0");
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const year = date.getFullYear();

    return `${day}.${month}.${year}`;
}


// ----------------------------
// DATEN LADEN
// ----------------------------

async function loadEntries() {

    const response = await fetch("/api/entries");

    allEntries = await response.json();

    applyFilter();
}


// ----------------------------
// FILTER FUNKTION
// ----------------------------

function getFilteredData() {

    const value = document.getElementById("search").value.toLowerCase();

    const hideAutosave = document.getElementById("hideAutosave")?.checked;

    return allEntries.filter(e => {

        if (hideAutosave && e.description === "AUTOSAVE") {
            return false;
        }

        return (
            (e.customer || "").toLowerCase().includes(value) ||
            (e.project || "").toLowerCase().includes(value)
        );
    });
}


// ----------------------------
// TABELLE RENDER
// ----------------------------

function renderTable(data) {

    const tbody = document.getElementById("table-body");

    tbody.innerHTML = "";

    // ----------------------------
    // TOTALS: customer + project (FIX)
    // ----------------------------

    const totals = {};

    data.forEach(entry => {

        const customer = entry.customer || "unknown";
        const project = entry.project || "unknown";

        // 🔥 WICHTIG: COMPOSITE KEY
        const key = customer + "||" + project;

        const duration = entry.duration_seconds || 0;

        if (!totals[key]) {
            totals[key] = 0;
        }

        totals[key] += duration;
    });


    // ----------------------------
    // ZEILEN BAUEN
    // ----------------------------

    data.forEach(entry => {

        const customer = entry.customer || "unknown";
        const project = entry.project || "unknown";

        const key = customer + "||" + project;

        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${customer}</td>
            <td>${project}</td>
            <td>${entry.description || ""}</td>
            <td>${formatDateTime(entry.start_time)}</td>
            <td>${formatDuration(entry.duration_seconds)}</td>
            <td>${formatDuration(totals[key])}</td>
        `;

        tbody.appendChild(row);
    });
}


// ----------------------------
// APPLY FILTER
// ----------------------------

function applyFilter() {

    const filtered = getFilteredData();

    renderTable(filtered);
}


// ----------------------------
// EVENTS
// ----------------------------

document.getElementById("search")
    .addEventListener("input", applyFilter);

document.getElementById("hideAutosave")
    .addEventListener("change", applyFilter);


// ----------------------------
// INIT
// ----------------------------

loadEntries();