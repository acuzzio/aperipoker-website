#!/usr/bin/env python3
"""
Unisce tutti i file week-XX.json in un singolo file pagelle/{anno}.json
con statistiche cumulative calcolate.
"""

import json
import os
import sys
from pathlib import Path
from collections import defaultdict

def merge_weekly_pagelle(year):
    """Unisce le pagelle settimanali in un unico file."""

    pagelle_dir = Path(f'data/pagelle/{year}')
    output_file = Path(f'data/pagelle/{year}.json')

    if not pagelle_dir.exists():
        print(f"Directory {pagelle_dir} non trovata")
        return

    # Raccogli tutti i file week-XX.json
    week_files = sorted(pagelle_dir.glob('week-*.json'))

    if not week_files:
        print(f"Nessun file settimana trovato in {pagelle_dir}")
        return

    print(f"Trovate {len(week_files)} settimane per il {year}")

    weeks = []
    member_stats = defaultdict(lambda: {
        'voti': [],
        'messaggi': 0,
        'settimane': 0,
        'highlights': []
    })

    # Normalizzazione nomi
    name_map = {
        'Cosimo Nencioni': 'Cosimo Nenciòni',
        'Alessio Macaluso': 'Alessio Macalùso',
        'Alessio Mac': 'Alessio Macalùso',
    }

    def normalize_name(name):
        return name_map.get(name, name)

    for week_file in week_files:
        try:
            with open(week_file, 'r', encoding='utf-8') as f:
                week_data = json.load(f)

            # Estrai dati per cumulative
            for pagella in week_data.get('pagelle', []):
                name = normalize_name(pagella.get('name', ''))
                voto = pagella.get('voto', 0)
                messaggi = pagella.get('messaggi', 0)

                if name and voto > 0:
                    member_stats[name]['voti'].append(voto)
                    member_stats[name]['messaggi'] += messaggi
                    member_stats[name]['settimane'] += 1

                    # Raccogli migliori highlights
                    if pagella.get('highlights'):
                        for h in pagella['highlights'][:1]:  # Solo il primo
                            member_stats[name]['highlights'].append(h)

            # Prepara dati settimana per output
            week_output = {
                'startDate': week_data.get('startDate', ''),
                'stats': week_data.get('stats', {}),
                'riassunto': week_data.get('riassunto', ''),
                'bestQuotes': week_data.get('bestQuotes', [])[:3],  # Max 3 citazioni
                'pagelle': week_data.get('pagelle', [])
            }

            weeks.append(week_output)

        except Exception as e:
            print(f"Errore processando {week_file}: {e}")

    # Calcola statistiche cumulative
    cumulative = []
    for name, stats in member_stats.items():
        if stats['voti']:
            media_voto = sum(stats['voti']) / len(stats['voti'])
            cumulative.append({
                'name': name,
                'mediaVoto': round(media_voto, 2),
                'bestVoto': max(stats['voti']),
                'worstVoto': min(stats['voti']),
                'settimaneAttive': stats['settimane'],
                'totalMessaggi': stats['messaggi'],
                'signature': stats['highlights'][0] if stats['highlights'] else ''
            })

    # Ordina per media voto
    cumulative.sort(key=lambda x: x['mediaVoto'], reverse=True)

    # Crea output finale
    output = {
        'year': year,
        'weeks': weeks,
        'cumulative': cumulative,
        'totalWeeks': len(weeks)
    }

    # Salva
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Salvato {output_file}")
    print(f"  - {len(weeks)} settimane")
    print(f"  - {len(cumulative)} membri nella classifica cumulativa")

    # Mostra top 3
    print("\nTop 3 dell'anno:")
    for i, m in enumerate(cumulative[:3], 1):
        print(f"  {i}. {m['name']}: {m['mediaVoto']} (best: {m['bestVoto']}, worst: {m['worstVoto']})")

if __name__ == '__main__':
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2024
    merge_weekly_pagelle(year)
