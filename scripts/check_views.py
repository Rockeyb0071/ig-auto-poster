"""
check_views.py
----------------
Runs on a schedule (every few hours). For every recent post that hasn't
already triggered a 1000-views alert, fetches its view count from the
Graph API Insights endpoint and notifies Telegram the first time it
crosses config.VIEW_MILESTONE.

Older posts (beyond VIEW_CHECK_WINDOW_DAYS) are skipped to save API calls.
"""

import json
import os
import sys
from datetime import datetime, timezone

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from telegram_utils import send_telegram_message

GRAPH_BASE = f"https://graph.facebook.com/{config.GRAPH_API_VERSION}"

# Metric name has changed across API versions/media types over time.
# Try them in order and use whichever the account/version actually supports.
METRIC_CANDIDATES = ["views", "impressions", "reach"]


def load_state():
    with open(config.STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    with open(config.STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def get_views(media_id: str):
    url = f"{GRAPH_BASE}/{media_id}/insights"
    for metric in METRIC_CANDIDATES:
        params = {"metric": metric, "access_token": config.IG_ACCESS_TOKEN}
        resp = requests.get(url, params=params, timeout=30)
        data = resp.json()
        values = data.get("data")
        if values:
            try:
                return values[0]["values"][0]["value"], metric
            except (KeyError, IndexError):
                continue
    return None, None


def is_within_window(posted_at_iso: str) -> bool:
    posted_at = datetime.fromisoformat(posted_at_iso)
    age_days = (datetime.now(timezone.utc) - posted_at).days
    return age_days <= config.VIEW_CHECK_WINDOW_DAYS


def main():
    state = load_state()
    posts = state.get("posts", [])
    changed = False

    for post in posts:
        if post.get("views_notified"):
            continue
        if not is_within_window(post["posted_at"]):
            continue

        views, metric_used = get_views(post["media_id"])
        if views is None:
            print(f"Could not fetch views for {post['media_id']}")
            continue

        print(f"{post['media_id']}: {views} ({metric_used})")

        if views >= config.VIEW_MILESTONE:
            send_telegram_message(
                config.TELEGRAM_BOT_TOKEN,
                config.TELEGRAM_CHAT_ID,
                f"🔥 Tumhare post ne {config.VIEW_MILESTONE}+ views paar kar liye!\n\n"
                f"👁️ Views: {views}\n📝 {post['quote']}\n🔗 {post['permalink']}",
            )
            post["views_notified"] = True
            changed = True

    if changed:
        save_state(state)
        print("state.json updated with new milestone notifications.")
    else:
        print("No new milestones crossed.")


if __name__ == "__main__":
    main()
