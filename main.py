"""
Ashum - Saudi Market Analysis & Signal Bot
==========================================
AI-powered trading signal bot for Tadawul (Saudi Stock Exchange).
Scans 239+ stocks, generates buy/sell signals, and sends alerts via Telegram.
"""

import asyncio
import logging
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import TELEGRAM_BOT_TOKEN, DATABASE_URL
from src.data.repository import setup_database
from src.scheduler.jobs import create_scheduler
from src.notifications.telegram import create_telegram_app

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("ashum.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("ashum")


async def main():
    logger.info("=" * 50)
    logger.info("Ashum - Saudi Market Signal Bot")
    logger.info("=" * 50)

    # Validate config
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set. Check .env file.")
        sys.exit(1)

    # Initialize database
    logger.info(f"Connecting to database...")
    try:
        setup_database()
        logger.info("Database ready.")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        logger.info("Continuing without database (signals won't be persisted).")

    # Start scheduler
    scheduler = create_scheduler()
    scheduler.start()
    logger.info("Scheduler started. Jobs:")
    for job in scheduler.get_jobs():
        logger.info(f"  - {job.name}: {job.trigger}")

    # Start Telegram bot
    logger.info("Starting Telegram bot...")
    app = create_telegram_app()

    # Run the bot (this blocks until stopped)
    async with app:
        await app.start()
        logger.info("Bot is running! Send /help in Telegram to get started.")
        await app.updater.start_polling(drop_pending_updates=True)

        # Keep running until interrupted
        try:
            while True:
                await asyncio.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            logger.info("Shutting down...")
        finally:
            await app.updater.stop()
            await app.stop()
            scheduler.shutdown()
            logger.info("Ashum stopped. Goodbye!")


if __name__ == "__main__":
    asyncio.run(main())
