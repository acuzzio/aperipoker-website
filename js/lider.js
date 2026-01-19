// AperiPoker - Lider JS

async function loadLider() {
    const data = await loadData('lider.json');

    if (!data) {
        document.getElementById('timeline-container').innerHTML = `
            <div class="loading">
                <p>Dati Lider non disponibili.</p>
            </div>
        `;
        return;
    }

    // Update description
    document.getElementById('lider-description').textContent = data.description;

    // Render rules
    renderRules(data.rules);

    // Render current lider
    renderCurrentLider(data.timeline, data.stats);

    // Render timeline
    renderTimeline(data.timeline);

    // Render stats
    renderStats(data.stats);
}

function renderRules(rules) {
    const rulesList = document.getElementById('rules-list');
    if (!rules || rules.length === 0) return;

    rulesList.innerHTML = rules.map(rule => `<li>${rule}</li>`).join('');
}

function renderCurrentLider(timeline, stats) {
    const container = document.getElementById('current-lider-card');
    const current = timeline.find(l => l.endDate === null);

    if (!current) {
        container.innerHTML = '<p>Nessun Lider attivo al momento.</p>';
        return;
    }

    container.innerHTML = `
        <div class="lider-card current-lider">
            <div class="lider-crown">👑</div>
            <h3>${current.name}</h3>
            ${current.alias ? `<p class="lider-alias">alias "${current.alias}"</p>` : ''}
            <p class="lider-period">${current.period}</p>
            <p class="lider-highlight">${current.highlight}</p>
            ${current.quote ? `<blockquote class="lider-quote">"${current.quote}"</blockquote>` : ''}
        </div>
    `;
}

function renderTimeline(timeline) {
    const container = document.getElementById('timeline-container');
    if (!timeline || timeline.length === 0) {
        container.innerHTML = '<p>Nessun Lider nella storia.</p>';
        return;
    }

    // Reverse to show oldest first (or newest first based on preference)
    const sortedTimeline = [...timeline].reverse();

    container.innerHTML = `
        <div class="lider-timeline-list">
            ${sortedTimeline.map((lider, index) => {
                const isCurrent = lider.endDate === null;
                const cardClass = isCurrent ? 'lider-card current' : 'lider-card';

                return `
                    <div class="${cardClass}">
                        <div class="lider-number">${timeline.length - index}</div>
                        <div class="lider-info">
                            <h3>${lider.name}${lider.alias ? ` <span class="alias">(${lider.alias})</span>` : ''}</h3>
                            <p class="period">${lider.period}</p>
                            <p class="highlight">${lider.highlight}</p>
                            ${lider.quote ? `<blockquote>"${lider.quote}"</blockquote>` : ''}
                        </div>
                    </div>
                `;
            }).join('')}
        </div>
    `;
}

function renderStats(stats) {
    const container = document.getElementById('stats-container');
    if (!stats) return;

    container.innerHTML = `
        <div class="lider-stats-grid">
            <div class="stat-card">
                <div class="stat-value">${stats.totalLiders}</div>
                <div class="stat-label">Lider Totali</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${stats.longestReign?.years || '?'}</div>
                <div class="stat-label">Anni del Regno Più Lungo</div>
                <div class="stat-detail">${stats.longestReign?.name || ''}</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${stats.mostReigns?.count || '?'}</div>
                <div class="stat-label">Record di Mandati</div>
                <div class="stat-detail">${stats.mostReigns?.name || ''}</div>
            </div>
        </div>
    `;
}

// Init
document.addEventListener('DOMContentLoaded', loadLider);
