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

function getAvatarHTML(member) {
    const initials = member.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
    const fallback = member.emoji || initials;

    if (member.photo) {
        // Con foto: mostra immagine con fallback su errore
        return `
            <div class="member-avatar-wrapper">
                <img src="../img/membri/${member.photo}"
                     alt="${member.name}"
                     onerror="this.parentElement.innerHTML='<span class=\\'member-avatar-fallback\\'>${fallback}</span>'"
                />
            </div>
        `;
    } else {
        // Senza foto: mostra emoji o iniziali
        return `
            <div class="member-avatar-wrapper">
                <span class="member-avatar-fallback">${fallback}</span>
            </div>
        `;
    }
}

function renderMembers(members) {
    const grid = document.getElementById('members-grid');

    grid.innerHTML = members.map(m => {
        const traits = m.traits || [];

        return `
            <div class="member-card">
                <div class="member-header">
                    ${getAvatarHTML(m)}
                    <div class="member-nickname">${m.name}</div>
                    <div class="member-title">${m.title || 'Membro'}</div>
                </div>
                <div class="member-body">
                    <p class="member-description">${m.description}</p>
                    ${m.catchphrase ? `
                        <p class="member-catchphrase" style="font-style: italic; margin: 0.75rem 0; color: var(--secondary);">
                            "${m.catchphrase}"
                        </p>
                    ` : ''}
                    ${traits.length > 0 ? `
                        <div class="member-traits">
                            ${traits.map(t => `<span class="trait">${t}</span>`).join('')}
                        </div>
                    ` : ''}
                    ${m.stats ? `
                        <div class="member-stats-detailed" style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--bg-light);">
                            <p style="font-size: 0.85rem; color: var(--text-muted);">
                                <strong style="color: var(--secondary);">${formatNumber(m.stats.messageCount)}</strong> messaggi |
                                Rank: <strong>#${m.stats.rank}</strong> |
                                Media: ${m.stats.avgWordsPerMessage} parole/msg
                            </p>
                        </div>
                    ` : ''}
                    ${m.superpower ? `
                        <p style="font-size: 0.8rem; margin-top: 0.5rem;">
                            <strong>Superpotere:</strong> ${m.superpower}
                        </p>
                    ` : ''}
                </div>
            </div>
        `;
    }).join('');
}

// Init
document.addEventListener('DOMContentLoaded', loadMembri);
