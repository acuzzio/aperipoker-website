// AperiPoker - Classifica JS

let currentYear = '2026';
let classificaData = null;
let yearData = null;

async function loadClassifica() {
    const leaderboard = document.getElementById('leaderboard');

    // Controlla se c'è un anno nell'URL
    const urlParams = new URLSearchParams(window.location.search);
    const yearParam = urlParams.get('anno');
    if (yearParam) {
        currentYear = yearParam;
        document.getElementById('year-select').value = yearParam;
    }

    await loadYearData(currentYear);
}

async function loadYearData(year) {
    const leaderboard = document.getElementById('leaderboard');
    currentYear = year;

    if (year === 'all') {
        // Carica classifica generale
        classificaData = await loadData('classifica.json');
        yearData = await loadData('stats.json');

        // Aggiorna stats con dati aggregati
        document.getElementById('year-title').textContent = 'Tutti gli anni';
        document.getElementById('year-messages').textContent = classificaData ? formatNumber(
            classificaData.members.reduce((sum, m) => sum + m.messageCount, 0)
        ) : '-';
        document.getElementById('year-members').textContent = classificaData?.members?.length || '-';
        document.getElementById('year-mvp').textContent = classificaData?.members?.[0]?.name?.split(' ')[0] || '-';
        document.getElementById('year-trend').textContent = '-';
    } else {
        // Carica dati anno specifico
        yearData = await loadData(`anni/${year}.json`);

        if (!yearData) {
            // Fallback a classifica.json per 2026
            if (year === '2026') {
                classificaData = await loadData('classifica.json');
                yearData = await loadData('stats.json');
                if (classificaData) {
                    yearData = {
                        stats: {
                            totalMessages: classificaData.members.reduce((sum, m) => sum + m.messageCount, 0),
                            totalMembers: classificaData.members.length,
                            mvp: classificaData.members[0]?.name,
                            trend: null
                        },
                        classifica: classificaData.members,
                        hourlyActivity: classificaData.hourlyTotal,
                        dailyActivity: classificaData.dailyTotal
                    };
                }
            }
        }

        if (!yearData) {
            leaderboard.innerHTML = `
                <div class="loading">
                    <p>Nessun dato disponibile per ${year}.</p>
                    <p>Esegui il parser WhatsApp per popolare i dati.</p>
                </div>
            `;
            return;
        }

        // Aggiorna stats
        document.getElementById('year-title').textContent = year === '2026' ? '2026 (in corso)' : year;
        document.getElementById('year-messages').textContent = formatNumber(yearData.stats?.totalMessages || 0);
        document.getElementById('year-members').textContent = yearData.stats?.totalMembers || '-';
        document.getElementById('year-mvp').textContent = (yearData.stats?.mvp || '-').split(' ')[0];

        const trend = yearData.stats?.trend;
        const trendEl = document.getElementById('year-trend');
        if (trend !== null && trend !== undefined) {
            trendEl.textContent = `${trend > 0 ? '+' : ''}${trend}%`;
            trendEl.style.color = trend > 0 ? 'var(--success)' : trend < 0 ? 'var(--danger)' : 'inherit';
        } else {
            trendEl.textContent = '-';
            trendEl.style.color = 'inherit';
        }
    }

    // Render classifica
    const members = yearData?.classifica || classificaData?.members || [];
    renderLeaderboard(members);

    // Render grafici
    renderHourlyChart(yearData?.hourlyActivity || classificaData?.hourlyTotal);
    renderDailyChart(yearData?.dailyActivity || classificaData?.dailyTotal);
}

function renderLeaderboard(members) {
    const leaderboard = document.getElementById('leaderboard');

    if (!members || members.length === 0) {
        leaderboard.innerHTML = '<div class="loading">Nessun dato disponibile.</div>';
        return;
    }

    // Ordina per messaggi
    const sorted = [...members].sort((a, b) => b.messageCount - a.messageCount);
    const maxMessages = sorted[0]?.messageCount || 1;

    leaderboard.innerHTML = sorted.map((member, index) => {
        const rank = index + 1;
        let rankClass = '';
        let barClass = '';
        if (rank === 1) { rankClass = 'top-1'; barClass = 'gold'; }
        else if (rank === 2) { rankClass = 'top-2'; barClass = 'silver'; }
        else if (rank === 3) { rankClass = 'top-3'; barClass = 'bronze'; }

        const medal = rank === 1 ? '🥇' : rank === 2 ? '🥈' : rank === 3 ? '🥉' : rank;
        const barWidth = (member.messageCount / maxMessages) * 100;

        return `
            <div class="leaderboard-item ${rankClass}">
                <span class="rank">${medal}</span>
                <div class="leaderboard-bar-wrapper">
                    <span class="member-name">${member.name}</span>
                    <div class="leaderboard-bar">
                        <div class="leaderboard-bar-fill ${barClass}" style="width: ${barWidth}%"></div>
                    </div>
                </div>
                <span class="message-count">${formatNumber(member.messageCount)}</span>
            </div>
        `;
    }).join('');
}

function renderHourlyChart(hourlyData) {
    const container = document.getElementById('hourly-chart');
    if (!container || !hourlyData) {
        if (container) container.innerHTML = '<div class="loading">Dati non disponibili</div>';
        return;
    }

    // Prepara dati per tutte le 24 ore
    const hours = [];
    let maxValue = 0;
    for (let i = 0; i < 24; i++) {
        const value = hourlyData[i] || 0;
        hours.push({ hour: i, value });
        if (value > maxValue) maxValue = value;
    }

    container.innerHTML = hours.map(h => {
        const heightPercent = maxValue > 0 ? (h.value / maxValue) * 100 : 0;
        return `
            <div class="bar-vertical">
                <div class="bar-vertical-fill" style="height: ${heightPercent}%"></div>
                <span class="bar-vertical-label">${h.hour}</span>
            </div>
        `;
    }).join('');
}

function renderDailyChart(dailyData) {
    const container = document.getElementById('daily-chart');
    if (!container || !dailyData) {
        if (container) container.innerHTML = '<div class="loading">Dati non disponibili</div>';
        return;
    }

    const dayNames = ['Lun', 'Mar', 'Mer', 'Gio', 'Ven', 'Sab', 'Dom'];

    // Prepara dati per tutti i 7 giorni
    const days = [];
    let maxValue = 0;
    for (let i = 0; i < 7; i++) {
        const value = dailyData[i] || 0;
        days.push({ day: i, name: dayNames[i], value });
        if (value > maxValue) maxValue = value;
    }

    container.innerHTML = days.map(d => {
        const heightPercent = maxValue > 0 ? (d.value / maxValue) * 100 : 0;
        return `
            <div class="weekday-bar">
                <div class="weekday-bar-container">
                    <div class="weekday-bar-fill" style="height: ${heightPercent}%"></div>
                </div>
                <span class="weekday-label">${d.name}</span>
                <span class="weekday-value">${formatNumber(d.value)}</span>
            </div>
        `;
    }).join('');
}

// Gestione selezione anno
document.getElementById('year-select')?.addEventListener('change', (e) => {
    loadYearData(e.target.value);

    // Aggiorna URL senza ricaricare
    const url = new URL(window.location);
    if (e.target.value === '2026') {
        url.searchParams.delete('anno');
    } else {
        url.searchParams.set('anno', e.target.value);
    }
    window.history.replaceState({}, '', url);
});

// Init
document.addEventListener('DOMContentLoaded', loadClassifica);
