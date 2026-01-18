#!/usr/bin/env python3
"""
Parser per export chat WhatsApp.
Legge un file .txt esportato da WhatsApp e genera file JSON per il sito.

Uso:
    python parse_whatsapp.py <path_to_chat.txt>

Output:
    - data/stats.json: Statistiche generali (da 2026)
    - data/classifica.json: Classifica per attività (da 2026)
    - data/raw_messages_2025.json: Messaggi 2025 (per profili membri)
    - data/raw_messages_2026.json: Messaggi 2026 (per pagelle/best-of)
"""

import re
import json
import sys
from datetime import datetime
from collections import defaultdict
from pathlib import Path

# Pattern per messaggi WhatsApp
# Formato: M/D/YY, H:MM AM/PM - Nome: messaggio
PATTERNS = [
    # Formato americano con AM/PM: 1/17/26, 9:08 AM - Nome: messaggio
    re.compile(r'^(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2})\s*(AM|PM)?\s*[-–]\s*([^:]+):\s*(.*)$', re.IGNORECASE),
    # Formato senza AM/PM
    re.compile(r'^(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2})\s*[-–]\s*([^:]+):\s*(.*)$'),
]

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
                'author': author.strip(),
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
        'firstMessage': None,
        'lastMessage': None,
    })

    for msg in messages:
        author = msg['author']
        member = members[author]

        member['messageCount'] += 1
        member['wordCount'] += len(msg['text'].split())
        member['hourlyActivity'][msg['hour']] += 1
        member['dailyActivity'][msg['weekday']] += 1

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
            }
            for name, data in sorted(members.items(), key=lambda x: -x[1]['messageCount'])
        ],
        'generatedAt': datetime.now().isoformat(),
    }

    return stats, classifica, dict(members)


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

    # Separa per anno
    messages_2025 = [m for m in messages if m['year'] == 2025]
    messages_2026 = [m for m in messages if m['year'] == 2026]

    print(f"  - 2025: {len(messages_2025)} messaggi")
    print(f"  - 2026: {len(messages_2026)} messaggi")

    # Analizza solo 2026 per stats e classifica correnti
    stats, classifica, members_data_2026 = analyze_messages(messages_2026)

    # Analizza 2025 per profili membri
    _, _, members_data_2025 = analyze_messages(messages_2025)

    # Crea directory data se non esiste
    data_dir = Path(__file__).parent.parent / 'data'
    data_dir.mkdir(exist_ok=True)

    # Salva stats.json (da 2026)
    with open(data_dir / 'stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"Salvato: stats.json (2026)")

    # Salva classifica.json (da 2026)
    with open(data_dir / 'classifica.json', 'w', encoding='utf-8') as f:
        json.dump(classifica, f, indent=2, ensure_ascii=False)
    print(f"Salvato: classifica.json (2026)")

    # Salva raw_messages_2025.json (per profili membri)
    with open(data_dir / 'raw_messages_2025.json', 'w', encoding='utf-8') as f:
        json.dump({
            'messages': messages_2025,
            'members': members_data_2025,
            'year': 2025,
            'parsedAt': datetime.now().isoformat(),
        }, f, indent=2, ensure_ascii=False)
    print(f"Salvato: raw_messages_2025.json ({len(messages_2025)} messaggi)")

    # Salva raw_messages_2026.json (per pagelle/best-of)
    with open(data_dir / 'raw_messages_2026.json', 'w', encoding='utf-8') as f:
        json.dump({
            'messages': messages_2026,
            'members': members_data_2026,
            'year': 2026,
            'parsedAt': datetime.now().isoformat(),
        }, f, indent=2, ensure_ascii=False)
    print(f"Salvato: raw_messages_2026.json ({len(messages_2026)} messaggi)")

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

    print("\n--- Prossimi passi ---")
    print("1. Genera profili membri: leggi agents/membri-agent.md")
    print("2. Genera pagelle/best-of: leggi agents/pagelle-agent.md e agents/best-of-agent.md")


if __name__ == '__main__':
    main()
