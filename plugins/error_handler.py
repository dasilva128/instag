from pyrogram import Client
from pyrogram.types import Message
from pyrogram.errors import (
    FloodWait,
    RPCError,
    BadRequest,
    Unauthorized
)
import logging
import time

logger = logging.getLogger(__name__)

@Client.on_message()
async def error_handler(bot: Client, message: Message):
    try:
        # Let other handlers process the message
        await message.continue_propagation()
    except FloodWait as e:
        logger.warning(f"Flood wait: Sleeping for {e.x} seconds")
        time.sleep(e.x)
    except BadRequest as e:
        logger.error(f"Bad request: {e}")
        await message.reply("❌ Invalid request. Please try again.")
    except Unauthorized:
        logger.error("Unauthorized access attempt")
    except RPCError as e:
        logger.error(f"RPC error: {e}")
        await message.reply("⚠️ An error occurred. Please try again later.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        await message.reply("❌ An unexpected error occurred. Please contact admin.")