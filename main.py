import asyncio
from pyrogram import Client, idle
from config import Config
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("instabot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def main():
    bot = Client(
        "InstaSessionBot",
        bot_token=Config.BOT_TOKEN,
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        plugins=dict(root="plugins"),
        workers=200,
        sleep_threshold=180
    )

    async with bot:
        try:
            # Load Instagram session if available
            if Config.INSTA_SESSIONFILE_ID:
                await bot.download_media(
                    Config.INSTA_SESSIONFILE_ID,
                    file_name=f"./{Config.USER}"
                )
                Config.L.load_session_from_file(
                    Config.USER, 
                    filename=f"./{Config.USER}"
                )
                Config.STATUS.add(1)
                logger.info("Instagram session loaded successfully")

            # Notify owner
            await bot.send_message(
                Config.OWNER,
                "🤖 Bot started successfully!\n"
                f"🔗 Instagram: @{Config.USER}\n"
                "Use /help for commands"
            )
            
            await idle()
            
        except Exception as e:
            logger.error(f"Bot crashed: {e}", exc_info=True)
        finally:
            logger.info("Bot stopped gracefully")

if __name__ == "__main__":
    try:
        logger.info("Starting bot...")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        sys.exit(0)