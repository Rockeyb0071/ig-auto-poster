"""
Central configuration for the Instagram auto-poster.
Edit the values in this file to change the look of the posts or the
caption/hashtags — no need to touch the other scripts.
"""

import os

# ---------- VISUAL THEME (dark aesthetic) ----------
IMG_SIZE = (1080, 1080)          # Instagram square post size
BG_TOP_COLOR = (8, 8, 14)        # near-black, top of gradient
BG_BOTTOM_COLOR = (20, 20, 38)   # deep indigo, bottom of gradient
TEXT_COLOR = (245, 245, 245)     # quote text (off-white)
ACCENT_COLOR = (202, 164, 93)    # muted gold accent line + tag
FOOTER_COLOR = (140, 140, 150)   # muted grey footer text

QUOTE_FONT_PATH = "fonts/BricolageGrotesque-Bold.ttf"
TAG_FONT_PATH = "fonts/WorkSans-Bold.ttf"
FOOTER_FONT_PATH = "fonts/WorkSans-Regular.ttf"

# Fallback system fonts if the bundled ones are ever missing
FALLBACK_FONTS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]

TAG_TEXT = "DAILY MOTIVATION"          # small label near the top
HANDLE_TEXT = "@yourhandle"            # shown at the bottom — EDIT to your real @handle

# ---------- CAPTION / HASHTAGS ----------
HASHTAGS = (
    "#motivation #motivationalquotes #discipline #mindset #selfimprovement "
    "#hustle #grindset #successmindset #dailymotivation #mentalstrength"
)

def build_caption(quote: str) -> str:
    return f"{quote}\n\nFollow for daily motivation. 🔥\n\n{HASHTAGS}"

# ---------- ACCOUNT / API SETTINGS (read from GitHub Actions secrets) ----------
IG_USER_ID = os.environ.get("IG_USER_ID", "")
IG_ACCESS_TOKEN = os.environ.get("IG_ACCESS_TOKEN", "")
IG_APP_ID = os.environ.get("IG_APP_ID", "")          # only needed for refresh_token.py
IG_APP_SECRET = os.environ.get("IG_APP_SECRET", "")  # only needed for refresh_token.py
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# The public repo, e.g. "rockey/ig-auto-poster" — used to build the raw image URL
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY", "")
GITHUB_BRANCH = os.environ.get("GITHUB_BRANCH", "main")

GRAPH_API_VERSION = "v21.0"

# View milestone that triggers a Telegram alert
VIEW_MILESTONE = 1000

# Stop checking a post's views after this many days (saves API calls)
VIEW_CHECK_WINDOW_DAYS = 21

STATE_FILE = "state.json"
QUOTES_FILE = "quotes.json"
POSTS_DIR = "posts"
