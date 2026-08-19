#!/usr/bin/env python3
"""
tg_chat_scorer — rank Telegram chats by USEFULNESS for research/scraping.

Reads the local messages.db populated by `tg-user sync-all`. Scores each chat on:
  - recency           : how recently it was active (dead chats = useless)
  - sender diversity  : unique senders / messages (broadcast-only = low engagement)
  - topic relevance   : --topic filter boosts chats matching YOUR interests
  - link density      : URLs / resource links
  - noise denylist    : demotes promotional/religious/spam chats regardless of volume

Stdlib only (sqlite3) — no telethon, no venv required.

Usage:
  python3 tg_chat_scorer.py                              # full ranking (activity-based)
  python3 tg_chat_scorer.py --top 15                     # top N
  python3 tg_chat_scorer.py --min-score 50               # only chats >= 50
  python3 tg_chat_scorer.py --topic "java,rust,devops,ai,python,sql,linux,kubernetes,aws,interview,job,course"  # research-relevant ranking
"""
from __future__ import annotations
import argparse
import os
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = os.environ.get(
    "DB_PATH",
    os.path.expanduser("~/.local/share/tg-cli/messages.db"),
)

TOPIC_RE = re.compile(
    r"(https?://|course|job|hire|internship|rust|python|java|ai|ml|llm|"
    r"kubernetes|devops|aws|gcp|azure|github|tutorial|scholarship|cert|"
    r"paper|arxiv|book|free|repo|dataset|opensource|code|sql|linux|security)",
    re.IGNORECASE,
)
URL_RE = re.compile(r"https?://", re.IGNORECASE)
NOW = datetime.now(timezone.utc)


def score_chats(db_path: str, top: int | None, min_score: float, topics: str | None):
    topic_filter = None
    if topics:
        parts = re.split(r"[,\s]+", topics.strip())
        topic_filter = re.compile("(" + "|".join(re.escape(p) for p in parts if p) + ")", re.IGNORECASE)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT chat_id, chat_name,
               COUNT(*)                              AS msg_count,
               COUNT(DISTINCT sender_id)             AS unique_senders,
               MIN(timestamp)                        AS first_msg,
               MAX(timestamp)                        AS last_msg,
               SUM(CASE WHEN content LIKE '%http%' THEN 1 ELSE 0 END) AS link_msgs
        FROM messages
        GROUP BY chat_id
        """
    ).fetchall()

    scored = []
    for r in rows:
        msg_count = r["msg_count"]
        if msg_count == 0:
            continue
        unique = r["unique_senders"] or 1
        last = datetime.fromisoformat(r["last_msg"].replace("Z", "+00:00"))
        age_days = max((NOW - last).total_seconds() / 86400.0, 0.0)

        recency = max(0.0, 100.0 - (age_days / 60.0) * 100.0)
        diversity = min(100.0, (unique / msg_count) * 300.0)
        links = r["link_msgs"] or 0
        link_density = min(100.0, (links / msg_count) * 200.0)

        c = sqlite3.connect(db_path)
        c.row_factory = sqlite3.Row
        contents = [row["content"] or "" for row in c.execute(
            "SELECT content FROM messages WHERE chat_id=?", (r["chat_id"],))]
        c.close()

        topic_hits = sum(1 for t in contents if TOPIC_RE.search(t))
        topic_density = min(100.0, (topic_hits / msg_count) * 150.0)

        rel_pct = 0.0
        if topic_filter is not None:
            rel_hits = sum(1 for t in contents if topic_filter.search(t))
            rel_pct = (rel_hits / msg_count) * 100.0
            topic_density = min(100.0, rel_pct * 2.0)

        NOISE_RE = re.compile(
            r"(prayer|loveworld|telecom|scribd|issuu|slideshare|downloader|"
            r"directors global|influencers|miracle|church|prophe|testimony|"
            r"earn money|crypto signal|forex|investment scheme|airdrop|"
            r"leak|premium course|dm admin|whatsapp group|t\.me/)",
            re.IGNORECASE,
        )
        noise_hits = sum(1 for t in contents if NOISE_RE.search(t))
        noise_ratio = noise_hits / msg_count

        balance_bonus = 10.0 if 0.05 < (unique / msg_count) < 0.8 else 0.0

        total = round(
            0.35 * recency + 0.25 * diversity + 0.20 * topic_density + 0.20 * link_density + balance_bonus,
            1,
        )
        if topic_filter is not None and rel_pct < 15.0:
            total = min(total, 30.0)
        if noise_ratio > 0.25:
            total = min(total, 25.0)

        scored.append({
            "chat_id": r["chat_id"], "chat_name": r["chat_name"], "msg_count": msg_count,
            "unique_senders": unique, "age_days": round(age_days, 1), "links": links,
            "topic_hits": topic_hits, "score": total,
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    if min_score:
        scored = [s for s in scored if s["score"] >= min_score]
    if top:
        scored = scored[:top]

    print(f"{'SCORE':>6}  {'VERDICT':<7}  {'MSGS':>5}  {'SND':>4}  {'AGE(d)':>7}  {'LK':>4}  {'TPC':>4}  CHAT")
    print("-" * 90)
    for s in scored:
        verdict = "USEFUL" if s["score"] >= 55 else ("OK" if s["score"] >= 35 else "NOISE")
        print(f"{s['score']:>6}  {verdict:<7}  {s['msg_count']:>5}  {s['unique_senders']:>4}  "
              f"{s['age_days']:>7}  {s['links']:>4}  {s['topic_hits']:>4}  {s['chat_name']}")
    print(f"\nTotal chats scored: {len(scored)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=None)
    ap.add_argument("--min-score", type=float, default=0.0)
    ap.add_argument("--topic", type=str, default=None,
                    help="Comma/space-separated research topics to boost relevance")
    ap.add_argument("--db", default=DB_PATH)
    args = ap.parse_args()
    if not Path(args.db).exists():
        raise SystemExit(f"DB not found at {args.db}. Run: tg-user sync-all -n 200")
    score_chats(args.db, args.top, args.min_score, args.topic)


if __name__ == "__main__":
    main()
