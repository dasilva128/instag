from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config
from utils import *
from instaloader import (
    Profile, 
    TwoFactorAuthRequiredException, 
    BadCredentialsException
)
from asyncio.exceptions import TimeoutError

USER = Config.USER
STATUS = Config.STATUS

@Client.on_message(filters.command("login") & filters.private)
async def login_command(bot: Client, message: Message):
    """
    مدیریت دستور /login
    
    Args:
        bot (Client): نمونه ربات Pyrogram
        message (Message): پیام تلگرامی
    """
    if str(message.from_user.id) != Config.OWNER:
        return await message.reply("⛔ دسترسی محدود به مالک ربات")
        
    if 1 in STATUS:
        profile = await safe_instagram_request(Profile.own_profile, Config.L.context)
        return await message.reply_photo(
            photo=profile.profile_pic_url,
            caption=(
                f"✅ Already logged in as {profile.full_name}\n\n"
                f"👤 Username: @{profile.username}\n"
                f"📸 Posts: {profile.mediacount}\n"
                f"👥 Followers: {profile.followers}\n"
                f"🔄 Following: {profile.followees}"
            )
        )
    
    try:
        password = await bot.ask(
            chat_id=message.from_user.id,
            text="🔒 Enter your Instagram password:",
            filters=filters.text,
            timeout=120
        )
    except TimeoutError:
        return await message.reply("⌛ Timeout. Please try /login again")
    
    try:
        Config.L.login(USER, password.text)
        Config.L.save_session_to_file(filename=f"./{USER}")
        STATUS.add(1)
        
        profile = await safe_instagram_request(Profile.own_profile, Config.L.context)
        await message.reply_photo(
            photo=profile.profile_pic_url,
            caption=(
                f"✅ Successfully logged in as {profile.full_name}\n\n"
                f"👤 Username: @{profile.username}\n"
                f"📸 Posts: {profile.mediacount}\n"
                f"👥 Followers: {profile.followers}\n"
                f"🔄 Following: {profile.followees}"
            )
        )
        
    except TwoFactorAuthRequiredException:
        try:
            code = await bot.ask(
                chat_id=message.from_user.id,
                text="🔐 Enter the 2FA code sent to your phone:",
                filters=filters.text,
                timeout=120
            )
            Config.L.two_factor_login(code.text)
            Config.L.save_session_to_file(filename=f"./{USER}")
            STATUS.add(1)
            
            profile = await safe_instagram_request(Profile.own_profile, Config.L.context)
            await message.reply_photo(
                photo=profile.profile_pic_url,
                caption=(
                    f"✅ Successfully logged in with 2FA as {profile.full_name}\n\n"
                    f"👤 Username: @{profile.username}\n"
                    f"📸 Posts: {profile.mediacount}\n"
                    f"👥 Followers: {profile.followers}\n"
                    f"🔄 Following: {profile.followees}"
                )
            )
            
        except Exception as e:
            await message.reply(f"❌ Error: {e}")
            
    except BadCredentialsException:
        await message.reply("❌ Invalid password. Please try /login again")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

@Client.on_message(filters.command("logout") & filters.private)
async def logout_command(bot: Client, message: Message):
    """
    مدیریت دستور /logout
    
    Args:
        bot (Client): نمونه ربات Pyrogram
        message (Message): پیام تلگرامی
    """
    if str(message.from_user.id) != Config.OWNER:
        return await message.reply("⛔ دسترسی محدود به مالک ربات")
        
    if 1 in STATUS:
        STATUS.remove(1)
        session_file = f"./{USER}"
        try:
            if os.path.exists(session_file):
                os.remove(session_file)
            await message.reply("✅ Successfully logged out")
        except Exception as e:
            await message.reply(f"❌ Error logging out: {e}")
            logger.error(f"Logout error: {e}")
    else:
        await message.reply("❌ Not currently logged in")