// AperiPoker - Best Of JS

let allMoments = [];
let yearMoments = {};  // Momenti caricati da file per anno
let currentCategory = 'all';
let currentYear = 'all';

async function loadBestOf() {
    const list = document.getElementById('best-of-list');

    // Carica best-of.json principale (2026)
    const data = await loadData('best-of.json');

    if (data && data.moments) {
        allMoments = data.moments;
        // Associa anno ai momenti esistenti (dal campo date)
        allMoments.forEach(m => {
            if (m.date) {
                m.year = parseInt(m.date.substring(0, 4));
            }
        });
    }

    // Carica anche i best-of dagli anni (se disponibili)
    await loadYearBestOfs();

    if (allMoments.length === 0) {
        list.innerHTML = `
            <div class="loading">
                <p>Nessun momento epico registrato.</p>
                <p>Esegui l'agente best-of per scoprire i momenti migliori.</p>
            </div>
        `;
        return;
    }

    renderMoments();
    renderHallOfFame(data?.hallOfFame || allMoments.slice(0, 3));
}

async function loadYearBestOfs() {
    // Prova a caricare best-of da ogni anno
    const years = [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026];

    for (const year of years) {
        try {
            const yearData = await loadData(`anni/${year}.json`);
            if (yearData && yearData.bestOf) {
                yearMoments[year] = yearData.bestOf.map(b => ({
                    ...b,
                    year: year,
                    date: b.date || `${year}-01-01`,
                    category: b.category || 'momenti'
                }));

                // Aggiungi ai momenti totali se non già presenti
                yearMoments[year].forEach(ym => {
                    if (!allMoments.find(m => m.quote === ym.quote)) {
                        allMoments.push(ym);
                    }
                });
            }
        } catch (e) {
            // File anno non trovato, ignora
        }
    }
}

function filterMoments() {
    let filtered = allMoments;

    // Filtra per anno
    if (currentYear !== 'all') {
        const yearNum = parseInt(currentYear);
        filtered = filtered.filter(m => m.year === yearNum);
    }

    // Filtra per categoria
    if (currentCategory !== 'all') {
        filtered = filtered.filter(m => m.category === currentCategory);
    }

    return filtered;
}

function renderMoments() {
    const list = document.getElementById('best-of-list');
    const filtered = filterMoments();

    if (filtered.length === 0) {
        list.innerHTML = `<div class="loading">Nessun momento trovato con questi filtri.</div>`;
        return;
    }

    // Ordina per data (più recenti prima)
    filtered.sort((a, b) => (b.date || '').localeCompare(a.date || ''));

    list.innerHTML = filtered.map(m => `
        <div class="best-of-item">
            <p class="quote">"${m.quote}"</p>
            <p>
                <span class="author">— ${m.author}</span>
                ${m.date ? `<span class="date">${formatDate(m.date)}</span>` : ''}
            </p>
            ${m.context ? `<p class="best-of-context" style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.5rem;">${m.context}</p>` : ''}
            <span class="category-tag">${getCategoryLabel(m.category)}</span>
        </div>
    `).join('');
}

function getCategoryLabel(category) {
    const labels = {
        'battute': 'Battuta Top',
        'fails': 'Epic Fail',
        'quotes': 'Citazione',
        'momenti': 'Momento Storico'
    };
    return labels[category] || category;
}

function renderHallOfFame(topMoments) {
    const fame = document.getElementById('hall-of-fame');
    if (!fame) return;

    fame.innerHTML = topMoments.map((m, i) => `
        <div class="best-of-item" style="border-left-color: ${i === 0 ? 'gold' : i === 1 ? 'silver' : '#cd7f32'}">
            <p class="quote">"${m.quote}"</p>
            <p class="author">— ${m.author}</p>
        </div>
    `).join('');
}

// Gestione tabs categoria
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentCategory = btn.dataset.category;
        renderMoments();
    });
});

// Gestione tabs anno
document.querySelectorAll('.year-tab').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.year-tab').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentYear = btn.dataset.year;
        renderMoments();
    });
});

// Init
document.addEventListener('DOMContentLoaded', loadBestOf);
