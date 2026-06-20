"""
post_to_instagram.py
---------------------
Publishes an already-generated image to Instagram using the official
Meta Graph API (Content Publishing flow):
  1. Create a media container from a public image URL.
  2. Publish that container.
  3. Fetch the resulting permalink.

The image must already be live at a public URL before this runs — the
daily workflow commits/pushes posts/*.png to GitHub first, then calls
this script with the resulting raw.githubusercontent.com URL.
"""

import sys
import time
import os

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

GRAPH_BASE = f"https://graph.facebook.com/{config.GRAPH_API_VERSION}"


class InstagramPostError(Exception):
    pass


def create_media_container(image_url: str, caption: str) -> str:
    url = f"{GRAPH_BASE}/{config.IG_USER_ID}/media"
    params = {
        "image_url": image_url,
        "caption": caption,
        "access_token": config.IG_ACCESS_TOKEN,
    }
    resp = requests.post(url, params=params, timeout=60)
    data = resp.json()
    if "id" not in data:
        raise InstagramPostError(f"Failed to create media container: {data}")
    return data["id"]


def publish_container(creation_id: str) -> str:
    url = f"{GRAPH_BASE}/{config.IG_USER_ID}/media_publish"
    params = {
        "creation_id": creation_id,
        "access_token": config.IG_ACCESS_TOKEN,
    }
    resp = requests.post(url, params=params, timeout=60)
    data = resp.json()
    if "id" not in data:
        raise InstagramPostError(f"Failed to publish media: {data}")
    return data["id"]


def get_permalink(media_id: str) -> str:
    url = f"{GRAPH_BASE}/{media_id}"
    params = {"fields": "permalink", "access_token": config.IG_ACCESS_TOKEN}
    resp = requests.get(url, params=params, timeout=30)
    data = resp.json()
    return data.get("permalink", "")


def post_image(image_url: str, caption: str) -> dict:
    """Full flow: create container -> wait for it to be ready -> publish."""
    creation_id = create_media_container(image_url, caption)

    # IG sometimes needs a moment to fetch/process the image before publish.
    time.sleep(8)

    media_id = publish_container(creation_id)
    permalink = get_permalink(media_id)
    return {"media_id": media_id, "permalink": permalink}


if __name__ == "__main__":
    # Manual test: python3 scripts/post_to_instagram.py <image_url> "<caption>"
    if len(sys.argv) < 3:
        print("Usage: post_to_instagram.py <image_url> <caption>")
        sys.exit(1)
    result = post_image(sys.argv[1], sys.argv[2])
    print(result)
