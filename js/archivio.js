// AperiPoker - Archivio JS

let yearsData = [];

async function loadArchivio() {
    const grid = document.getElementById('archivio-grid');

    // Carica overview anni
    const overview = await loadData('anni-overview.json');

    if (!overview || !overview.years || overview.years.length === 0) {
        grid.innerHTML = `
            <div class="loading">
                <p>Archivio non disponibile.</p>
                <p>Esegui il parser WhatsApp per generare i dati storici.</p>
            </div>
        `;
        return;
    }

    yearsData = overview.years;

    // Calcola totali
    const totalMessages = yearsData.reduce((sum, y) => sum + y.totalMessages, 0);
    const peakYear = yearsData.reduce((max, y) => y.totalMessages > max.totalMessages ? y : max);
    const mvpCounts = {};
    yearsData.forEach(y => {
        const mvpName = y.mvp.split(' ')[0];  // Solo nome
        mvpCounts[mvpName] = (mvpCounts[mvpName] || 0) + 1;
    });
    const allTimeMvp = Object.entries(mvpCounts).reduce((max, [name, count]) =>
        count > max.count ? {name, count} : max, {name: '', count: 0}
    );

    // Aggiorna stats totali
    document.getElementById('total-messages-all').textContent = formatNumber(totalMessages);
    document.getElementById('total-years').textContent = yearsData.length;
    document.getElementById('peak-year').textContent = peakYear.year;
    document.getElementById('all-time-mvp').textContent = allTimeMvp.name;

    // Render grafico trend
    renderYearlyTrend();

    // Render cards
    renderYearCards();
}

function renderYearlyTrend() {
    const container = document.getElementById('yearly-trend-chart');
    if (!container) return;

    const maxMessages = Math.max(...yearsData.map(y => y.totalMessages));

    container.innerHTML = yearsData.map(y => {
        const heightPercent = (y.totalMessages / maxMessages) * 100;
        const isCurrent = y.year === 2026;

        return `
            <div class="bar-vertical">
                <div class="bar-vertical-fill"
                     style="height: ${heightPercent}%; ${isCurrent ? 'background: linear-gradient(0deg, var(--secondary), #f1c40f);' : ''}">
                </div>
                <span class="bar-vertical-label">${y.year}</span>
            </div>
        `;
    }).join('');
}

function renderYearCards() {
    const grid = document.getElementById('archivio-grid');

    // Ordina dal più recente
    const sortedYears = [...yearsData].sort((a, b) => b.year - a.year);

    grid.innerHTML = sortedYears.map(y => {
        const isCurrent = y.year === 2026;
        const trendClass = y.trend > 0 ? 'positive' : y.trend < 0 ? 'negative' : '';
        const trendStr = y.trend ?
            `${y.trend > 0 ? '+' : ''}${y.trend}%` : '-';

        return `
            <div class="archivio-card ${isCurrent ? 'current' : ''}" onclick="viewYear(${y.year})">
                <div class="archivio-card-header">
                    <div class="archivio-card-year">${y.year}</div>
                    ${isCurrent ? '<span class="archivio-card-badge">In corso</span>' : ''}
                </div>
                <div class="archivio-card-body">
                    <div class="archivio-stat">
                        <span class="archivio-stat-label">Messaggi</span>
                        <span class="archivio-stat-value">${formatNumber(y.totalMessages)}</span>
                    </div>
                    <div class="archivio-stat">
                        <span class="archivio-stat-label">MVP</span>
                        <span class="archivio-stat-value">${y.mvp.split(' ')[0]}</span>
                    </div>
                    <div class="archivio-stat">
                        <span class="archivio-stat-label">Trend</span>
                        <span class="archivio-stat-value archivio-trend ${trendClass}">${trendStr}</span>
                    </div>
                    ${y.highlights ? `<p class="archivio-highlight">${y.highlights}</p>` : ''}
                </div>
            </div>
        `;
    }).join('');
}

function viewYear(year) {
    // Naviga alla pagina classifica con anno selezionato
    // Oppure mostra un modal con dettagli anno
    window.location.href = `classifica.html?anno=${year}`;
}

// Init
document.addEventListener('DOMContentLoaded', loadArchivio);
