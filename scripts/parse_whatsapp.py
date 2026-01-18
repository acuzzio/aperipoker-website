#!/usr/bin/env python3
"""
Parser per export chat WhatsApp.
Legge un file .txt esportato da WhatsApp e genera file JSON per il sito.

Uso:
    python parse_whatsapp.py <path_to_chat.txt>

Output:
    - data/stats.json: Statistiche generali
    - data/classifica.json: Classifica per attività
    - data/raw_messages.json: Tutti i messaggi parsati (per gli agenti)
"""

import re
import json
import sys
from datetime import datetime
from collections import defaultdict
from pathlib import Path

# Pattern per messaggi WhatsApp (gestisce vari formati)
# Formato italiano: "12/01/23, 18:30 - Nome: messaggio"
# Formato con parentesi: "[12/01/23, 18:30] Nome: messaggio"
PATTERNS = [
    # Formato: DD/MM/YY, HH:MM - Nome: messaggio
    re.compile(r'^(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2})\s*[-–]\s*([^:]+):\s*(.+)$'),
    # Formato con parentesi quadre
    re.compile(r'^\[(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2})\]\s*([^:]+):\s*(.+)$'),
    # Formato americano: MM/DD/YY
    re.compile(r'^(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2})\s*(?:AM|PM)?\s*[-–]\s*([^:]+):\s*(.+)$', re.IGNORECASE),
]

# Messaggi di sistema da ignorare
SYSTEM_KEYWORDS = [
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
    '<Questo messaggio è stato eliminato>',
    '<Media omessi>',
]


def is_system_message(text):
    """Verifica se è un messaggio di sistema."""
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in SYSTEM_KEYWORDS)


def parse_date(date_str, time_str):
    """Parsa data e ora in formato datetime."""
    # Prova vari formati di data
    formats = [
        '%d/%m/%y',
        '%d/%m/%Y',
        '%m/%d/%y',
        '%m/%d/%Y',
    ]

    for fmt in formats:
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
            date_str, time_str, author, text = match.groups()

            # Salta messaggi di sistema
            if is_system_message(text) or is_system_message(author):
                return None

            timestamp = parse_date(date_str, time_str)
            if not timestamp:
                continue

            return {
                'timestamp': timestamp.isoformat(),
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
    print(f"Trovati {len(messages)} messaggi")

    if not messages:
        print("Nessun messaggio trovato. Verifica il formato del file.")
        sys.exit(1)

    # Analizza
    stats, classifica, members_data = analyze_messages(messages)

    # Crea directory data se non esiste
    data_dir = Path(__file__).parent.parent / 'data'
    data_dir.mkdir(exist_ok=True)

    # Salva stats.json
    with open(data_dir / 'stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"Salvato: {data_dir / 'stats.json'}")

    # Salva classifica.json
    with open(data_dir / 'classifica.json', 'w', encoding='utf-8') as f:
        json.dump(classifica, f, indent=2, ensure_ascii=False)
    print(f"Salvato: {data_dir / 'classifica.json'}")

    # Salva raw_messages.json (per gli agenti)
    with open(data_dir / 'raw_messages.json', 'w', encoding='utf-8') as f:
        json.dump({
            'messages': messages,
            'members': members_data,
            'parsedAt': datetime.now().isoformat(),
        }, f, indent=2, ensure_ascii=False)
    print(f"Salvato: {data_dir / 'raw_messages.json'}")

    # Riepilogo
    print("\n--- Riepilogo ---")
    print(f"Messaggi totali: {stats['totalMessages']}")
    print(f"Membri: {stats['totalMembers']}")
    print(f"Più attivo: {stats['mostActive']}")
    print("\nTop 5:")
    for i, member in enumerate(classifica['members'][:5], 1):
        print(f"  {i}. {member['name']}: {member['messageCount']} messaggi")

    print("\nOra puoi eseguire gli agenti per generare pagelle, best-of e profili membri!")


if __name__ == '__main__':
    main()
