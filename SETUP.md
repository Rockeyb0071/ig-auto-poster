# Setup Guide — Instagram Auto-Poster

One-time setup (~30-45 minutes). After this, everything runs by itself:
a new post every day at 7:00 AM IST, a Telegram message when it's live,
and another Telegram alert the first time a post crosses 1000 views.

This uses Meta's **official** Graph API (not any unofficial bot), so your
account stays safe and policy-compliant.

---

## What you need before starting
- Your Instagram account already set as Business/Creator and linked to a
  Facebook Page ✅ (you already have this)
- A GitHub account (free)
- A Telegram account

---

## Step 1 — Create a Meta App and get your access token

1. Go to https://developers.facebook.com/ → **My Apps** → **Create App**.
   Choose the **"Other"** → **"Business"** app type.
2. Inside your app, add the **Instagram Graph API** product (search for it
   under "Add Products").
3. Go to https://developers.facebook.com/tools/explorer/
   - Select your app from the dropdown.
   - Click **"Get Token" → "Get User Access Token"**.
   - Tick these permissions: `instagram_basic`, `instagram_content_publish`,
     `instagram_manage_insights`, `pages_show_list`, `pages_read_engagement`,
     `business_management`.
   - Generate the token.
4. In the Explorer, run: `GET /me/accounts` → copy your **Page ID** from
   the result.
5. Run: `GET /{page-id}?fields=instagram_business_account` (replace
   `{page-id}`) → this returns your **IG_USER_ID**. Save it.
6. Exchange the short-lived token (1 hour) for a **long-lived token**
   (~60 days). In a browser or the Explorer, call:
   ```
   GET https://graph.facebook.com/v21.0/oauth/access_token
     ?grant_type=fb_exchange_token
     &client_id={YOUR_APP_ID}
     &client_secret={YOUR_APP_SECRET}
     &fb_exchange_token={SHORT_LIVED_TOKEN}
   ```
   App ID/Secret are on your app's **Settings → Basic** page. The response
   gives you your **IG_ACCESS_TOKEN**.
7. Submit your app for **App Review** requesting `instagram_content_publish`
   and `instagram_manage_insights` (needed for posting + view counts on a
   live app). While in development mode, the app only works for accounts
   added as Admin/Developer/Tester on the app — which is fine if it's just
   your own account.

Meta's exact developer-console screens shift around sometimes — if a button
name above doesn't match what you see, search "Instagram Graph API content
publishing" on https://developers.facebook.com/docs/ for the current steps;
the IDs/tokens you need stay the same.

**Save these 4 values somewhere safe**: `IG_USER_ID`, `IG_ACCESS_TOKEN`,
`IG_APP_ID`, `IG_APP_SECRET` (the last two are only needed for Step 6 below).

---

## Step 2 — Create your Telegram bot

1. In Telegram, message **@BotFather** → send `/newbot` → follow prompts →
   copy the **bot token** it gives you (`TELEGRAM_BOT_TOKEN`).
2. Send any message to your new bot (e.g. "hi") so it can message you back.
3. Message **@userinfobot** (or visit
   `https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/getUpdates` after
   step 2) to get your numeric **chat ID** (`TELEGRAM_CHAT_ID`).

---

## Step 3 — Put this project on GitHub

1. Create a new **public** repo on GitHub (it needs to be public so
   `raw.githubusercontent.com` image links work for Instagram to fetch —
   the repo only contains quote images/text, nothing private).
2. Upload everything from this folder to that repo (drag-and-drop on
   GitHub's web UI works fine, or `git init && git add . && git commit -m "init" && git push`).

---

## Step 4 — Add your secrets

In your repo: **Settings → Secrets and variables → Actions → New repository secret**.
Add each of these:

| Secret name | Value |
|---|---|
| `IG_USER_ID` | from Step 1 |
| `IG_ACCESS_TOKEN` | from Step 1 |
| `TELEGRAM_BOT_TOKEN` | from Step 2 |
| `TELEGRAM_CHAT_ID` | from Step 2 |
| `IG_APP_ID` | from Step 1 (only needed for Step 6) |
| `IG_APP_SECRET` | from Step 1 (only needed for Step 6) |

---

## Step 5 — Turn it on and test

1. Go to the **Actions** tab of your repo → enable workflows if prompted.
2. Open **"Daily Instagram Post"** → **Run workflow** (this is the manual
   trigger — use it now to test instead of waiting for 7 AM).
3. Watch the run. If it succeeds, check your Instagram and Telegram.
4. From tomorrow, it runs automatically every day at 7:00 AM IST — no
   action needed from you.

GitHub's free scheduler can occasionally run a few minutes late during
high-traffic periods — this is normal and not a bug.

---

## Step 6 — True zero-maintenance token refresh (optional but recommended)

Your `IG_ACCESS_TOKEN` is valid for ~60 days. Without this step, you'll
need to repeat Step 1.6 manually every couple of months, or the daily
posting will silently stop working.

To automate this too:
1. Go to https://github.com/settings/tokens → **Generate new token
   (classic)** → scope: `repo` → copy it.
2. Add it as a repo secret named `ADMIN_PAT`.
3. That's it — the **"Refresh Instagram Token"** workflow now runs every
   Sunday and keeps `IG_ACCESS_TOKEN` fresh automatically, with a Telegram
   alert if it ever fails.

If you skip this step, just re-do Step 1.6 every ~50 days and update the
`IG_ACCESS_TOKEN` secret manually — takes 2 minutes.

---

## Customizing

- **Quotes**: edit `quotes.json` — add as many lines as you want, plain
  English sentences in quotes, comma-separated.
- **Look**: edit `config.py` — colors, your real `HANDLE_TEXT`, hashtags,
  caption format.
- **Posting time**: edit the `cron` line in
  `.github/workflows/daily-post.yml` (times are in UTC; IST = UTC + 5:30).
- **View milestone**: change `VIEW_MILESTONE` in `config.py` (e.g. 5000
  instead of 1000).

---

## Troubleshooting

- **"Failed to create media container"**: usually an expired/invalid
  token (redo Step 1.6) or the image URL isn't public yet (check the repo
  is Public, not Private).
- **No views data returned**: very new accounts/posts sometimes take a
  few hours before Insights data is available — this is normal.
- **Telegram message never arrives**: confirm you sent the bot a message
  first (Step 2.2) — bots can't message you until you've messaged them.
- **Workflow shows red ❌**: click into the run → it prints the exact
  API error message from Meta or Telegram.

---

## Cost
₹0. GitHub Actions free tier (2,000 minutes/month — this uses a tiny
fraction of that), Meta Graph API (free), Telegram Bot API (free).
