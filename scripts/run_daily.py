"""
run_daily.py
-------------
Runs AFTER scripts/generate_post.py has already created today's image
AND that image has been git-pushed to the repo (so it has a public
raw.githubusercontent.com URL that Instagram's servers can fetch).

Steps:
  1. Find today's image + quote text in posts/.
  2. Build the public image URL and caption.
  3. Publish to Instagram via the Graph API.
  4. Send a "post is live" message to Telegram.
  5. Record the new post in state.json so check_views.py can track it.
"""

import glob
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from telegram_utils import send_telegram_message
from post_to_instagram import post_image, InstagramPostError


def load_state():
    with open(config.STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    with open(config.STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def latest_post_image():
    files = sorted(glob.glob(os.path.join(config.POSTS_DIR, "post_*.png")))
    if not files:
        raise FileNotFoundError("No generated post image found in posts/. Run generate_post.py first.")
    return files[-1]


def main():
    image_path = latest_post_image()
    filename = os.path.basename(image_path)

    quote_path = os.path.join(config.POSTS_DIR, "latest_quote.txt")
    with open(quote_path, "r", encoding="utf-8") as f:
        quote = f.read().strip()

    if not config.GITHUB_REPOSITORY:
        print("GITHUB_REPOSITORY env var not set — cannot build public image URL.")
        sys.exit(1)

    image_url = (
        f"https://raw.githubusercontent.com/{config.GITHUB_REPOSITORY}/"
        f"{config.GITHUB_BRANCH}/{config.POSTS_DIR}/{filename}"
    )
    caption = config.build_caption(quote)

    print(f"Publishing {filename} to Instagram...")
    try:
        result = post_image(image_url, caption)
    except InstagramPostError as e:
        send_telegram_message(
            config.TELEGRAM_BOT_TOKEN,
            config.TELEGRAM_CHAT_ID,
            f"⚠️ Aaj ka Instagram post FAIL ho gaya:\n{e}",
        )
        raise

    permalink = result["permalink"] or "(permalink not returned yet)"
    print(f"Published! media_id={result['media_id']} permalink={permalink}")

    send_telegram_message(
        config.TELEGRAM_BOT_TOKEN,
        config.TELEGRAM_CHAT_ID,
        f"✅ Aaj ka post upload ho gaya!\n\n📝 {quote}\n\n🔗 {permalink}",
    )

    state = load_state()
    state.setdefault("posts", []).append({
        "media_id": result["media_id"],
        "permalink": permalink,
        "quote": quote,
        "posted_at": datetime.now(timezone.utc).isoformat(),
        "views_notified": False,
    })
    save_state(state)
    print("state.json updated.")


if __name__ == "__main__":
    main()
