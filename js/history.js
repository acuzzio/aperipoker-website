// AperiPoker - History JS

async function loadHistory() {
    const data = await loadData('history.json');

    if (!data) {
        document.getElementById('timeline').querySelector('.timeline-container').innerHTML = `
            <div class="loading">
                <p>Storia non ancora disponibile.</p>
                <p>Esegui l'agente history per generare i contenuti.</p>
            </div>
        `;
        return;
    }

    // Stats generali
    document.getElementById('years-active').textContent = data.yearsActive || '-';
    document.getElementById('total-messages-ever').textContent = formatNumber(data.totalMessages) || '-';
    document.getElementById('founding-date').textContent = data.foundingDate || '-';
    document.getElementById('founder').textContent = data.founder || '-';

    // Timeline
    renderTimeline(data.timeline || []);

    // Yearly recap
    renderYearlyRecap(data.yearlyStats || {});

    // Evolution narrative
    if (data.evolutionNarrative) {
        document.getElementById('evolution-content').innerHTML = `<p>${data.evolutionNarrative}</p>`;
    }
}

function renderTimeline(events) {
    const container = document.getElementById('timeline').querySelector('.timeline-container');

    if (events.length === 0) {
        container.innerHTML = '<p class="loading">Nessun evento nella timeline.</p>';
        return;
    }

    container.innerHTML = events.map(event => `
        <div class="timeline-event">
            <div class="event-date">${event.date}</div>
            <div class="event-content">
                <h3>${event.title}</h3>
                <p>${event.description}</p>
            </div>
        </div>
    `).join('');
}

function renderYearlyRecap(yearlyStats) {
    const container = document.getElementById('yearly-recap').querySelector('.years-grid');

    const years = Object.keys(yearlyStats).sort((a, b) => b - a);

    if (years.length === 0) {
        container.innerHTML = '<p class="loading">Statistiche annuali non disponibili.</p>';
        return;
    }

    container.innerHTML = years.map(year => {
        const stats = yearlyStats[year];
        return `
            <div class="year-card">
                <h3>${year}</h3>
                <div class="year-stats">
                    <p><strong>${formatNumber(stats.messages)}</strong> messaggi</p>
                    <p><strong>${stats.activeMembers}</strong> membri attivi</p>
                    <p>MVP: <strong>${stats.mvp || '-'}</strong></p>
                    ${stats.highlight ? `<p class="highlight">"${stats.highlight}"</p>` : ''}
                </div>
            </div>
        `;
    }).join('');
}

// Init
document.addEventListener('DOMContentLoaded', loadHistory);
