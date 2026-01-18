// AperiPoker - Best Of JS

let allMoments = [];
let currentCategory = 'all';

async function loadBestOf() {
    const list = document.getElementById('best-of-list');
    const data = await loadData('best-of.json');

    if (!data || !data.moments || data.moments.length === 0) {
        list.innerHTML = `
            <div class="loading">
                <p>Nessun momento epico registrato.</p>
                <p>Esegui l'agente best-of per scoprire i momenti migliori.</p>
            </div>
        `;
        return;
    }

    allMoments = data.moments;
    renderMoments('all');
    renderHallOfFame(data.hallOfFame || allMoments.slice(0, 3));
}

function renderMoments(category) {
    const list = document.getElementById('best-of-list');
    currentCategory = category;

    let filtered = allMoments;
    if (category !== 'all') {
        filtered = allMoments.filter(m => m.category === category);
    }

    if (filtered.length === 0) {
        list.innerHTML = `<div class="loading">Nessun momento in questa categoria.</div>`;
        return;
    }

    list.innerHTML = filtered.map(m => `
        <div class="best-of-item">
            <p class="quote">"${m.quote}"</p>
            <p>
                <span class="author">— ${m.author}</span>
                <span class="date">${formatDate(m.date)}</span>
            </p>
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
        renderMoments(btn.dataset.category);
    });
});

// Init
document.addEventListener('DOMContentLoaded', loadBestOf);
