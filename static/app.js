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

    // falls invalid
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

    // initial render
    applyFilter();
}


// ----------------------------
// FILTER FUNKTION (ZENTRAL)
// ----------------------------
function getFilteredData() {

    const value = document.getElementById("search").value.toLowerCase();

    const hideAutosave = document.getElementById("hideAutosave")?.checked;

    return allEntries.filter(e => {

        // AUTOSAVE toggle
        if (hideAutosave && e.description === "AUTOSAVE") {
            return false;
        }

        // nur Kunde + Projekt Filter
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
    // TOTALS PRO PROJEKT
    // ----------------------------
    const projectTotals = {};

    data.forEach(entry => {

        const project = entry.project || "unknown";

        const duration = entry.duration_seconds || 0;

        if (!projectTotals[project]) {
            projectTotals[project] = 0;
        }

        projectTotals[project] += duration;
    });


    // ----------------------------
    // ZEILEN BAUEN
    // ----------------------------
    data.forEach(entry => {

        const project = entry.project || "unknown";

        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${entry.customer || ""}</td>
            <td>${project}</td>
            <td>${entry.description || ""}</td>
            <td>${formatDateTime(entry.start_time) || ""}</td>
            <td>${formatDuration(entry.duration_seconds)}</td>
            <td>${formatDuration(projectTotals[project])}</td>
        `;

        tbody.appendChild(row);
    });
}


// ----------------------------
// APPLY FILTER (RENDER PIPELINE)
// ----------------------------
function applyFilter() {

    const filtered = getFilteredData();

    renderTable(filtered);
}


// ----------------------------
// EVENT LISTENER
// ----------------------------

// Text input
document.getElementById("search")
    .addEventListener("input", applyFilter);

// Checkbox toggle
document.getElementById("hideAutosave")
    .addEventListener("change", applyFilter);


// ----------------------------
// INIT
// ----------------------------
loadEntries();