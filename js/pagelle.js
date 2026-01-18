// AperiPoker - Pagelle JS

let currentYear = '2026';
let currentWeekIndex = 0;
let pagelleData = null;

async function loadPagelle() {
    // Controlla se c'è un anno nell'URL
    const urlParams = new URLSearchParams(window.location.search);
    const yearParam = urlParams.get('anno');
    if (yearParam) {
        currentYear = yearParam;
        document.getElementById('pagelle-year-select').value = yearParam;
    }

    await loadYearPagelle(currentYear);
}

async function loadYearPagelle(year) {
    const grid = document.getElementById('pagelle-grid');
    const cumulativeGrid = document.getElementById('cumulative-grid');
    currentYear = year;

    // Aggiorna labels
    document.getElementById('cumulative-year-label').textContent = year;
    document.getElementById('year-summary-label').textContent = year;

    // Carica dati pagelle per l'anno
    pagelleData = await loadData(`pagelle/${year}.json`);

    // Fallback a pagelle.json per 2026 se il file per anno non esiste
    if (!pagelleData && year === '2026') {
        pagelleData = await loadData('pagelle.json');
        if (pagelleData) {
            // Converti vecchio formato
            pagelleData = {
                year: 2026,
                weeks: pagelleData.weeks || [],
                cumulative: [],
                totalWeeks: pagelleData.weeks?.length || 0,
            };
        }
    }

    if (!pagelleData || !pagelleData.weeks || pagelleData.weeks.length === 0) {
        grid.innerHTML = `
            <div class="loading">
                <p>Nessuna pagella disponibile per ${year}.</p>
                <p>Esegui il parser WhatsApp per generare i dati.</p>
            </div>
        `;
        cumulativeGrid.innerHTML = '<div class="loading">Nessun dato disponibile.</div>';
        updateYearSummary(null);
        return;
    }

    // Render classifica cumulativa
    renderCumulativeStats(pagelleData.cumulative);

    // Render year summary
    updateYearSummary(pagelleData);

    // Seleziona ultima settimana
    currentWeekIndex = pagelleData.weeks.length - 1;
    renderCurrentWeek();
}

function renderCumulativeStats(cumulative) {
    const grid = document.getElementById('cumulative-grid');

    if (!cumulative || cumulative.length === 0) {
        // Calcola da weeks se cumulative non esiste
        grid.innerHTML = '<div class="loading">Statistiche cumulative non disponibili.</div>';
        return;
    }

    grid.innerHTML = cumulative.map((member, index) => {
        const rank = index + 1;
        let medalClass = '';
        let medal = rank;
        if (rank === 1) { medalClass = 'gold'; medal = '🥇'; }
        else if (rank === 2) { medalClass = 'silver'; medal = '🥈'; }
        else if (rank === 3) { medalClass = 'bronze'; medal = '🥉'; }

        const votoClass = member.mediaVoto >= 7 ? 'voto-alto' : member.mediaVoto >= 6 ? 'voto-medio' : 'voto-basso';
        const firstName = member.name.split(' ')[0];
        const signatureHtml = member.signature
            ? `<span class="cumulative-signature">${member.signature}</span>`
            : '';

        return `
            <div class="cumulative-card ${medalClass}">
                <div class="cumulative-rank">${medal}</div>
                <div class="cumulative-info">
                    <span class="cumulative-name">${firstName}</span>
                    <span class="cumulative-details">
                        ${member.settimaneAttive} settimane · ${formatNumber(member.totalMessaggi)} msg
                    </span>
                    ${signatureHtml}
                </div>
                <div class="cumulative-voto ${votoClass}">${member.mediaVoto.toFixed(1)}</div>
                <div class="cumulative-range">
                    <span class="voto-best" title="Miglior voto">▲ ${member.bestVoto}</span>
                    <span class="voto-worst" title="Peggior voto">▼ ${member.worstVoto}</span>
                </div>
            </div>
        `;
    }).join('');
}

function updateYearSummary(data) {
    if (!data) {
        document.getElementById('year-total-weeks').textContent = '-';
        document.getElementById('year-best-performer').textContent = '-';
        document.getElementById('year-highest-voto').textContent = '-';
        return;
    }

    document.getElementById('year-total-weeks').textContent = data.totalWeeks || data.weeks.length;

    // Best performer
    if (data.cumulative && data.cumulative.length > 0) {
        const best = data.cumulative[0];
        document.getElementById('year-best-performer').textContent =
            `${best.name.split(' ')[0]} (${best.mediaVoto.toFixed(1)})`;
    } else {
        document.getElementById('year-best-performer').textContent = '-';
    }

    // Highest single voto
    let highestVoto = 0;
    let highestName = '';
    for (const week of data.weeks) {
        for (const p of week.pagelle) {
            if (p.voto > highestVoto) {
                highestVoto = p.voto;
                highestName = p.name.split(' ')[0];
            }
        }
    }
    document.getElementById('year-highest-voto').textContent =
        highestVoto > 0 ? `${highestVoto} (${highestName})` : '-';
}

function renderCurrentWeek() {
    const grid = document.getElementById('pagelle-grid');
    const weekLabel = document.getElementById('current-week');
    const summary = document.getElementById('week-summary');

    if (!pagelleData || !pagelleData.weeks || pagelleData.weeks.length === 0) {
        grid.innerHTML = '<div class="loading">Nessuna settimana disponibile.</div>';
        return;
    }

    const week = pagelleData.weeks[currentWeekIndex];
    weekLabel.textContent = `Settimana del ${formatDate(week.startDate)}`;

    // Update mini stats
    if (week.stats) {
        document.getElementById('week-total-msgs').textContent = formatNumber(week.stats.totalMessages);
        document.getElementById('week-active-members').textContent = week.stats.activeMembers;
        document.getElementById('week-avg-per-member').textContent = week.stats.avgPerMember?.toFixed(1) || '-';
    }

    // Render pagelle
    grid.innerHTML = week.pagelle.map(p => {
        const votoClass = p.voto >= 7 ? 'voto-alto' : p.voto >= 5 ? 'voto-medio' : 'voto-basso';
        const highlightsHtml = p.highlights && p.highlights.length > 0
            ? `<div class="pagella-highlights">${p.highlights.map(h => `<span class="highlight-tag">${h}</span>`).join('')}</div>`
            : '';

        return `
            <div class="pagella-card">
                <div class="pagella-header">
                    <span class="pagella-name">${p.name}</span>
                    <span class="pagella-voto ${votoClass}">${p.voto}</span>
                </div>
                <div class="pagella-content">
                    <p class="pagella-giudizio">"${p.giudizio}"</p>
                    ${highlightsHtml}
                    <p class="pagella-stats">
                        ${p.messaggi} messaggi | ${p.mediaGiornaliera} msg/giorno
                    </p>
                </div>
            </div>
        `;
    }).join('');

    // Render riassunto con citazioni
    let summaryHtml = `<p>${week.riassunto}</p>`;
    if (week.bestQuotes && week.bestQuotes.length > 0) {
        summaryHtml += `
            <div class="week-quotes">
                <h4>Citazioni della settimana</h4>
                ${week.bestQuotes.map(q => `
                    <blockquote class="week-quote">
                        <p>"${q.quote}"</p>
                        <cite>— ${q.author.split(' ')[0]}</cite>
                    </blockquote>
                `).join('')}
            </div>
        `;
    }
    summary.querySelector('.summary-content').innerHTML = summaryHtml;

    // Aggiorna bottoni
    document.getElementById('prev-week').disabled = currentWeekIndex === 0;
    document.getElementById('next-week').disabled = currentWeekIndex === pagelleData.weeks.length - 1;
}

// Gestione selezione anno
document.getElementById('pagelle-year-select')?.addEventListener('change', (e) => {
    loadYearPagelle(e.target.value);

    // Aggiorna URL senza ricaricare
    const url = new URL(window.location);
    if (e.target.value === '2026') {
        url.searchParams.delete('anno');
    } else {
        url.searchParams.set('anno', e.target.value);
    }
    window.history.replaceState({}, '', url);
});

// Navigazione settimane
document.getElementById('prev-week')?.addEventListener('click', () => {
    if (currentWeekIndex > 0) {
        currentWeekIndex--;
        renderCurrentWeek();
    }
});

document.getElementById('next-week')?.addEventListener('click', () => {
    if (pagelleData && currentWeekIndex < pagelleData.weeks.length - 1) {
        currentWeekIndex++;
        renderCurrentWeek();
    }
});

// Init
document.addEventListener('DOMContentLoaded', loadPagelle);
