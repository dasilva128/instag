#!/usr/bin/env python3
import asyncio
import logging
import sys
import os
from pyrogram import Client, idle
from pyrogram.errors import PeerIdInvalid, FloodWait, RPCError
from config import Config

# تنظیمات لاگینگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("instabot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def initialize_bot():
    """
    تابع اصلی برای راه‌اندازی ربات
    
    Returns:
        None
    """
    bot = Client(
        name="InstaSessionBot",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        bot_token=Config.BOT_TOKEN,
        plugins=dict(root="plugins"),
        workers=20,  # کاهش تعداد workers برای بهبود عملکرد
        sleep_threshold=180,
        in_memory=True
    )

    async with bot:
        try:
            # راه‌اندازی اولیه
            await setup_instagram_session(bot)
            
            # اطلاع‌رسانی به مالک
            await notify_owner(bot)
            
            # شروع فعالیت ربات
            logger.info("Bot is now running...")
            await idle()

        except Exception as e:
            logger.critical(f"Bot crashed: {e}", exc_info=True)
        finally:
            logger.info("Bot stopped")

async def setup_instagram_session(bot: Client) -> None:
    """
    تنظیم session اینستاگرام
    
    Args:
        bot (Client): نمونه ربات Pyrogram
        
    Raises:
        Exception: در صورت بروز خطا در بارگذاری session
    """
    if Config.INSTA_SESSIONFILE_ID:
        try:
            session_file = f"./{Config.USER}"
            await bot.download_media(
                Config.INSTA_SESSIONFILE_ID,
                file_name=session_file
            )
            if not os.path.exists(session_file):
                raise FileNotFoundError(f"Session file {session_file} not found after download")
                
            Config.L.load_session_from_file(
                Config.USER, 
                filename=session_file
            )
            Config.STATUS.add(1)
            logger.info("Instagram session loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Instagram session: {e}")
            raise
        finally:
            if os.path.exists(session_file):
                os.remove(session_file)  # حذف فایل جلسه پس از استفاده

async def notify_owner(bot: Client) -> None:
    """
    ارسال پیام به مالک ربات
    
    Args:
        bot (Client): نمونه ربات Pyrogram
        
    Raises:
        ValueError: در صورت نامعتبر بودن OWNER_ID
        FloodWait: در صورت محدودیت تلگرام
        RPCError: در صورت خطای API تلگرام
    """
    try:
        owner_id = int(Config.OWNER)
        
        try:
            await bot.get_chat(owner_id)
        except PeerIdInvalid:
            logger.warning(f"Owner {owner_id} not found. Waiting for first interaction...")
            return

        await bot.send_message(
            owner_id,
            "🤖 **ربات با موفقیت راه‌اندازی شد!**\n\n"
            f"🔗 حساب اینستاگرام: @{Config.USER}\n"
            "✍️ از دستور /help برای مشاهده امکانات استفاده کنید"
        )
    except ValueError:
        logger.error(f"Invalid OWNER_ID: {Config.OWNER}")
    except FloodWait as e:
        logger.warning(f"Flood wait: Need to wait {e.value} seconds")
        await asyncio.sleep(e.value)
    except RPCError as e:
        logger.error(f"Telegram API error: {e}")
    except Exception as e:
        logger.error(f"Failed to notify owner: {e}")

if __name__ == "__main__":
    try:
        logger.info("Starting bot...")
        asyncio.run(initialize_bot())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)