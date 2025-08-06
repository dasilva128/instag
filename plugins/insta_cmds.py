from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from config import Config
from utils import *
from instaloader import Profile
from typing import Optional

USER = Config.USER
OWNER = Config.OWNER
insta = Config.L

async def validate_instagram_user(username: str) -> Optional[Profile]:
    """Validate Instagram user and return profile if accessible"""
    try:
        profile = Profile.from_username(insta.context, username)
        if profile.is_private and not profile.followed_by_viewer:
            return None
        return profile
    except Exception:
        return None

@Client.on_message(filters.command("posts") & filters.private)
async def posts_command(bot: Client, message: Message):
    if str(message.from_user.id) != OWNER:
        return
        
    if 1 not in Config.STATUS:
        return await message.reply("🔒 Please /login first")
    
    username = USER
    if " " in message.text:
        username = message.text.split(" ", 1)[1].strip()
    
    profile = await validate_instagram_user(username)
    if not profile:
        return await message.reply("❌ Private account or invalid username")
    
    await message.reply(
        f"📂 Select content type from @{username}",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📷 Photos", callback_data=f"photos#{username}"),
                InlineKeyboardButton("🎥 Videos", callback_data=f"video#{username}")
            ]
        ])
    )

@Client.on_message(filters.command("igtv") & filters.private)
async def igtv_command(bot: Client, message: Message):
    if str(message.from_user.id) != OWNER:
        return
        
    if 1 not in Config.STATUS:
        return await message.reply("🔒 Please /login first")
    
    username = USER
    if " " in message.text:
        username = message.text.split(" ", 1)[1].strip()
    
    profile = await validate_instagram_user(username)
    if not profile:
        return await message.reply("❌ Private account or invalid username")
    
    if profile.igtvcount == 0:
        return await message.reply("❌ No IGTV videos found")
    
    await message.reply(
        f"📺 Download {profile.igtvcount} IGTV videos from @{username}?",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Yes", callback_data=f"igtv#{username}"),
                InlineKeyboardButton("❌ No", callback_data="close")
            ]
        ])
    )