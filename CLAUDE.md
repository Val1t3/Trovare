# Trovare

## Project Description

Trovare is a Telegram chatbot that helps 2 users find apartments. It combines three capabilities:

1. **On-demand analysis** — the user sends a listing URL in Telegram, the bot scrapes the page, analyzes the listing with Claude (match against criteria, price quality, scam risks) and returns a structured summary.
2. **Interactive chat** — the user can freely converse with the bot to compare listings, ask questions, update search criteria, or manage their saved listings.
3. **Automated watch** — twice a day (noon and evening), the bot scrapes a configured list of sites, filters new listings against the criteria, and sends a digest to Telegram.

The project runs on a Linux VPS (Ubuntu 24) or on MacOS locally. No web interface, no dashboard — Telegram is the only user interface.

---

## Tech Stack

| Layer | Technology | Role |
|---|---|---|
| API & server | FastAPI + Uvicorn | Telegram webhook entry point, internal REST routes |
| Telegram bot | python-telegram-bot | Receive/send messages via webhook |
| LLM analysis | anthropic SDK — Sonnet 4.6 | Deep listing analysis, conversational chat |
| LLM filtering | anthropic SDK — Haiku 4.5 | Intent classification, watch filtering (lower cost) |
| Scheduling | APScheduler | Automated jobs integrated into FastAPI |
| Database | SQLite + aiosqlite | Store listings, conversation history, metadata |
| Criteria config | criteria.json | Search criteria editable without redeployment |
| Environment | python-dotenv | Sensitive variables (.env) |
| Package manager | uv | Fast Python package & project manager |

**Python version**: 3.11+

---

## Project Structure

```
trovare/
├── api/
│   ├── main.py              # FastAPI app, Telegram webhook registration
│   ├── scheduler.py         # APScheduler — noon/evening jobs
│   └── routes/
│       ├── telegram.py      # POST /telegram — main webhook
│       ├── analyze.py       # POST /analyze — analyze a listing URL
│       ├── chat.py          # POST /chat — conversation
│       ├── criteria.py      # GET|PATCH /criteria — read/write criteria
│       ├── listings.py      # GET|PATCH|DELETE /listings — listing management
│       ├── watch.py         # POST /watch — trigger manual watch
│       └── stats.py         # GET /stats — usage metrics
│
├── scrapers/
│   ├── base.py              # Abstract BaseScraper class
│   ├── leboncoin.py         # Leboncoin scraper (playwright)
│   ├── pap.py               # PAP scraper (requests + bs4)
│   └── seloger.py           # SeLoger scraper (playwright)
│
├── llm/
│   ├── classifier.py        # Intent classification (Haiku) → JSON
│   ├── analyzer.py          # Full listing analysis (Sonnet)
│   ├── filter.py            # Fast watch filtering (Haiku)
│   └── prompts.py           # Centralized prompt templates
│
├── storage/
│   ├── db.py                # SQLite init, aiosqlite connection pool
│   ├── models.py            # Dataclasses: Listing, Analysis, Conversation
│   ├── listings.py          # Listings CRUD
│   └── conversations.py     # Conversation history per chat_id
│
├── bot/
│   ├── dispatcher.py        # Message routing → intent → handler
│   ├── handlers.py          # Handlers for each intent/command
│   └── formatter.py         # Telegram response formatting (Markdown)
│
├── criteria.yaml            # Search criteria (see dedicated section)
├── .env                     # Environment variables (do not commit)
├── .env.example             # .env template without sensitive values
├── requirements.txt
└── CLAUDE.md                # This file
```

---

## Main Message Flow

```
Telegram
  └─→ POST /telegram (webhook)
        └─→ bot/dispatcher.py
              ├─→ /cmd command → direct handler (no LLM)
              └─→ free text
                    └─→ llm/classifier.py (Haiku) → intent + JSON params
                          ├─→ ANALYZE_URL   → scrapers/ + llm/analyzer.py
                          ├─→ CRITERIA_*    → storage/ + confirmation → criteria.yaml
                          ├─→ LISTING_*     → storage/listings.py
                          ├─→ COMPARE/DETAIL → storage/ + llm/analyzer.py
                          └─→ GENERAL_CHAT  → llm/analyzer.py + history
                                └─→ bot/formatter.py → Telegram response
```

---

## Telegram Commands

### Explicit commands (no LLM)

| Command | Description |
|---|---|
| `/start` | Welcome message, list of available commands |
| `/criteria` | Display current criteria in readable format |
| `/listings [n]` | Show the n most recent listings (default: 10) |
| `/watch` | Trigger an immediate manual watch |
| `/stats` | Today's metrics (listings seen, estimated API cost) |
| `/reset` | Reset the current conversation history |
| `/help` | Full list of commands and recognized intents |

### Natural language intents (Claude classifies)

| Intent | Examples |
|---|---|
| `ANALYZE_URL` | Sending a listing URL |
| `COMPARE` | "Compare the last 3 listings" |
| `DETAIL` | "Are there any red flags on this one?" |
| `CRITERIA_ADD` | "Add Vincennes to my cities" |
| `CRITERIA_REMOVE` | "Remove the balcony requirement" |
| `CRITERIA_UPDATE` | "Raise the max rent to €1,600" |
| `CRITERIA_READ` | "What are my current criteria?" |
| `LISTING_TAG` | "Mark the last one as interesting" |
| `LISTING_DELETE` | "Delete the Montreuil listing" |
| `LISTING_FILTER` | "Show apartments with a balcony under €1,200" |
| `SCHEDULE_UPDATE` | "Move the evening watch to 8pm" |
| `SITE_ADD` | "Add logic-immo.com to the watch list" |
| `GENERAL_CHAT` | Anything else |

**Confirmation rule**: any write operation (PATCH/DELETE) triggers a reformulation by the bot before execution. Listing tags (non-destructive) are the only exception.

---

## criteria.yaml

```yaml
max_rent: 1400            # €/month all charges included
min_surface: 35           # m²
min_rooms: 2
cities:
  - Paris 11th
  - Paris 12th
  - Montreuil
must_have:
  - furnished
nice_to_have:
  - balcony
  - parking
exclusions:
  - "no elevator above 3rd floor"
sites:
  - leboncoin.fr
  - pap.fr
  - seloger.com
schedule:
  noon: "12:00"
  evening: "19:30"
```

This file is read on every request (no cache) so bot modifications take effect immediately. The bot can edit it via `PATCH /criteria` after user confirmation.

---

## Environment Variables (.env)

```bash
# Telegram
TELEGRAM_BOT_TOKEN=         # Token from @BotFather
TELEGRAM_WEBHOOK_URL=       # Public VPS URL, e.g. https://myvps.com/telegram
TELEGRAM_ALLOWED_CHAT_IDS=  # Authorized Telegram chat IDs, comma-separated

# Anthropic
ANTHROPIC_API_KEY=          # Anthropic API key (console.anthropic.com)

# App
ENV=production              # production | development
LOG_LEVEL=INFO
PORT=8000
```

---

## Installation & Setup

### Prerequisites

```bash
# Python 3.11+
python --version

# uv (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Playwright (Chromium for JS scraping)
uv pip install playwright
playwright install chromium
playwright install-deps chromium
```

### Install

```bash
git clone <repo> trovare
cd trovare

# uv automatically creates a virtual environment
uv sync

cp .env.example .env
# Fill in variables in .env

# Initialize the SQLite database
uv run python -c "from storage.db import init_db; import asyncio; asyncio.run(init_db())"
```

### Run in development

```bash
# Start the API with hot reload
uv run uvicorn api.main:app --reload --port 8000

# Expose locally with ngrok (to test the Telegram webhook)
ngrok http 8000
# Then update TELEGRAM_WEBHOOK_URL in .env with the ngrok URL
```

### Register the Telegram webhook

```bash
# Run this after any public URL change
uv run python -c "
import asyncio
from telegram import Bot
from dotenv import load_dotenv
import os
load_dotenv()
async def set_webhook():
    bot = Bot(os.getenv('TELEGRAM_BOT_TOKEN'))
    await bot.set_webhook(os.getenv('TELEGRAM_WEBHOOK_URL'))
    print('Webhook registered')
asyncio.run(set_webhook())
"
```

### Run in production (systemd)

```bash
# Copy the service file
sudo cp deploy/trovare.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable trovare
sudo systemctl start trovare

# Follow logs
journalctl -u trovare -f
```

### deploy/trovare.service

```ini
[Unit]
Description=Trovare FastAPI
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/trovare
EnvironmentFile=/opt/trovare/.env
ExecStart=/opt/trovare/venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

---

## Code Conventions

- **Async everywhere**: all I/O functions (DB, HTTP, LLM) must be `async def`
- **Strict typing**: all functions must have type annotations
- **Dataclasses** for data models (no Pydantic outside of FastAPI route schemas)
- **Prompts**: all templates in `llm/prompts.py`, never inline in business logic
- **No print statements**: use `logging` (level configured via `LOG_LEVEL` in `.env`)
- **Secrets**: only via `os.getenv()`, never hardcoded

---

## Security

- Validate `chat_id` on every incoming Telegram message: only IDs listed in `TELEGRAM_ALLOWED_CHAT_IDS` are accepted. Silently reject all others.
- Never log tokens, API keys, or user message contents.
- The FastAPI webhook must be served over HTTPS (nginx + Let's Encrypt recommended).

---

## LLM Models — Usage Rules

| Model | Use case | Reason |
|---|---|---|
| `claude-haiku-4-5-20251001` | Intent classification, watch filtering, deduplication | Fast, cheap, simple task |
| `claude-sonnet-4-6` | Listing analysis, conversational chat, comparison | Better comprehension, rich context |

Never use Sonnet for intent classification — Haiku is sufficient and 3x cheaper. Never use Haiku for the final listing analysis — quality matters there.

---

## Project Status

- [ ] Base FastAPI structure + Telegram webhook
- [ ] Intent classifier (Haiku)
- [ ] PAP scraper (requests + bs4)
- [ ] Leboncoin scraper (playwright)
- [ ] SeLoger scraper (playwright)
- [ ] Listing analyzer (Sonnet)
- [ ] Listings CRUD SQLite
- [ ] criteria.yaml read/write via bot
- [ ] Automated watch (APScheduler)
- [ ] Telegram response formatting
- [ ] systemd VPS deployment
