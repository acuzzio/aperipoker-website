#!/usr/bin/env python3
"""
Extract a summary of a year's chat messages for Claude analysis.
Outputs: stats + sample of interesting messages (small enough for context)
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

def extract_year_summary(year: int, sample_size: int = 150) -> dict:
    """Extract summary from raw_messages_{year}.json"""

    data_dir = Path(__file__).parent.parent / "data"
    input_file = data_dir / f"raw_messages_{year}.json"

    if not input_file.exists():
        return {"error": f"File not found: {input_file}"}

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    messages = data.get("messages", [])

    # Stats per member
    member_stats = defaultdict(lambda: {
        "count": 0,
        "words": 0,
        "longest_msg": "",
        "sample_messages": []
    })

    # Monthly activity
    monthly_counts = defaultdict(int)

    # Collect all messages with metadata
    all_msgs = []

    for msg in messages:
        sender = msg.get("author", msg.get("sender", "Unknown"))
        text = msg.get("text", "")
        date = msg.get("timestamp", msg.get("date", ""))[:10]  # YYYY-MM-DD

        # Skip empty or very short
        if not text or len(text) < 3:
            continue

        word_count = len(text.split())

        member_stats[sender]["count"] += 1
        member_stats[sender]["words"] += word_count

        # Track longest message per member
        if len(text) > len(member_stats[sender]["longest_msg"]):
            member_stats[sender]["longest_msg"] = text[:500]  # Truncate

        # Monthly tracking
        if date:
            month = date[:7]  # YYYY-MM
            monthly_counts[month] += 1

        # Store for sampling (prefer longer, more interesting messages)
        score = min(word_count, 50)  # Cap at 50 words to avoid walls of text
        if word_count >= 5:  # At least 5 words
            all_msgs.append({
                "sender": sender,
                "text": text[:300],  # Truncate long messages
                "date": date,
                "score": score
            })

    # Sample interesting messages - diverse selection
    # Sort by score (message length up to 50 words)
    all_msgs.sort(key=lambda x: x["score"], reverse=True)

    # Take top messages but ensure diversity of senders
    sampled = []
    sender_counts = defaultdict(int)
    max_per_sender = sample_size // max(len(member_stats), 1) + 5

    for msg in all_msgs:
        if len(sampled) >= sample_size:
            break
        if sender_counts[msg["sender"]] < max_per_sender:
            sampled.append({
                "sender": msg["sender"],
                "text": msg["text"],
                "date": msg["date"]
            })
            sender_counts[msg["sender"]] += 1

    # Also grab some random shorter messages for variety
    import random
    short_msgs = [m for m in all_msgs if 5 <= m["score"] <= 15]
    if short_msgs and len(sampled) < sample_size:
        random.shuffle(short_msgs)
        for msg in short_msgs[:20]:
            if sender_counts[msg["sender"]] < max_per_sender + 3:
                sampled.append({
                    "sender": msg["sender"],
                    "text": msg["text"],
                    "date": msg["date"]
                })
                sender_counts[msg["sender"]] += 1

    # Sort sampled by date
    sampled.sort(key=lambda x: x["date"])

    # Build summary
    summary = {
        "year": year,
        "totalMessages": len(messages),
        "memberStats": {
            name: {
                "messageCount": stats["count"],
                "wordCount": stats["words"],
                "avgWordsPerMessage": round(stats["words"] / stats["count"], 1) if stats["count"] > 0 else 0,
                "longestMessage": stats["longest_msg"]
            }
            for name, stats in member_stats.items()
        },
        "monthlyActivity": dict(sorted(monthly_counts.items())),
        "sampleMessages": sampled
    }

    return summary


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_year_summary.py <year> [sample_size]")
        sys.exit(1)

    year = int(sys.argv[1])
    sample_size = int(sys.argv[2]) if len(sys.argv) > 2 else 150

    summary = extract_year_summary(year, sample_size)

    # Output to file
    output_dir = Path(__file__).parent.parent / "data" / "summaries"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f"summary_{year}.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"Written: {output_file}")
    print(f"Total messages: {summary['totalMessages']}")
    print(f"Sample messages: {len(summary['sampleMessages'])}")
    print(f"Members: {list(summary['memberStats'].keys())}")


if __name__ == "__main__":
    main()
