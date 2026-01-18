#!/usr/bin/env python3
"""
Identifica le settimane con messaggi per un dato anno.
Output: lista di numeri settimana ISO con almeno N messaggi.
"""

import json
import sys
from datetime import datetime
from collections import defaultdict

def get_iso_week(date_str):
    """Converte timestamp in numero settimana ISO."""
    dt = datetime.fromisoformat(date_str)
    return dt.isocalendar()[1]

def main():
    if len(sys.argv) < 2:
        print("Usage: python list_weeks_with_messages.py ANNO [MIN_MESSAGES]")
        print("Example: python list_weeks_with_messages.py 2024 10")
        sys.exit(1)

    year = int(sys.argv[1])
    min_messages = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    # Prova file specifico anno, altrimenti usa all
    try:
        with open(f'data/raw_messages_{year}.json', 'r') as f:
            data = json.load(f)
            messages = data['messages']
    except FileNotFoundError:
        with open('data/raw_messages_all.json', 'r') as f:
            data = json.load(f)
            messages = [m for m in data['messages'] if m.get('year') == year]

    # Conta messaggi per settimana
    weeks = defaultdict(int)
    for msg in messages:
        week = get_iso_week(msg['timestamp'])
        weeks[week] += 1

    # Filtra settimane con minimo messaggi
    valid_weeks = sorted([w for w, count in weeks.items() if count >= min_messages])

    print(f"Anno {year}: {len(valid_weeks)} settimane con >= {min_messages} messaggi")
    print(f"Totale messaggi: {len(messages)}")
    print(f"Settimane: {valid_weeks}")

    # Output dettagliato
    print("\nDettaglio:")
    for week in sorted(weeks.keys()):
        count = weeks[week]
        marker = "✓" if count >= min_messages else "✗"
        print(f"  Settimana {week:2d}: {count:4d} messaggi {marker}")

    return valid_weeks

if __name__ == '__main__':
    main()
