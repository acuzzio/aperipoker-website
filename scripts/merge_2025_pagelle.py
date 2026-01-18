#!/usr/bin/env python3
"""
Merge all 2025 pagelle partial files into one complete file.
Normalizes field names and fixes Alessio surname issue.
"""

import json
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path(__file__).parent.parent / 'data' / 'pagelle'

# Name normalization mapping
NAME_MAP = {
    'Adriano': 'Adriano',
    'Adriano Sergio Lorenzo Facchini': 'Adriano',
    'Cosimo': 'Cosimo',
    'Cosimo Nenciòni': 'Cosimo',
    'Cosimo Nencioni': 'Cosimo',
    'Giacomo': 'Giacomo',
    'Giacomo Paoletti': 'Giacomo',
    'Giacomo Dolfi': 'Giacomo',
    'Fausto': 'Fausto',
    'Fausto Tartuferi': 'Fausto',
    'Fausto Petrini': 'Fausto',
    'Alessio Valentini': 'Alessio V.',
    'Alessio V.': 'Alessio V.',
    'Alessio Macaluso': 'Alessio M.',
    'Alessio Macalùso': 'Alessio M.',
    'Alessio M.': 'Alessio M.',
    'Federico': 'Federico',
    'Federico Tartuferi': 'Federico',
    'Federico Ceccuzzi': 'Federico',
}

def normalize_name(name):
    """Normalize member name to short form with surname initial for Alessio."""
    return NAME_MAP.get(name, name)

def normalize_week(week):
    """Normalize week data to the expected pagelle.js format."""
    normalized = {
        'startDate': week.get('startDate') or week.get('weekStart'),
        'stats': {
            'totalMessages': 0,
            'activeMembers': 0,
            'avgPerMember': 0
        },
        'riassunto': week.get('theme') or week.get('riassunto', ''),
        'bestQuotes': [],
        'pagelle': []
    }

    # Get the pagelle - could be list (grades/pagelle) or dict keyed by name
    pagelle_raw = week.get('pagelle') or week.get('grades', [])

    # Convert dict format to list format if needed
    if isinstance(pagelle_raw, dict):
        pagelle_array = []
        for name, data in pagelle_raw.items():
            if isinstance(data, dict):
                data['name'] = name
                pagelle_array.append(data)
    else:
        pagelle_array = pagelle_raw

    total_msgs = 0
    all_quotes = []

    for p in pagelle_array:
        # Skip if not a dict (some files have just names as strings - incomplete data)
        if not isinstance(p, dict):
            continue

        name = normalize_name(p.get('name', ''))
        voto = p.get('voto') or p.get('grade', 7)  # Default 7 if no grade
        messaggi = p.get('messaggi', 0)
        media = p.get('mediaGiornaliera', 0)

        total_msgs += messaggi

        # Collect best quotes for the week
        quotes = p.get('bestQuotes', [])
        for q in quotes[:2]:  # Max 2 quotes per person
            if q:
                all_quotes.append({'quote': q, 'author': name})

        normalized['pagelle'].append({
            'name': name,
            'voto': round(voto, 1),
            'giudizio': p.get('giudizio', ''),
            'highlights': p.get('highlights', []),
            'messaggi': messaggi,
            'mediaGiornaliera': round(media, 1) if media else 0
        })

    # Update stats
    normalized['stats']['totalMessages'] = total_msgs
    normalized['stats']['activeMembers'] = len(normalized['pagelle'])
    normalized['stats']['avgPerMember'] = round(total_msgs / len(normalized['pagelle']), 1) if normalized['pagelle'] else 0

    # Select top 3 quotes for the week
    normalized['bestQuotes'] = all_quotes[:3]

    return normalized

def calculate_cumulative(weeks):
    """Calculate cumulative stats for all members across all weeks."""
    member_stats = defaultdict(lambda: {
        'totalMessaggi': 0,
        'totalVoti': [],
        'settimaneAttive': 0
    })

    for week in weeks:
        for p in week['pagelle']:
            name = p['name']
            member_stats[name]['totalMessaggi'] += p.get('messaggi', 0)
            member_stats[name]['totalVoti'].append(p['voto'])
            member_stats[name]['settimaneAttive'] += 1

    cumulative = []
    for name, stats in member_stats.items():
        voti = stats['totalVoti']
        if voti:
            cumulative.append({
                'name': name,
                'settimaneAttive': stats['settimaneAttive'],
                'totalMessaggi': stats['totalMessaggi'],
                'mediaVoto': round(sum(voti) / len(voti), 2),
                'bestVoto': max(voti),
                'worstVoto': min(voti),
                'signature': ''
            })

    # Sort by mediaVoto descending
    cumulative.sort(key=lambda x: -x['mediaVoto'])
    return cumulative

def main():
    all_weeks = []

    # Load main 2025.json (weeks 1-10)
    main_file = DATA_DIR / '2025.json'
    if main_file.exists():
        with open(main_file) as f:
            data = json.load(f)
            for week in data.get('weeks', []):
                all_weeks.append(normalize_week(week))

    # Load partial files
    partial_files = [
        '2025_weeks_11-20.json',
        '2025_weeks_21-30.json',
        '2025_weeks_31-40.json',
        '2025_weeks_41-53.json'
    ]

    for filename in partial_files:
        filepath = DATA_DIR / filename
        if filepath.exists():
            with open(filepath) as f:
                data = json.load(f)
                # Handle both dict with 'weeks' key and direct list
                if isinstance(data, list):
                    weeks_list = data
                else:
                    weeks_list = data.get('weeks', [])
                for week in weeks_list:
                    all_weeks.append(normalize_week(week))

    # Sort weeks by startDate
    all_weeks.sort(key=lambda w: w['startDate'])

    # Calculate cumulative stats
    cumulative = calculate_cumulative(all_weeks)

    # Create final structure
    final_data = {
        'year': 2025,
        'weeks': all_weeks,
        'cumulative': cumulative,
        'totalWeeks': len(all_weeks)
    }

    # Write merged file
    output_file = DATA_DIR / '2025.json'
    with open(output_file, 'w') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)

    print(f"Merged {len(all_weeks)} weeks into {output_file}")
    print(f"Cumulative stats for {len(cumulative)} members")

    # Clean up partial files
    for filename in partial_files:
        filepath = DATA_DIR / filename
        if filepath.exists():
            filepath.unlink()
            print(f"Removed {filepath}")

if __name__ == '__main__':
    main()
