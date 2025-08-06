from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from config import Config
import sys
import os
from typing import Optional

USER = Config.USER
OWNER = Config.OWNER
HELP = Config.HELP

@Client.on_message(filters.command("start") & filters.private)
async def start_command(bot: Client, message: Message):
    is_owner = str(message.from_user.id) == OWNER
    text = Config.HOME_TEXT_OWNER if is_owner else Config.HOME_TEXT
    text = text.format(
        message.from_user.first_name,
        message.from_user.id,
        USER,
        USER,
        USER,
        OWNER
    )
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🆘 Help", callback_data="help"),
            InlineKeyboardButton("🔒 Close", callback_data="close")
        ]
    ])
    
    await message.reply_text(
        text,
        reply_markup=buttons,
        disable_web_page_preview=True
    )

@Client.on_message(filters.command("help") & filters.private)
async def help_command(bot: Client, message: Message):
    await message.reply_text(
        HELP,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔙 Back", callback_data="back"),
                InlineKeyboardButton("🔒 Close", callback_data="close")
            ]
        ]),
        disable_web_page_preview=True
    )

@Client.on_message(filters.command("restart") & filters.private)
async def restart_command(bot: Client, message: Message):
    if str(message.from_user.id) != OWNER:
        return await start_command(bot, message)
    
    msg = await message.reply("🔄 Restarting bot...")
    await asyncio.sleep(2)
    await msg.edit("✅ Bot restarted successfully!")
    os.execl(sys.executable, sys.executable, *sys.argv)