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
    """
    اعتبارسنجی کاربر اینستاگرام و بازگشت پروفایل در صورت دسترسی
    
    Args:
        username (str): نام کاربری اینستاگرام
        
    Returns:
        Optional[Profile]: پروفایل اینستاگرام یا None
    """
    try:
        profile = await get_profile(username)
        if profile.is_private and not profile.followed_by_viewer:
            return None
        return profile
    except Exception:
        return None

@Client.on_message(filters.command("posts") & filters.private)
async def posts_command(bot: Client, message: Message):
    """
    مدیریت دستور /posts
    
    Args:
        bot (Client): نمونه ربات Pyrogram
        message (Message): پیام تلگرامی
    """
    if str(message.from_user.id) != OWNER:
        return await message.reply("⛔ دسترسی محدود به مالک ربات")
        
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
    """
    مدیریت دستور /igtv
    
    Args:
        bot (Client): نمونه ربات Pyrogram
        message (Message): پیام تلگرامی
    """
    if str(message.from_user.id) != OWNER:
        return await message.reply("⛔ دسترسی محدود به مالک ربات")
        
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

@Client.on_message(filters.command("followers") & filters.private)
async def followers_command(bot: Client, message: Message):
    """
    مدیریت دستور /followers
    
    Args:
        bot (Client): نمونه ربات Pyrogram
        message (Message): پیام تلگرامی
    """
    if str(message.from_user.id) != OWNER:
        return await message.reply("⛔ دسترسی محدود به مالک ربات")
        
    if 1 not in Config.STATUS:
        return await message.reply("🔒 Please /login first")
    
    username = USER
    if " " in message.text:
        username = message.text.split(" ", 1)[1].strip()
    
    profile = await validate_instagram_user(username)
    if not profile:
        return await message.reply("❌ Private account or invalid username")
    
    try:
        followers = [user.username for user in profile.get_followers()]
        if not followers:
            return await message.reply(f"❌ No followers found for @{username}")
        
        followers_text = f"📋 **Followers for @{username}**\n\n" + "\n".join(followers[:50])
        await message.reply(followers_text, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔒 Close", callback_data="close")]
        ]))
    except Exception as e:
        await message.reply(f"❌ Error fetching followers: {e}")
        logger.error(f"Followers error: {e}")

@Client.on_message(filters.command("followees") & filters.private)
async def followees_command(bot: Client, message: Message):
    """
    مدیریت دستور /followees
    
    Args:
        bot (Client): نمونه ربات Pyrogram
        message (Message): پیام تلگرامی
    """
    if str(message.from_user.id) != OWNER:
        return await message.reply("⛔ دسترسی محدود به مالک ربات")
        
    if 1 not in Config.STATUS:
        return await message.reply("🔒 Please /login first")
    
    username = USER
    if " " in message.text:
        username = message.text.split(" ", 1)[1].strip()
    
    profile = await validate_instagram_user(username)
    if not profile:
        return await message.reply("❌ Private account or invalid username")
    
    try:
        followees = [user.username for user in profile.get_followees()]
        if not followees:
            return await message.reply(f"❌ No followees found for @{username}")
        
        followees_text = f"📋 **Followees for @{username}**\n\n" + "\n".join(followees[:50])
        await message.reply(followees_text, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔒 Close", callback_data="close")]
        ]))
    except Exception as e:
        await message.reply(f"❌ Error fetching followees: {e}")
        logger.error(f"Followees error: {e}")