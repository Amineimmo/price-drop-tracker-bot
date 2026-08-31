# Price Drop Tracker Bot

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-2CA5E0)
![Playwright](https://img.shields.io/badge/Playwright-Automation-45ba4b)


A multi-user Telegram bot that tracks live product prices from major e-commerce platforms and notifies you the moment a price drops below your custom target — straight to your Telegram chat, with the product image included.

---

## Features

- **Multi-store support** — Track products from:
  - **Amazon**
  - **eBay** (automatic USD → MAD conversion)
  - **Jumia Maroc** (native MAD pricing)
- **Multi-user support** — Every user's tracked products are isolated in the database, so tracking and alerts stay private per user.
- **Automated background polling** — A dedicated background worker checks prices on a schedule, no manual refresh needed.
- **Rich alerts** — Notifications include the product image, title, current price, and your target price, both when you start tracking and when a price drop triggers.
- **Simple command interface** — Track, list, and remove products with a few Telegram commands.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.9+ |
| Bot framework | [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) |
| Scraping / automation | [Playwright](https://playwright.dev/python/) (headless browser, bypasses anti-bot protections) |
| HTML parsing | BeautifulSoup4 + lxml |
| Database | SQLite3 |
| Config management | python-dotenv |

---

## Project Structure

```
price-drop-tracker-bot/
├── telegram_bot.py    # Telegram command handlers: /start, /track, /list, /remove, /help
├── main.py             # Background loop — periodically checks prices and pushes alerts
├── scraper.py           # Playwright scraping logic for Amazon, eBay, and Jumia
├── database.py          # SQLite operations with per-user data isolation
├── requirements.txt     # Project dependencies
└── .env                 # Environment variables (bot token, etc.)
```

---

## Installation & Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/price-drop-tracker-bot.git
cd price-drop-tracker-bot
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Playwright browsers

Playwright needs its browser binaries installed separately:

```bash
playwright install
```

### 5. Set up environment variables

Create a `.env` file in the project root:

```env
BOT_TOKEN=your_telegram_bot_token_here
```

You can get a bot token by messaging [@BotFather](https://t.me/BotFather) on Telegram and creating a new bot with `/newbot`.

---

## Running the Project

This project runs as **two separate processes** that work together:

- `telegram_bot.py` — handles user interaction (commands, tracking requests)
- `main.py` — runs in the background, periodically checking prices and sending alerts

Run them **concurrently**, each in its own terminal:

**Terminal 1 — start the bot:**
```bash
python telegram_bot.py
```

**Terminal 2 — start the price-checking worker:**
```bash
python main.py
```

Both need to be running for the bot to fully function: `telegram_bot.py` lets users add/manage tracked products, while `main.py` is what actually detects price drops and sends the alerts.

---

## Telegram Commands

| Command | Description |
|---|---|
| `/start` | Show the welcome message and instructions |
| `/track` | Start tracking a new product (send a product link and target price) |
| `/list` | View all products you're currently tracking |
| `/remove` | Stop tracking a specific product |
| `/help` | Show the list of available commands |

---

## How It Works

1. A user sends `/track` along with a product URL and their target price.
2. `scraper.py` uses Playwright to load the product page and extract the title, image, and current price (handling anti-bot protections that simple `requests`-based scraping can't get past).
3. The tracked product is saved to the SQLite database, scoped to that user's Telegram ID.
4. `main.py` runs continuously in the background, periodically re-checking prices for all tracked products across all users.
5. When a product's price drops to or below the user's target, the bot sends an alert with the product image, current price, and target price.

---

## Notes

- eBay prices are automatically converted from USD to Moroccan Dirham (MAD) for consistency with Amazon and Jumia listings.
- Since scraping relies on Playwright's headless browser, initial setup requires the `playwright install` step to download the necessary browser binaries.
- Make sure `.env` is included in `.gitignore` — it holds your bot token and should never be committed to version control.

---
