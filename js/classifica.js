// AperiPoker - Classifica JS

async function loadClassifica() {
    const leaderboard = document.getElementById('leaderboard');
    const data = await loadData('classifica.json');

    if (!data) {
        leaderboard.innerHTML = `
            <div class="loading">
                <p>Nessun dato disponibile.</p>
                <p>Esegui il parser WhatsApp per popolare la classifica.</p>
            </div>
        `;
        return;
    }

    renderLeaderboard(data.members, 'all');
}

function renderLeaderboard(members, period) {
    const leaderboard = document.getElementById('leaderboard');

    // Filtra per periodo se necessario
    let filteredMembers = members;
    if (period !== 'all') {
        // TODO: implementare filtro per periodo
    }

    // Ordina per messaggi
    filteredMembers.sort((a, b) => b.messageCount - a.messageCount);

    leaderboard.innerHTML = filteredMembers.map((member, index) => {
        const rank = index + 1;
        let rankClass = '';
        if (rank === 1) rankClass = 'top-1';
        else if (rank === 2) rankClass = 'top-2';
        else if (rank === 3) rankClass = 'top-3';

        const medal = rank === 1 ? '🥇' : rank === 2 ? '🥈' : rank === 3 ? '🥉' : rank;

        return `
            <div class="leaderboard-item ${rankClass}">
                <span class="rank">${medal}</span>
                <span class="member-name">${member.name}</span>
                <span class="message-count">${formatNumber(member.messageCount)} messaggi</span>
            </div>
        `;
    }).join('');
}

// Gestione filtro periodo
document.getElementById('period-select')?.addEventListener('change', (e) => {
    // TODO: ricaricare con filtro
    console.log('Periodo selezionato:', e.target.value);
});

// Init
document.addEventListener('DOMContentLoaded', loadClassifica);
