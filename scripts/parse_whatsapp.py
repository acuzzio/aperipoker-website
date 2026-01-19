#!/usr/bin/env python3
"""
Parser per export chat WhatsApp.
Legge un file .txt esportato da WhatsApp e genera file JSON per il sito.

Uso:
    python parse_whatsapp.py <path_to_chat.txt>

Output:
    - data/stats.json: Statistiche generali (da 2026)
    - data/classifica.json: Classifica per attività (da 2026)
    - data/anni/*.json: Statistiche per ogni anno (2019-2026)
    - data/pagelle/*.json: Pagelle settimanali per ogni anno
    - data/raw_messages_*.json: Messaggi per anno
"""

import re
import json
import sys
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path
import calendar

# Pattern per messaggi WhatsApp
# Formato: M/D/YY, H:MM AM/PM - Nome: messaggio
PATTERNS = [
    # Formato americano con AM/PM: 1/17/26, 9:08 AM - Nome: messaggio
    re.compile(r'^(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2})\s*(AM|PM)?\s*[-–]\s*([^:]+):\s*(.*)$', re.IGNORECASE),
    # Formato senza AM/PM
    re.compile(r'^(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2})\s*[-–]\s*([^:]+):\s*(.*)$'),
]

# Normalizzazione nomi (nickname -> nome completo)
NAME_MAP = {
    'Alecs': 'Alessio Macalùso',
    'Alessio Mac': 'Alessio Macalùso',
    'Alessio Macaluso': 'Alessio Macalùso',
    'Cocco': 'Cosimo Nenciòni',
    'Cosimo Nencioni': 'Cosimo Nenciòni',
    'Giec': 'Giacomo Dolfi',
    'Adriano 2': 'Adriano Sergio Lorenzo Facchini',
    'Adriano': 'Adriano Sergio Lorenzo Facchini',
    '+39 348 813 1011': 'Adriano Sergio Lorenzo Facchini',
    'Fausto': 'Fausto Petrini',
    'Alessio Valentini Giusto': 'Alessio Valentini',
    'Fede': 'Federico Ceccuzzi',
}


def normalize_name(name):
    """Normalizza il nome usando la mappa dei nomi."""
    return NAME_MAP.get(name, name)


# Messaggi di sistema da ignorare
SYSTEM_KEYWORDS = [
    'created group',
    'added you',
    'added',
    'removed',
    'left',
    'changed',
    'end-to-end encrypted',
    'group settings',
    'modified',
    'disappearing messages',
    'ha creato il gruppo',
    'ti ha aggiunto',
    'ha aggiunto',
    'ha rimosso',
    'è uscito',
    'ha cambiato',
    'crittografia end-to-end',
    'impostazioni del gruppo',
    'ha modificato',
    'messaggi effimeri',
    '<This message was deleted>',
    '<Media omitted>',
    '<Questo messaggio è stato eliminato>',
    '<Media omessi>',
]


def is_system_message(text):
    """Verifica se è un messaggio di sistema."""
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in SYSTEM_KEYWORDS)


def parse_date(date_str, time_str, ampm=None):
    """Parsa data e ora in formato datetime."""
    # Formato americano M/D/YY
    try:
        date = datetime.strptime(date_str, '%m/%d/%y')
        hour, minute = map(int, time_str.split(':'))

        # Gestisci AM/PM
        if ampm:
            ampm = ampm.upper()
            if ampm == 'PM' and hour != 12:
                hour += 12
            elif ampm == 'AM' and hour == 12:
                hour = 0

        return date.replace(hour=hour, minute=minute)
    except ValueError:
        pass

    # Fallback: altri formati
    for fmt in ['%d/%m/%y', '%d/%m/%Y', '%m/%d/%Y']:
        try:
            date = datetime.strptime(date_str, fmt)
            hour, minute = map(int, time_str.split(':'))
            return date.replace(hour=hour, minute=minute)
        except ValueError:
            continue

    return None


def parse_message_line(line):
    """Parsa una singola riga di messaggio."""
    for pattern in PATTERNS:
        match = pattern.match(line.strip())
        if match:
            groups = match.groups()

            # Pattern con AM/PM ha 5 gruppi, senza ne ha 4
            if len(groups) == 5:
                date_str, time_str, ampm, author, text = groups
            else:
                date_str, time_str, author, text = groups
                ampm = None

            # Salta messaggi di sistema
            if is_system_message(text) or is_system_message(author):
                return None

            timestamp = parse_date(date_str, time_str, ampm)
            if not timestamp:
                continue

            return {
                'timestamp': timestamp.isoformat(),
                'year': timestamp.year,
                'author': normalize_name(author.strip()),
                'text': text.strip(),
                'date': date_str,
                'time': time_str,
                'hour': timestamp.hour,
                'weekday': timestamp.weekday(),
            }

    return None


def parse_chat_file(filepath):
    """Parsa un file di chat WhatsApp."""
    messages = []
    current_message = None

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            parsed = parse_message_line(line)

            if parsed:
                # Nuovo messaggio
                if current_message:
                    messages.append(current_message)
                current_message = parsed
            elif current_message and line.strip():
                # Continuazione del messaggio precedente (multilinea)
                current_message['text'] += '\n' + line.strip()

    # Aggiungi l'ultimo messaggio
    if current_message:
        messages.append(current_message)

    return messages


def analyze_messages(messages):
    """Analizza i messaggi e genera statistiche."""
    stats = {
        'totalMessages': len(messages),
        'totalMembers': 0,
        'mostActive': '',
        'lastUpdate': datetime.now().isoformat(),
    }

    members = defaultdict(lambda: {
        'messageCount': 0,
        'wordCount': 0,
        'emojiCount': 0,
        'hourlyActivity': defaultdict(int),
        'dailyActivity': defaultdict(int),
        'monthlyActivity': defaultdict(int),
        'firstMessage': None,
        'lastMessage': None,
    })

    # Attività aggregata per grafici
    hourly_total = defaultdict(int)
    daily_total = defaultdict(int)
    monthly_total = defaultdict(int)

    for msg in messages:
        author = msg['author']
        member = members[author]

        member['messageCount'] += 1
        member['wordCount'] += len(msg['text'].split())
        member['hourlyActivity'][msg['hour']] += 1
        member['dailyActivity'][msg['weekday']] += 1

        # Attività mensile
        month_key = msg['timestamp'][:7]  # YYYY-MM
        member['monthlyActivity'][month_key] += 1
        monthly_total[month_key] += 1

        # Totali aggregati
        hourly_total[msg['hour']] += 1
        daily_total[msg['weekday']] += 1

        # Primo e ultimo messaggio
        if not member['firstMessage'] or msg['timestamp'] < member['firstMessage']:
            member['firstMessage'] = msg['timestamp']
        if not member['lastMessage'] or msg['timestamp'] > member['lastMessage']:
            member['lastMessage'] = msg['timestamp']

    # Trova il più attivo
    if members:
        most_active = max(members.items(), key=lambda x: x[1]['messageCount'])
        stats['mostActive'] = most_active[0]
        stats['totalMembers'] = len(members)

    # Prepara classifica
    classifica = {
        'members': [
            {
                'name': name,
                'messageCount': data['messageCount'],
                'wordCount': data['wordCount'],
                'avgWordsPerMessage': round(data['wordCount'] / data['messageCount'], 1) if data['messageCount'] > 0 else 0,
                'hourlyActivity': dict(data['hourlyActivity']),
                'dailyActivity': dict(data['dailyActivity']),
            }
            for name, data in sorted(members.items(), key=lambda x: -x[1]['messageCount'])
        ],
        'hourlyTotal': dict(hourly_total),
        'dailyTotal': dict(daily_total),
        'monthlyTotal': dict(monthly_total),
        'generatedAt': datetime.now().isoformat(),
    }

    return stats, classifica, dict(members)


def generate_year_data(messages, year, all_years_stats):
    """Genera dati completi per un singolo anno."""
    year_messages = [m for m in messages if m['year'] == year]

    if not year_messages:
        return None

    stats, classifica, members_data = analyze_messages(year_messages)

    # MVP dell'anno (dati storici forniti)
    mvp_map = {
        2019: 'Cosimo Nenciòni',
        2020: 'Adriano Sergio Lorenzo Facchini',
        2021: 'Adriano Sergio Lorenzo Facchini',
        2022: 'Adriano Sergio Lorenzo Facchini',
        2023: 'Adriano Sergio Lorenzo Facchini',
        2024: 'Adriano Sergio Lorenzo Facchini',
        2025: 'Adriano Sergio Lorenzo Facchini',
        2026: 'Adriano Sergio Lorenzo Facchini',
    }

    # Highlights storici
    highlights_map = {
        2019: "Nascita ufficiale del gruppo chat. Cosimo domina la scena.",
        2020: "Anno del COVID: il gruppo esplode con 6107 messaggi! Adriano prende lo scettro.",
        2021: "Picco storico di attività: 6136 messaggi. Il gruppo è on fire.",
        2022: "Si torna alla normalità post-COVID. Attività più moderata.",
        2023: "Il gruppo trova un nuovo equilibrio. Discussioni di qualità.",
        2024: "Anno di consolidamento. Le dinamiche sono ormai rodate.",
        2025: "Arriva Federico! Aria fresca nel gruppo.",
        2026: "Anno in corso. Nuove avventure all'orizzonte.",
    }

    # Best-of placeholder per l'anno
    best_of_by_year = {
        2019: [
            {"quote": "Primo anno del gruppo!", "author": "Gruppo", "context": "Gli inizi di AperiPoker"}
        ],
        2020: [
            {"quote": "Covid edition - tutti a casa a scrivere", "author": "Gruppo", "context": "L'anno del lockdown"}
        ],
        2021: [
            {"quote": "Anno record per messaggi!", "author": "Gruppo", "context": "Peak activity"}
        ],
        2022: [
            {"quote": "Si ricomincia a uscire", "author": "Gruppo", "context": "Post-pandemia"}
        ],
        2023: [
            {"quote": "Ritorno alla normalità", "author": "Gruppo", "context": "Equilibrio ritrovato"}
        ],
        2024: [
            {"quote": "Routine consolidata", "author": "Gruppo", "context": "Il gruppo va avanti"}
        ],
        2025: [
            {"quote": "Federico si unisce al gruppo!", "author": "Gruppo", "context": "New entry"}
        ],
        2026: [
            {"quote": "Soddisfazione massima per aver aggiustato l'autoclave con chat gpt.", "author": "Adriano Sergio Lorenzo Facchini", "context": "ChatGPT fa l'idraulico"},
            {"quote": "W il bollore", "author": "Fausto Petrini", "context": "Il motto del 2026"},
            {"quote": "Tombino", "author": "Cosimo Nenciòni", "context": "Risposta filosofica"}
        ],
    }

    # Calcola trend rispetto anno precedente
    prev_year_stats = all_years_stats.get(year - 1, {})
    trend = None
    if prev_year_stats:
        prev_messages = prev_year_stats.get('totalMessages', 0)
        if prev_messages > 0:
            trend = round((stats['totalMessages'] - prev_messages) / prev_messages * 100, 1)

    return {
        'year': year,
        'stats': {
            'totalMessages': stats['totalMessages'],
            'totalMembers': stats['totalMembers'],
            'mvp': mvp_map.get(year, stats['mostActive']),
            'trend': trend,
        },
        'classifica': classifica['members'][:7],  # Top 7
        'monthlyActivity': classifica['monthlyTotal'],
        'hourlyActivity': classifica['hourlyTotal'],
        'dailyActivity': classifica['dailyTotal'],
        'highlights': highlights_map.get(year, ""),
        'bestOf': best_of_by_year.get(year, []),
        'generatedAt': datetime.now().isoformat(),
    }


def get_week_start(dt):
    """Restituisce il lunedì della settimana per una data."""
    return dt - timedelta(days=dt.weekday())


def generate_pagelle_for_year(messages, year):
    """Genera pagelle settimanali per un anno."""
    year_messages = [m for m in messages if m['year'] == year]

    if not year_messages:
        return None

    # Raggruppa messaggi per settimana
    weeks = defaultdict(list)
    for msg in year_messages:
        dt = datetime.fromisoformat(msg['timestamp'])
        week_start = get_week_start(dt)
        week_key = week_start.strftime('%Y-%m-%d')
        weeks[week_key].append(msg)

    # Ordina settimane
    sorted_weeks = sorted(weeks.keys())

    # Genera pagelle per ogni settimana
    pagelle_weeks = []
    member_cumulative = defaultdict(lambda: {
        'totalVoti': 0,
        'votiCount': 0,
        'totalMessaggi': 0,
        'bestVoto': 0,
        'worstVoto': 10,
        'bestWeek': None,
        'worstWeek': None,
    })

    for week_key in sorted_weeks:
        week_msgs = weeks[week_key]
        week_start = datetime.strptime(week_key, '%Y-%m-%d')
        week_end = week_start + timedelta(days=6)

        # Conta messaggi per membro questa settimana
        member_counts = defaultdict(int)
        for msg in week_msgs:
            member_counts[msg['author']] += 1

        if not member_counts:
            continue

        # Calcola statistiche settimana
        total_week_msgs = sum(member_counts.values())
        max_msgs = max(member_counts.values())
        avg_msgs = total_week_msgs / len(member_counts) if member_counts else 0
        days_in_week = min(7, (datetime.now() - week_start).days + 1) if year == datetime.now().year else 7

        # Genera pagelle per ogni membro attivo
        week_pagelle = []
        for name, count in sorted(member_counts.items(), key=lambda x: -x[1]):
            # Calcola voto basato su attività relativa
            # Media = 6, sopra media = bonus, top = 8+
            if max_msgs > 0:
                relative_activity = count / max_msgs
                if count == max_msgs:
                    base_voto = 8.0 + (count / 50) * 0.5  # Bonus per volume
                elif relative_activity > 0.5:
                    base_voto = 7.0 + relative_activity
                elif relative_activity > 0.2:
                    base_voto = 6.0 + relative_activity * 2
                else:
                    base_voto = 5.0 + relative_activity * 5
            else:
                base_voto = 6.0

            voto = round(min(10, max(4, base_voto)), 1)
            media_giornaliera = round(count / days_in_week, 1)

            # Giudizio automatico basato su stats
            if voto >= 8:
                giudizio = f"Settimana dominante con {count} messaggi. Protagonista assoluto."
            elif voto >= 7:
                giudizio = f"Buona presenza nel gruppo con {count} messaggi. Partecipazione attiva."
            elif voto >= 6:
                giudizio = f"Settimana nella media con {count} messaggi. Presente ma non protagonista."
            elif voto >= 5:
                giudizio = f"Settimana sottotono con solo {count} messaggi. Si può fare di più."
            else:
                giudizio = f"Quasi assente con {count} messaggi. In letargo?"

            week_pagelle.append({
                'name': name,
                'voto': voto,
                'giudizio': giudizio,
                'messaggi': count,
                'mediaGiornaliera': media_giornaliera,
            })

            # Aggiorna cumulativo
            cum = member_cumulative[name]
            cum['totalVoti'] += voto
            cum['votiCount'] += 1
            cum['totalMessaggi'] += count
            if voto > cum['bestVoto']:
                cum['bestVoto'] = voto
                cum['bestWeek'] = week_key
            if voto < cum['worstVoto']:
                cum['worstVoto'] = voto
                cum['worstWeek'] = week_key

        # Ordina per voto
        week_pagelle.sort(key=lambda x: -x['voto'])

        # Awards settimanali
        mvp = week_pagelle[0]['name'] if week_pagelle else None
        fantasma = week_pagelle[-1]['name'] if week_pagelle else None

        pagelle_weeks.append({
            'startDate': week_key,
            'endDate': week_end.strftime('%Y-%m-%d'),
            'pagelle': week_pagelle,
            'riassunto': f"Settimana con {total_week_msgs} messaggi totali. {len(member_counts)} membri attivi.",
            'awards': {
                'mvp': mvp,
                'chiacchierone': mvp,
                'fantasma': fantasma,
            },
            'stats': {
                'totalMessages': total_week_msgs,
                'activeMembers': len(member_counts),
                'avgPerMember': round(avg_msgs, 1),
            }
        })

    # Calcola statistiche cumulative
    cumulative_stats = []
    for name, cum in member_cumulative.items():
        if cum['votiCount'] > 0:
            cumulative_stats.append({
                'name': name,
                'mediaVoto': round(cum['totalVoti'] / cum['votiCount'], 2),
                'totalMessaggi': cum['totalMessaggi'],
                'settimaneAttive': cum['votiCount'],
                'bestVoto': cum['bestVoto'],
                'worstVoto': cum['worstVoto'],
                'bestWeek': cum['bestWeek'],
                'worstWeek': cum['worstWeek'],
            })

    # Ordina per media voto
    cumulative_stats.sort(key=lambda x: -x['mediaVoto'])

    return {
        'year': year,
        'weeks': pagelle_weeks,
        'cumulative': cumulative_stats,
        'totalWeeks': len(pagelle_weeks),
        'generatedAt': datetime.now().isoformat(),
    }


def main():
    if len(sys.argv) < 2:
        print("Uso: python parse_whatsapp.py <path_to_chat.txt>")
        print("\nEsempio:")
        print("  python parse_whatsapp.py ~/Downloads/Chat_WhatsApp.txt")
        sys.exit(1)

    chat_file = Path(sys.argv[1])

    if not chat_file.exists():
        print(f"Errore: File non trovato: {chat_file}")
        sys.exit(1)

    print(f"Parsing {chat_file}...")
    messages = parse_chat_file(chat_file)
    print(f"Trovati {len(messages)} messaggi totali")

    if not messages:
        print("Nessun messaggio trovato. Verifica il formato del file.")
        sys.exit(1)

    # Trova tutti gli anni presenti
    years = sorted(set(m['year'] for m in messages))
    print(f"Anni trovati: {years}")

    # Crea directory
    data_dir = Path(__file__).parent.parent / 'data'
    data_dir.mkdir(exist_ok=True)
    anni_dir = data_dir / 'anni'
    anni_dir.mkdir(exist_ok=True)

    # Calcola stats per ogni anno (per i trend)
    all_years_stats = {}
    for year in years:
        year_messages = [m for m in messages if m['year'] == year]
        all_years_stats[year] = {'totalMessages': len(year_messages)}

    print("\n--- Generazione dati per anno ---")

    # Genera JSON per ogni anno
    years_summary = []
    for year in years:
        year_data = generate_year_data(messages, year, all_years_stats)
        if year_data:
            # Salva file anno
            with open(anni_dir / f'{year}.json', 'w', encoding='utf-8') as f:
                json.dump(year_data, f, indent=2, ensure_ascii=False)
            print(f"  Salvato: anni/{year}.json ({year_data['stats']['totalMessages']} messaggi)")

            years_summary.append({
                'year': year,
                'totalMessages': year_data['stats']['totalMessages'],
                'mvp': year_data['stats']['mvp'],
                'trend': year_data['stats']['trend'],
                'highlights': year_data['highlights'],
            })

    # Salva overview anni
    with open(data_dir / 'anni-overview.json', 'w', encoding='utf-8') as f:
        json.dump({
            'years': years_summary,
            'generatedAt': datetime.now().isoformat(),
        }, f, indent=2, ensure_ascii=False)
    print(f"Salvato: anni-overview.json")

    # Genera pagelle per ogni anno
    print("\n--- Generazione pagelle settimanali ---")
    pagelle_dir = data_dir / 'pagelle'
    pagelle_dir.mkdir(exist_ok=True)

    pagelle_overview = []
    for year in years:
        pagelle_data = generate_pagelle_for_year(messages, year)
        if pagelle_data and pagelle_data['weeks']:
            # Salva pagelle anno
            with open(pagelle_dir / f'{year}.json', 'w', encoding='utf-8') as f:
                json.dump(pagelle_data, f, indent=2, ensure_ascii=False)
            print(f"  Salvato: pagelle/{year}.json ({pagelle_data['totalWeeks']} settimane)")

            # Top 3 per media voto
            top3 = pagelle_data['cumulative'][:3] if pagelle_data['cumulative'] else []
            pagelle_overview.append({
                'year': year,
                'totalWeeks': pagelle_data['totalWeeks'],
                'topPerformers': [{'name': p['name'], 'mediaVoto': p['mediaVoto']} for p in top3],
            })

    # Salva pagelle overview
    with open(data_dir / 'pagelle-overview.json', 'w', encoding='utf-8') as f:
        json.dump({
            'years': pagelle_overview,
            'generatedAt': datetime.now().isoformat(),
        }, f, indent=2, ensure_ascii=False)
    print(f"Salvato: pagelle-overview.json")

    # Salva raw_messages per tutti gli anni
    print("\n--- Salvataggio raw_messages per anno ---")
    for year in years:
        year_messages = [m for m in messages if m['year'] == year]
        _, _, members_data = analyze_messages(year_messages)
        with open(data_dir / f'raw_messages_{year}.json', 'w', encoding='utf-8') as f:
            json.dump({
                'messages': year_messages,
                'members': members_data,
                'year': year,
                'parsedAt': datetime.now().isoformat(),
            }, f, indent=2, ensure_ascii=False)
        print(f"  Salvato: raw_messages_{year}.json ({len(year_messages)} messaggi)")

    # Analizza anno corrente per stats e classifica
    current_year = max(years)
    messages_current = [m for m in messages if m['year'] == current_year]
    stats, classifica, _ = analyze_messages(messages_current)

    # Salva stats.json (anno corrente)
    with open(data_dir / 'stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"Salvato: stats.json ({current_year})")

    # Salva classifica.json (anno corrente)
    with open(data_dir / 'classifica.json', 'w', encoding='utf-8') as f:
        json.dump(classifica, f, indent=2, ensure_ascii=False)
    print(f"Salvato: classifica.json ({current_year})")

    # Analizza TUTTA la chat per profili membri e history
    _, _, members_data_all = analyze_messages(messages)

    # Salva raw_messages_all.json (per profili e history)
    with open(data_dir / 'raw_messages_all.json', 'w', encoding='utf-8') as f:
        json.dump({
            'messages': messages,
            'members': members_data_all,
            'totalMessages': len(messages),
            'dateRange': {
                'from': messages[0]['timestamp'] if messages else None,
                'to': messages[-1]['timestamp'] if messages else None,
            },
            'parsedAt': datetime.now().isoformat(),
        }, f, indent=2, ensure_ascii=False)
    print(f"Salvato: raw_messages_all.json ({len(messages)} messaggi totali)")

    # Riepilogo
    print("\n--- Riepilogo 2026 ---")
    print(f"Messaggi: {stats['totalMessages']}")
    print(f"Membri attivi: {stats['totalMembers']}")
    print(f"Più attivo: {stats['mostActive']}")
    print("\nClassifica 2026:")
    for i, member in enumerate(classifica['members'][:7], 1):
        print(f"  {i}. {member['name']}: {member['messageCount']} messaggi")

    print("\n--- Riepilogo storico ---")
    for ys in years_summary:
        trend_str = f" ({'+' if ys['trend'] and ys['trend'] > 0 else ''}{ys['trend']}%)" if ys['trend'] else ""
        print(f"  {ys['year']}: {ys['totalMessages']} messaggi{trend_str} - MVP: {ys['mvp'].split()[0]}")


if __name__ == '__main__':
    main()
