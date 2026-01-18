#!/usr/bin/env python3
"""
Estrae i messaggi di una singola settimana per analisi.
Uso: python extract_week.py <week_start_date>
Es:  python extract_week.py 2025-01-06
"""

import json
import sys
from datetime import datetime, timedelta
from collections import defaultdict

def get_week_start(ts):
    dt = datetime.fromisoformat(ts)
    return (dt - timedelta(days=dt.weekday())).strftime('%Y-%m-%d')

def main():
    if len(sys.argv) < 2:
        print("Uso: python extract_week.py <week_start_date>")
        print("Es:  python extract_week.py 2025-01-06")
        sys.exit(1)

    week_date = sys.argv[1]
    year = int(week_date[:4])

    # Load messages - try year-specific file first, then all
    import os
    year_file = f'data/raw_messages_{year}.json'
    all_file = 'data/raw_messages_all.json'

    if os.path.exists(year_file):
        with open(year_file, 'r') as f:
            data = json.load(f)
    else:
        with open(all_file, 'r') as f:
            data = json.load(f)

    messages = data['messages']

    # Filter for this week
    week_msgs = [m for m in messages if get_week_start(m['timestamp']) == week_date]

    if not week_msgs:
        print(f"Nessun messaggio per la settimana {week_date}")
        sys.exit(1)

    # Count per member
    member_counts = defaultdict(int)
    for msg in week_msgs:
        member_counts[msg['author']] += 1

    print(f"SETTIMANA: {week_date}")
    print(f"Messaggi totali: {len(week_msgs)}")
    print(f"Membri attivi: {len(member_counts)}")
    print("\nConteggio per membro:")
    for name, count in sorted(member_counts.items(), key=lambda x: -x[1]):
        print(f"  {name.split()[0]}: {count}")
    print("\n" + "="*60 + "\n")

    # Print messages
    for msg in week_msgs:
        author = msg['author'].split()[0]
        text = msg['text'][:300].replace('\n', ' ')
        ts = msg['timestamp'][5:16]
        print(f"[{ts}] {author}: {text}")

if __name__ == '__main__':
    main()
