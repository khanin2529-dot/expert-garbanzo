# Setup: How to install the "fire" (badge) on Gift Up profiles

This repository now includes two approaches; choose one depending on what you can provide:

A) API client (recommended)
- Place your GiftUp API token in an environment variable: `GIFTUP_TOKEN`.
- Edit `GIFTUP_API_BASE` only if Gift Up provides a non-standard base URL.
- Run (dry run first):

```bash
python giftup_client.py username "🔥" --dry
# If output looks good, set GIFTUP_TOKEN and run without --dry
python giftup_client.py username "🔥"
```

B) Browser automation (fallback)
- Install Playwright and run browsers once:

```bash
pip install playwright
playwright install
```

- Set `GIFTUP_EMAIL` and `GIFTUP_PASSWORD` env vars (do NOT commit them).
- Run the script (adjust selectors if Gift Up UI changed):

```bash
python giftup_automation.py --badge "🔥"
```

Security notes
- Never paste credentials into public chat.
- Use environment variables or secrets store (GitHub Secrets) when automating.
- Prefer API token over full password where possible.

If you want, provide one of the following and I will proceed to run (or guide you to run):
- `GIFTUP_TOKEN` (I will run API client in repo environment), or
- `GIFTUP_EMAIL` + `GIFTUP_PASSWORD` (I will provide an automation script for you to run locally), or
- I can only provide the scripts and you will run them locally.
