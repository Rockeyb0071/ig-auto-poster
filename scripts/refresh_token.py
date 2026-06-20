"""
refresh_token.py
------------------
Your IG_ACCESS_TOKEN is a long-lived Facebook token tied to your Page
(valid roughly 60 days). This re-exchanges it for a fresh long-lived
token using the same fb_exchange_token method you used to get it in
the first place -- keeping everything on graph.facebook.com, consistent
with post_to_instagram.py and check_views.py.

This must run on a schedule at LEAST once every ~55 days (the
refresh-token.yml workflow runs it weekly, well within that window).

Note: this only fully automates if you've set up the ADMIN_PAT secret
described in SETUP.md. Without it, refresh manually every ~2 months --
see SETUP.md "Token maintenance" section.
"""

import os
import sys

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

GRAPH_BASE = f"https://graph.facebook.com/{config.GRAPH_API_VERSION}"


def refresh_token(current_token: str) -> dict:
    if not config.IG_APP_ID or not config.IG_APP_SECRET:
        raise RuntimeError(
            "IG_APP_ID / IG_APP_SECRET not set. These are required for token refresh "
            "-- see SETUP.md Step 6."
        )
    url = f"{GRAPH_BASE}/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": config.IG_APP_ID,
        "client_secret": config.IG_APP_SECRET,
        "fb_exchange_token": current_token,
    }
    resp = requests.get(url, params=params, timeout=30)
    data = resp.json()
    if "access_token" not in data:
        raise RuntimeError(f"Token refresh failed: {data}")
    return data


if __name__ == "__main__":
    result = refresh_token(config.IG_ACCESS_TOKEN)
    # Printed so the workflow step can capture it as $NEW_TOKEN
    print(result["access_token"])
