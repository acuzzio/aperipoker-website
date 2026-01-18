// AperiPoker - Membri JS

async function loadMembri() {
    const grid = document.getElementById('members-grid');
    const data = await loadData('membri.json');

    if (!data || !data.members || data.members.length === 0) {
        grid.innerHTML = `
            <div class="loading">
                <p>Nessun profilo disponibile.</p>
                <p>Esegui l'agente membri per generare i profili.</p>
            </div>
        `;
        return;
    }

    renderMembers(data.members);
}

function renderMembers(members) {
    const grid = document.getElementById('members-grid');

    grid.innerHTML = members.map(m => {
        const initials = m.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
        const traits = m.traits || [];

        return `
            <div class="member-card">
                <div class="member-header">
                    <div class="member-avatar">${m.emoji || initials}</div>
                    <div class="member-nickname">${m.name}</div>
                    <div class="member-title">${m.title || 'Membro'}</div>
                </div>
                <div class="member-body">
                    <p class="member-description">${m.description}</p>
                    ${traits.length > 0 ? `
                        <div class="member-traits">
                            ${traits.map(t => `<span class="trait">${t}</span>`).join('')}
                        </div>
                    ` : ''}
                    ${m.stats ? `
                        <p class="member-stats" style="margin-top: 1rem; font-size: 0.85rem; color: var(--text-muted);">
                            ${m.stats.messageCount} messaggi |
                            Emoji preferita: ${m.stats.favoriteEmoji || '🤷'}
                        </p>
                    ` : ''}
                </div>
            </div>
        `;
    }).join('');
}

// Init
document.addEventListener('DOMContentLoaded', loadMembri);
