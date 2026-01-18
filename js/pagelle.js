// AperiPoker - Pagelle JS

let currentWeekIndex = 0;
let weeksData = [];

async function loadPagelle() {
    const grid = document.getElementById('pagelle-grid');
    const data = await loadData('pagelle.json');

    if (!data || !data.weeks || data.weeks.length === 0) {
        grid.innerHTML = `
            <div class="loading">
                <p>Nessuna pagella disponibile.</p>
                <p>Esegui l'agente pagelle per generare i contenuti.</p>
            </div>
        `;
        return;
    }

    weeksData = data.weeks;
    currentWeekIndex = weeksData.length - 1; // Ultima settimana
    renderCurrentWeek();
}

function renderCurrentWeek() {
    const grid = document.getElementById('pagelle-grid');
    const weekLabel = document.getElementById('current-week');
    const summary = document.getElementById('week-summary');

    const week = weeksData[currentWeekIndex];
    weekLabel.textContent = `Settimana del ${formatDate(week.startDate)}`;

    // Render pagelle
    grid.innerHTML = week.pagelle.map(p => {
        const votoClass = p.voto >= 7 ? 'voto-alto' : p.voto >= 5 ? 'voto-medio' : 'voto-basso';

        return `
            <div class="pagella-card">
                <div class="pagella-header">
                    <span class="pagella-name">${p.name}</span>
                    <span class="pagella-voto ${votoClass}">${p.voto}</span>
                </div>
                <div class="pagella-content">
                    <p class="pagella-giudizio">"${p.giudizio}"</p>
                    <p class="pagella-stats">
                        ${p.messaggi} messaggi | ${p.mediaGiornaliera} msg/giorno
                    </p>
                </div>
            </div>
        `;
    }).join('');

    // Render riassunto
    if (week.riassunto) {
        summary.querySelector('.summary-content').innerHTML = `<p>${week.riassunto}</p>`;
    }

    // Aggiorna bottoni
    document.getElementById('prev-week').disabled = currentWeekIndex === 0;
    document.getElementById('next-week').disabled = currentWeekIndex === weeksData.length - 1;
}

// Navigazione settimane
document.getElementById('prev-week')?.addEventListener('click', () => {
    if (currentWeekIndex > 0) {
        currentWeekIndex--;
        renderCurrentWeek();
    }
});

document.getElementById('next-week')?.addEventListener('click', () => {
    if (currentWeekIndex < weeksData.length - 1) {
        currentWeekIndex++;
        renderCurrentWeek();
    }
});

// Init
document.addEventListener('DOMContentLoaded', loadPagelle);
