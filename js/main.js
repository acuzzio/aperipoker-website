// AperiPoker - Main JS

// Utility per caricare dati JSON
async function loadData(filename) {
    try {
        const response = await fetch(`../data/${filename}`);
        if (!response.ok) {
            // Prova senza ../ per la homepage
            const response2 = await fetch(`data/${filename}`);
            if (!response2.ok) throw new Error('File non trovato');
            return await response2.json();
        }
        return await response.json();
    } catch (error) {
        console.log(`Dati non ancora disponibili: ${filename}`);
        return null;
    }
}

// Formatta numeri grandi
function formatNumber(num) {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
}

// Formatta data
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('it-IT', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
    });
}

// Carica statistiche rapide nella homepage
async function loadQuickStats() {
    const statsSection = document.getElementById('quick-stats');
    if (!statsSection) return;

    const stats = await loadData('stats.json');
    if (!stats) {
        document.getElementById('total-messages').textContent = '?';
        document.getElementById('total-members').textContent = '?';
        document.getElementById('most-active').textContent = '?';
        document.getElementById('last-update').textContent = 'Mai';
        return;
    }

    document.getElementById('total-messages').textContent = formatNumber(stats.totalMessages);
    document.getElementById('total-members').textContent = stats.totalMembers;
    document.getElementById('most-active').textContent = stats.mostActive;
    document.getElementById('last-update').textContent = formatDate(stats.lastUpdate);
}

// Init
document.addEventListener('DOMContentLoaded', () => {
    loadQuickStats();
});
