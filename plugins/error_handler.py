from pyrogram import Client
from pyrogram.errors import FloodWait, RPCError, BadRequest, Unauthorized
from pyrogram import ContinuePropagation
import logging
import asyncio

logger = logging.getLogger(__name__)

@Client.on_message()
async def error_handler(client: Client, message):
    """
    هندلر مرکزی برای مدیریت خطاها
    
    Args:
        client (Client): نمونه ربات Pyrogram
        message (Message): پیام تلگرامی
    """
    try:
        raise ContinuePropagation
    except FloodWait as e:
        logger.warning(f"Flood wait: Sleeping for {e.value} seconds")
        await asyncio.sleep(e.value)
        await message.reply("⏳ لطفاً چند لحظه صبر کنید و دوباره تلاش کنید.")
    except BadRequest as e:
        logger.error(f"Bad request: {e}")
        await message.reply("❌ خطای درخواست نامعتبر. لطفاً دوباره تلاش کنید.")
    except Unauthorized:
        logger.error("Unauthorized access attempt")
        await message.reply("❌ دسترسی غیرمجاز. لطفاً ابتدا وارد شوید.")
    except RPCError as e:
        logger.error(f"RPC error: {e}")
        await message.reply(f"❌ خطای API تلگرام: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        await message.reply("❌ خطای غیرمنتظره‌ای رخ داد. لطفاً بعداً تلاش کنید.")