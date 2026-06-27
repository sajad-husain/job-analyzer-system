# Job Analyzer System

An automated job monitoring and notification system that scrapes job listings every 30 seconds, filters them based on deadline conflicts and pay rate thresholds, and sends alerts via Telegram.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [File-by-File Reference](#file-by-file-reference)
3. [Setup](#setup)
4. [Running the System](#running-the-system)
5. [Logging & Debugging](#logging--debugging)
6. [Common Errors & Fixes](#common-errors--fixes)
7. [Environment Variables](#environment-variables)
8. [Missing / Planned Modules](#missing--planned-modules)
9. [Flow Diagram](#flow-diagram)

---

## Architecture Overview

```
┌─────────────┐    ┌──────────────┐    ┌───────────────┐    ┌──────────────────┐
│  main.py    │───▶│  scheduler/  │───▶│  scraper/     │───▶│  analyzer/       │
│ (entrypoint)│    │  job_scheduler│    │  dashboard_   │    │  deadline_checker│
└─────────────┘    │  .py         │    │  scraper.py   │    │  .py             │
                   └──────────────┘    └───────────────┘    └────────┬─────────┘
                                           │                         │
                                           ▼                         ▼
                                    ┌──────────────┐        ┌──────────────┐
                                    │  Telegram Bot │        │  calendar.json│
                                    │  (notifications│       │  (persisted)  │
                                    │  /telegram_bot│        └──────────────┘
                                    │  .py)         │
                                    └──────────────┘
```

**Data flow:**

1. `main.py` starts the `JobMonitorScheduler` and runs an infinite async loop.
2. Every 30 seconds, the scheduler calls `DashboardScraper.fetch_new_jobs()`.
3. Each job is checked against already-processed IDs (tracked in-memory via a `set`).
4. `DeadlineChecker.has_conflict()` verifies the deadline does not fall within 2 days of existing commitments.
5. Jobs below the $25/hour pay threshold are discarded.
6. Remaining jobs are sent via `TelegramNotifier.send_alerts()` (formatted HTML messages).

---

## File-by-File Reference

### `main.py` — Application Entry Point

```python
# Startup sequence (lines 17-44):
# 1. Initialize WordMacroHandler    ← FAILS if word_automation/ missing
# 2. Initialize EditGPTClient       ← FAILS if ai_integration/ missing
# 3. Start JobMonitorScheduler      ← Runs every 30s
# 4. Keep alive via asyncio.sleep(1)
```

- **Logs:** Writes to both `logs/system.log` and stdout.
- **Shutdown:** Catches `KeyboardInterrupt` and calls `scheduler.shutdown()`.

### `scheduler/job_scheduler.py` — 30-Second Job Monitor

Key class: `JobMonitorScheduler`

| Method | Purpose |
|--------|---------|
| `__init__` | Creates `AsyncIOScheduler`, `DashboardScraper`, `DeadlineChecker`, `TelegramNotifier`, and an empty `processed_jobs` set |
| `monitor_jobs()` | Core cycle: scrape → filter (by ID, deadline conflict, pay rate) → notify |
| `get_min_pay_threshold()` | Returns `25.0` (hardcoded minimum $/hour) |
| `start()` | Adds the interval job (30s), starts scheduler, triggers an immediate first run |

**Debug tip:** `processed_jobs` is an in-memory `set()`. If the process restarts, all previously seen jobs are re-evaluated.

### `scraper/dashboard_scraper.py` — Job Listings Scraper

- **Current state:** Returns **mock data** (3 hardcoded jobs — Technical Writer, Content Editor, Grant Writer).
- **Planned:** `_scrape_dashboard()` contains commented-out `aiohttp` + `BeautifulSoup` logic for real scraping.
- **Imports:** `aiohttp`, `bs4`, `re`.

### `analyzer/deadline_checker.py` — Deadline Conflict Detection

| Component | Detail |
|-----------|--------|
| `_load_calendar()` | Returns hardcoded calendar with 3 entries (July 2026) |
| `has_conflict(deadline)` | Returns `True` if new deadline is within **< 2 days** of existing commitment |
| `add_commitment(date, desc)` | Adds entry and persists to `config/calendar.json` |
| `_save_calendar()` | Writes to `config/calendar.json` (directory does **not** exist yet) |

**Note:** The `config/` directory and `config/calendar.json` are referenced but **do not exist**. The system will crash on `_save_calendar()` if `add_commitment()` is called.

### `notifications/telegram_bot.py` — Telegram Alert Sender

- Reads `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` from `.env`.
- `send_alerts()` sends one HTML-formatted message per job with 0.5s delay between messages.
- If `self.bot` is `None` (no token configured), it prints a warning and returns silently.

### `.env` — Environment Variables

| Variable | Purpose | Default Value |
|----------|---------|---------------|
| `TELEGRAM_BOT_TOKEN` | Bot token for Telegram API | `your_bot_token_here` |
| `TELEGRAM_CHAT_ID` | Target chat/channel ID | `your_chat_id_here` |
| `EDITGPT_API_KEY` | (Planned) AI editing API key | `your_editgpt_api_key` |
| `DASHBOARD_USERNAME` | (Planned) Dashboard auth | `your_username` |
| `DASHBOARD_PASSWORD` | (Planned) Dashboard auth | `your_password` |
| `WORD_TEMPLATE_PATH` | (Planned) Word template path | `./templates/job_template.docm` |

### `requirements.txt` — Dependencies

| Package | Version | Used By |
|---------|---------|---------|
| `requests` | >=2.31.0 | (planned HTTP) |
| `beautifulsoup4` | >=4.12.0 | `dashboard_scraper.py` |
| `selenium` | >=4.15.0 | (planned JS-heavy scraping) |
| `pyopenvba` | >=0.1.0 | (planned Word VBA) |
| `python-dotenv` | >=1.0.0 | `telegram_bot.py` |
| `sqlalchemy` | >=2.0.0 | (planned DB persistence) |
| `apscheduler` | >=3.10.0 | `job_scheduler.py` |
| `python-telegram-bot` | >=20.0 | `telegram_bot.py` |
| `pandas` | >=2.0.0 | (planned data analysis) |
| `pyyaml` | >=6.0 | (planned YAML config) |
| `aspose-words` | >=23.0.0 | (planned Word processing) |

---

## Setup

### Prerequisites

- Python 3.14+ (the project uses `uv` — see `.venv/pyvenv.cfg`)
- A Telegram bot token (from [@BotFather](https://t.me/BotFather))

### Quick Start

```powershell
# 1. Clone and enter the project directory
git clone https://github.com/sajad-husain/job-analyzer-system.git
cd job-analyzer-system

# 2. Create and activate virtual environment
uv venv
.venv\Scripts\activate

# 3. Install dependencies
uv pip install -r requirements.txt

# 4. Configure environment
# Edit .env and set your TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID

# 5. Create required directories
mkdir logs
mkdir config
mkdir templates
```

---

## Running the System

```powershell
# From the job-analyzer-system directory:
python main.py
```

**Expected output (successful startup):**

```
🚀 Starting Job Monitor System v1.0
==================================================
📄 Checking Word integration...
🤖 Initializing editGPT integration...
⏰ Starting 30-second job monitor...

✅ System running. Press Ctrl+C to stop.
```

**Stop:** `Ctrl+C`

---

## Logging & Debugging

### Log Configuration

From `main.py` (lines 8-15):

| Handler | Output | Level |
|---------|--------|-------|
| `FileHandler` | `logs/system.log` | INFO |
| `StreamHandler` | stdout (console) | INFO |

### Debugging Tips

1. **Run with debug logging** (edit `main.py` line 9):
   ```python
   level=logging.DEBUG
   ```

2. **Check the log file** after a run:
   ```powershell
   Get-Content logs/system.log -Tail 50
   ```

3. **Test the Telegram integration in isolation:**
   ```powershell
   python -c "import asyncio; from notifications.telegram_bot import TelegramNotifier; asyncio.run(TelegramNotifier().send_alerts([{'title':'Test','company':'TestCo','pay_rate':30,'word_count':100,'deadline':'2026-07-20'}]))"
   ```

4. **Test the deadline checker in isolation:**
   ```powershell
   python -c "from analyzer.deadline_checker import DeadlineChecker; dc=DeadlineChecker(); print(dc.has_conflict('2026-07-11'))"
   ```

5. **Monitor the real-time log stream:**
   ```powershell
   Get-Content logs/system.log -Wait
   ```

---

## Common Errors & Fixes

### 1. `ModuleNotFoundError: No module named 'word_automation'`

**Cause:** `main.py` imports `word_automation.macro_handler` which does not exist.

**Fix:** Create placeholder modules, or comment out lines 5 and 22-24 in `main.py`:

```python
# from word_automation.macro_handler import WordMacroHandler
# ...
# word_handler = WordMacroHandler()
# word_handler.test_connection()
```

### 2. `ModuleNotFoundError: No module named 'ai_integration'`

**Cause:** `main.py` imports `ai_integration.editgpt_client` which does not exist.

**Fix:** Comment out lines 6 and 27-30 in `main.py`:

```python
# from ai_integration.editgpt_client import EditGPTClient
# ...
# ai_client = EditGPTClient()
# if ai_client.is_available():
#     print("✅ editGPT ready")
```

### 3. `FileNotFoundError: [Errno 2] No such file or directory: 'config/calendar.json'`

**Cause:** `deadline_checker.py:_save_calendar()` tries to write to `config/calendar.json` but the `config/` directory does not exist.

**Fix:** Create the directory:

```powershell
mkdir config
```

### 4. `FileNotFoundError: [Errno 2] No such file or directory: 'logs/system.log'`

**Cause:** The `logs/` directory does not exist when `main.py` starts.

**Fix:**

```powershell
mkdir logs
```

### 5. Telegram bot not sending messages

**Causes and checks:**

| Symptom | Check |
|---------|-------|
| `⚠️ Telegram not configured` printed | `.env` file missing or `TELEGRAM_BOT_TOKEN` not set |
| `Failed to send notification: ...` | Invalid token, wrong chat_id, or no network |
| No output | Ensure `.env` is in the **same directory** as `telegram_bot.py` (it calls `load_dotenv()` with no path, so it searches CWD). **Run `python main.py` from the `job-analyzer-system/` directory.** |

### 6. `ImportError: No module named 'apscheduler'`

**Cause:** Dependencies not installed.

**Fix:**

```powershell
uv pip install -r requirements.txt
```

---

## Environment Variables

The `.env` file uses placeholder values. For real operation, replace these:

```ini
# Required for Telegram notifications
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklmNOPqrstUVwxyz
TELEGRAM_CHAT_ID=-1001234567890

# Optional / planned
EDITGPT_API_KEY=sk-...
DASHBOARD_USERNAME=johndoe
DASHBOARD_PASSWORD=supersecret
WORD_TEMPLATE_PATH=./templates/job_template.docm
```

---

## Missing / Planned Modules

These are imported in `main.py` but **not yet implemented**:

| Module Path | Referenced Class | Status |
|---|---|---|
| `word_automation/macro_handler.py` | `WordMacroHandler` | ❌ Does not exist |
| `ai_integration/editgpt_client.py` | `EditGPTClient` | ❌ Does not exist |

These directories are referenced but **do not exist**:

| Path | Referenced In | Purpose |
|------|---------------|---------|
| `logs/` | `main.py:12` | Log file output |
| `config/` | `deadline_checker.py:51` | Calendar persistence |
| `templates/` | `.env` | Word template storage |

---

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         main.py                                    │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  1. Import WordMacroHandler          ← CRASH if missing      │   │
│  │  2. Import EditGPTClient            ← CRASH if missing      │   │
│  │  3. Create JobMonitorScheduler                                │   │
│  │  4. Run asyncio loop (Ctrl+C to stop)                        │   │
│  └──────────────────────┬───────────────────────────────────────┘   │
│                         │                                          │
└─────────────────────────┼──────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  scheduler/job_scheduler.py                         │
│                                                                     │
│  Every 30 seconds → monitor_jobs():                                 │
│                                                                     │
│    ┌──────────────────┐                                             │
│    │ scrape new jobs  │ ← DashboardScraper.fetch_new_jobs()        │
│    │                  │   (currently returns mock data)            │
│    └────────┬─────────┘                                             │
│             ▼                                                       │
│    ┌──────────────────┐                                             │
│    │ already seen?    │ ← Check job['id'] in processed_jobs set    │
│    └────────┬─────────┘                                             │
│             ▼ (skip if seen)                                        │
│    ┌──────────────────┐                                             │
│    │ deadline         │ ← DeadlineChecker.has_conflict()            │
│    │ conflict?        │   (checks within 2-day buffer)             │
│    └────────┬─────────┘                                             │
│             ▼ (skip if conflict)                                    │
│    ┌──────────────────┐                                             │
│    │ pay ≥ $25/hr?    │ ← get_min_pay_threshold()                  │
│    └────────┬─────────┘                                             │
│             ▼ (skip if below threshold)                             │
│    ┌──────────────────┐                                             │
│    │ send notification│ ← TelegramNotifier.send_alerts()           │
│    └──────────────────┘                                             │
└─────────────────────────────────────────────────────────────────────┘
```
