# Instagram Auto-Poster — Daily Dark-Theme Motivation

Fully automated Instagram content agent:
- Generates a new dark-theme, English motivational quote image every day
  (no repeats until all ~110 quotes have been used, then reshuffles).
- Publishes it to your Instagram automatically at **7:00 AM IST**.
- Sends you a **Telegram message** the moment it's live.
- Sends another **Telegram alert** the first time that post crosses
  **1000 views**.
- Runs on GitHub Actions' free scheduler — no server, no PC left running,
  nothing for you to click each day.

➡️ **Start here: [SETUP.md](./SETUP.md)** — one-time setup, ~30-45 minutes.

## How it works
```
7:00 AM IST daily
   └─ generate_post.py   → picks a quote, renders posts/post_<date>.png
   └─ (pushed to GitHub) → image now has a public URL
   └─ run_daily.py        → publishes to Instagram via Graph API
                           → sends "post is live" Telegram message
                           → records the post in state.json

Every 4 hours
   └─ check_views.py      → checks view counts on recent posts
                           → sends a Telegram alert the first time
                             any post crosses 1000 views

Every Sunday (optional)
   └─ refresh_token.py    → keeps your Instagram access token from expiring
```

## Project structure
```
quotes.json          → the quote bank (edit freely to add more)
config.py            → colors, handle, hashtags, view milestone, etc.
state.json           → tracks quote rotation + posted media (auto-managed)
fonts/               → open-license fonts used in the generated images
scripts/
  generate_post.py   → builds the image
  post_to_instagram.py → Graph API publish flow
  check_views.py     → view-count milestone checker
  refresh_token.py   → optional token auto-refresh
  run_daily.py        → ties generation + posting + Telegram together
.github/workflows/   → the 3 scheduled GitHub Actions
```

Built on Meta's official Instagram Graph API and Telegram's official Bot
API — no unofficial bots, no ToS-violating automation, no risk to your
account.
