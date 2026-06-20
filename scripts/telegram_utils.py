"""
telegram_utils.py
------------------
Tiny helper to send a message through a Telegram bot.
Create a bot with @BotFather and get your chat_id (see SETUP.md) before use.
"""

import requests


def send_telegram_message(bot_token: str, chat_id: str, text: str) -> bool:
    if not bot_token or not chat_id:
        print("Telegram bot token or chat id missing — skipping notification.")
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": False,
    }
    try:
        resp = requests.post(url, data=payload, timeout=20)
        resp.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"Telegram send failed: {e}")
        return False
