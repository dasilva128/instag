from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config
from utils import *

async def is_admin(message: Message) -> bool:
    """
    بررسی اینکه آیا کاربر ادمین/مالک است
    
    Args:
        message (Message): پیام تلگرامی
        
    Returns:
        bool: True اگر کاربر مالک باشد، در غیر این صورت False
    """
    return str(message.from_user.id) == Config.OWNER

@Client.on_message(filters.command("stats") & filters.private)
async def stats_command(bot: Client, message: Message):
    """
    نمایش آمار ربات
    
    Args:
        bot (Client): نمونه ربات Pyrogram
        message (Message): پیام تلگرامی
    """
    if not await is_admin(message):
        await message.reply("⛔ دسترسی محدود به مالک ربات")
        return
        
    try:
        profile = await safe_instagram_request(Profile.own_profile, Config.L.context)
        
        await message.reply(
            "📊 **Bot Statistics**\n\n"
            f"🖼 **Posts Downloaded:** {profile.mediacount}\n"
            f"🎥 **IGTV Downloaded:** {profile.igtvcount}\n"
            f"👥 **Followers Tracked:** {profile.followers}\n"
            f"🔄 **Following Tracked:** {profile.followees}"
        )
    except Exception as e:
        await message.reply(f"❌ Error fetching stats: {e}")
        logger.error(f"Stats error: {e}")

@Client.on_message(filters.command("clean") & filters.private)
async def clean_command(bot: Client, message: Message):
    """
    پاکسازی حافظه کش
    
    Args:
        bot (Client): نمونه ربات Pyrogram
        message (Message): پیام تلگرامی
    """
    if not await is_admin(message):
        await message.reply("⛔ دسترسی محدود به مالک ربات")
        return
        
    cache_path = f"./{Config.USER}"
    try:
        if os.path.exists(cache_path):
            shutil.rmtree(cache_path, ignore_errors=True)
            await message.reply("🧹 Cache cleaned successfully!")
        else:
            await message.reply("🧹 No cache found to clean")
    except Exception as e:
        await message.reply(f"❌ Error cleaning cache: {e}")
        logger.error(f"Cache cleaning error: {e}")