# News Bot

A Telegram bot that aggregates and sends news from various sources including Apple news, Korean news, and US news (New Jersey and New York).

## Features

- Fetches news from multiple sources:
  - Apple news (9to5mac)
  - Korean news (Naver News)
  - US news (Google News for New Jersey and New York)
- Sends categorized news updates via Telegram
- Configurable scheduling for news updates

## Setup

1. Clone the repository:

```bash
git clone [your-repository-url]
cd [repository-name]
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `config.py` file with your configuration:

```python
TELEGRAM_BOT_TOKEN = "your-telegram-bot-token"
TELEGRAM_CHAT_ID = "your-chat-id"
```

4. Run the bot:

```bash
python3 main.py
```

## Configuration

The bot can be configured through the following files:

- `config.py`: Contains API keys and tokens
- `scheduler.py`: Configure scheduling settings
- `apple_news_bot.service`: Systemd service file for running the bot as a service

## Project Structure

- `main.py`: Main entry point
- `news_scraper.py`: Apple news scraping logic
- `korean_news_scraper.py`: Korean news scraping logic
- `us_news_scraper.py`: US news scraping logic
- `telegram_sender.py`: Telegram message sending functionality
- `scheduler.py`: Scheduling configuration

## License

This project is licensed under the MIT License - see the LICENSE file for details..
