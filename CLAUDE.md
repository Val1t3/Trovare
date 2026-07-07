# Trovare

## Project Description

Trovare is a Discord chatbot that helps 2 users find apartments. It combines three capabilities:

1. **On-demand analysis** — the user sends a listing URL in Discord, the bot scrapes the page, analyzes the listing with Claude (match against criteria, price quality, scam risks) and returns a structured summary.
2. **Interactive chat** — the user can freely converse with the bot to compare listings, ask questions, update search criteria, or manage their saved listings.
3. **Automated watch** — twice a day (noon and evening), the bot scrapes a configured list of sites, filters new listings against the criteria, and sends a digest to Discord.

The project runs on a Linux VPS (Ubuntu 24) or on MacOS locally. No web interface, no dashboard — Discord is the only user interface.

---

## Tech Stack

| Layer                | Technology                    | Role                                                                   |
| -------------------- | ----------------------------- | ---------------------------------------------------------------------- |
| API & server         | FastAPI + Uvicorn             | App host, internal REST routes                                         |
| Discord bot          | discord.py                    | Receive/send messages via the gateway (integrated in the app lifespan) |
| LLM chat             | anthropic SDK — Haiku 4.5     | Interactive chat, intent classification, watch filtering (lower cost)  |
| LLM analysis         | anthropic SDK — Sonnet 4.6    | Deep listing analysis (future work)                                    |
| Scheduling           | APScheduler                   | Automated jobs integrated into FastAPI                                 |
| Conversation context | JSON file (data/context.json) | Shared chat history across both users, capped at 20 messages           |
| Database             | SQLite + aiosqlite            | Store listings, metadata (future work)                                 |
| Criteria config      | criteria.json                 | Search criteria editable without redeployment                          |
| Environment          | python-dotenv                 | Sensitive variables (.env)                                             |
| Package manager      | uv                            | Fast Python package & project manager                                  |

**Python version**: 3.14

---

## Project Structure

```
trovare/
├── api/
│   ├── main.py              # FastAPI app, Discord bot lifecycle (gateway client)
│   ├── scheduler.py         # APScheduler — noon/evening jobs
│   └── routes/
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
│   ├── classifier.py        # Intent classification (Haiku) → JSON (future work)
│   ├── analyzer.py          # Full listing analysis (Sonnet, future work)
│   ├── filter.py            # Fast watch filtering (Haiku, future work)
│   ├── client.py            # Anthropic Haiku wiring for interactive chat
│   └── prompts.py           # Centralized prompt templates
│
├── storage/
│   ├── db.py                # SQLite init, aiosqlite connection pool (future work)
│   ├── listings.py          # Listings CRUD (future work)
│   ├── models.py            # Dataclasses: ContextMessage (Listing/Analysis future work)
│   └── context.py           # Shared JSON-backed chat history (data/context.json)
│
├── commands/
│   ├── params.py            # CommandParameter — single nullable-field argument for all command handlers
│   └── new.py               # /new — reset the shared conversation context
│
├── bot/
│   ├── discord_bot.py       # discord.py gateway client + on_message handler
│   ├── dispatcher.py        # Message routing → command/chat handler
│   ├── handlers.py          # handle_command() routing table + handle_chat() (LLM chat)
│   └── formatter.py         # Discord response formatting (Markdown, future work)
│
├── criteria.yaml            # Search criteria (see dedicated section, future work)
├── .env                     # Environment variables (do not commit)
├── .env.example             # .env template without sensitive values
├── requirements.txt
└── CLAUDE.md                # This file
```

---

## Main Message Flow

```
Discord (gateway)
  └─→ bot/discord_bot.py on_message (allow-listed channels)
        └─→ bot/dispatcher.py
              ├─→ /cmd command → bot/handlers.py:handle_command()
              │     └─→ commands/<name>.py handler(CommandParameter) — e.g. /new
              └─→ free text → bot/handlers.py:handle_chat()
                    └─→ llm/client.py (Haiku) + storage/context.py (shared history, capped at 20)
                          └─→ Discord channel reply
```

Intent classification (`llm/classifier.py`) and the routed intents in the table
below are not implemented yet — all free text currently goes straight to
general chat. The full intent-routed flow (`ANALYZE_URL`, `CRITERIA_*`,
`LISTING_*`, etc.) is future work.

---

## Discord Commands

The bot responds to every message posted in the allow-listed channels
(`DISCORD_ALLOWED_CHANNEL_IDS`).

### Explicit commands (no LLM)

| Command | Description                                                                                        |
| ------- | -------------------------------------------------------------------------------------------------- |
| `/new`  | Reset the shared conversation history (also auto-resets at 20 messages, with a warning beforehand) |
| `/help` | Full list of commands and recognized intents                                                       |

### Natural language intents (Claude classifies)

| Intent            | Examples                                      |
| ----------------- | --------------------------------------------- |
| `ANALYZE_URL`     | Sending a listing URL                         |
| `COMPARE`         | "Compare the last 3 listings"                 |
| `DETAIL`          | "Are there any red flags on this one?"        |
| `CRITERIA_ADD`    | "Add Vincennes to my cities"                  |
| `CRITERIA_REMOVE` | "Remove the balcony requirement"              |
| `CRITERIA_UPDATE` | "Raise the max rent to €1,600"                |
| `CRITERIA_READ`   | "What are my current criteria?"               |
| `LISTING_TAG`     | "Mark the last one as interesting"            |
| `LISTING_DELETE`  | "Delete the Montreuil listing"                |
| `LISTING_FILTER`  | "Show apartments with a balcony under €1,200" |
| `SCHEDULE_UPDATE` | "Move the evening watch to 8pm"               |
| `SITE_ADD`        | "Add logic-immo.com to the watch list"        |
| `GENERAL_CHAT`    | Anything else                                 |

**Confirmation rule**: any write operation (PATCH/DELETE) triggers a reformulation by the bot before execution. Listing tags (non-destructive) are the only exception.

---

## criteria.yaml

```yaml
max_rent: 1400 # €/month all charges included
min_surface: 35 # m²
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
# Discord
DISCORD_BOT_TOKEN=            # Bot token from the Discord developer portal
DISCORD_ALLOWED_CHANNEL_IDS= # Authorized Discord channel IDs, comma-separated

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
# Python 3.14
python --version

# uv (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Playwright (Chromium for JS scraping)
uv pip install playwright
playwright install chromium
playwright install-deps chromium
```

### Run

Runs the app locally in the same environment as production (Python 3.14 + uv,
served by uvicorn on port 8000). Requires a filled-in `.env` (see the
Environment Variables section).

```bash
# Build and start in the background
docker compose up --build -d

# Follow logs
docker compose logs -f

# Health check
curl localhost:8000/health        # -> {"status":"ok"}

# Stop and remove the container
docker compose down

# Rebuild after changing dependencies (pyproject.toml / uv.lock)
docker compose build --no-cache
```

The SQLite database is persisted on the host via the `./data` volume.
The image is production-like: no hot reload and the source is not mounted, so
rebuild (`docker compose up --build`) to pick up code changes.

---

## Code Conventions

- **Async everywhere**: all I/O functions (DB, HTTP, LLM) must be `async def`
- **Strict typing**: all functions must have type annotations
- **Dataclasses** for data models (no Pydantic outside of FastAPI route schemas)
- **Prompts**: all templates in `llm/prompts.py`, never inline in business logic
- **No print statements**: use `logging` (level configured via `LOG_LEVEL` in `.env`)
- **Secrets**: only via `os.getenv()`, never hardcoded
