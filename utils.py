import asyncio
import shutil
import glob
import pytz
from datetime import datetime
from typing import Optional, List, Callable
from pyrogram.types import (
    InputMediaPhoto, 
    InputMediaVideo, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
    Message
)
from pyrogram import Client
from videoprops import get_audio_properties
from config import Config
import logging
from instaloader import Profile, Post
from pyrogram.errors import FloodWait
import os

logger = logging.getLogger(__name__)

IST = pytz.timezone('Asia/Tehran')
USER = Config.USER
session = f"./{USER}"

async def get_profile(username: str) -> Profile:
    """
    دریافت پروفایل اینستاگرام با مدیریت خطاها
    
    Args:
        username (str): نام کاربری اینستاگرام
        
    Returns:
        Profile: پروفایل اینستاگرام
        
    Raises:
        Exception: در صورت عدم دسترسی به پروفایل
    """
    try:
        return await safe_instagram_request(
            Profile.from_username,
            Config.L.context,
            username
        )
    except Exception as e:
        logger.error(f"Failed to get profile: {e}")
        raise Exception(f"Could not fetch profile for {username}")

async def download_insta(command: List[str], message: Message, directory: str) -> bool:
    """
    اجرای دستور instaloader و به‌روزرسانی پیشرفت دانلود
    
    Args:
        command (List[str]): لیست دستورات برای اجرای instaloader
        message (Message): پیام تلگرامی برای به‌روزرسانی وضعیت
        directory (str): مسیر دایرکتوری برای ذخیره فایل‌های دانلودشده
        
    Returns:
        bool: True در صورت موفقیت، False در صورت شکست
    """
    try:
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        while True:
            output = await process.stdout.readline()
            if not output:
                break
                
            datetime_ist = datetime.now(IST)
            ist_time = datetime_ist.strftime("%I:%M:%S %p - %d %B %Y")
            msg = f"⏳ Status: `{output.decode().strip()}`\n🕒 Last Updated: `{ist_time}`"
            msg = msg.replace(f'{directory}/', '📥 Downloaded: ')
            
            try:
                await message.edit(msg)
            except:
                pass
        
        return True
    except Exception as e:
        logger.error(f"Download failed: {e}")
        await message.edit(f"❌ Download failed: {e}")
        return False

async def upload(
    message: Message, 
    bot: Client, 
    chat_id: int, 
    directory: str
) -> None:
    """
    آپلود محتوای دانلودشده به تلگرام
    
    Args:
        message (Message): پیام تلگرامی برای به‌روزرسانی وضعیت
        bot (Client): نمونه ربات Pyrogram
        chat_id (int): شناسه چت تلگرام
        directory (str): مسیر دایرکتوری حاوی فایل‌ها
    """
    if not os.path.exists(directory):
        await message.edit("❌ Directory not found")
        return

    videos = glob.glob(f"{directory}/*.mp4")
    pics = glob.glob(f"{directory}/*.jpg")
    
    media = []
    for video in videos:
        try:
            get_audio_properties(video)
            media.append(InputMediaVideo(video))
        except:
            media.append(InputMediaVideo(video, supports_streaming=True))
    
    for pic in pics:
        media.append(InputMediaPhoto(pic))
    
    if not media:
        await message.edit("❌ No media found to upload")
        return
    
    try:
        await message.edit("📤 Starting upload...")
        
        for i in range(0, len(media), 10):
            chunk = media[i:i+10]
            await bot.send_media_group(
                chat_id=chat_id,
                media=chunk,
                disable_notification=True
            )
        
        await message.edit("✅ Upload completed!")
        
    except Exception as e:
        await message.edit(f"❌ Upload failed: {e}")
    finally:
        try:
            if os.path.exists(directory):
                shutil.rmtree(directory, ignore_errors=True)
        except Exception as e:
            logger.error(f"Failed to remove directory {directory}: {e}")

def acc_type(is_private: bool) -> str:
    """
    تعیین نوع حساب (خصوصی/عمومی)
    
    Args:
        is_private (bool): وضعیت خصوصی بودن حساب
        
    Returns:
        str: نوع حساب
    """
    return "🔒 Private" if is_private else "🔓 Public"

def yes_or_no(value: bool) -> str:
    """
    تبدیل مقدار بولین به متن
    
    Args:
        value (bool): مقدار بولین
        
    Returns:
        str: متن معادل
    """
    return "✅ Yes" if value else "❌ No"

def format_user_info(profile: Profile) -> str:
    """
    فرمت‌دهی اطلاعات پروفایل اینستاگرام
    
    Args:
        profile (Profile): نمونه پروفایل اینستاگرام
        
    Returns:
        str: متن فرمت‌شده اطلاعات کاربر
    """
    return (
        f"👤 **{profile.full_name}** (@{profile.username})\n\n"
        f"📝 **Bio:** {profile.biography}\n"
        f"🔒 **Private:** {yes_or_no(profile.is_private)}\n"
        f"🏢 **Business:** {yes_or_no(profile.is_business_account)}\n"
        f"📸 **Posts:** {profile.mediacount}\n"
        f"🎥 **IGTV:** {profile.igtvcount}\n"
        f"👥 **Followers:** {profile.followers}\n"
        f"🔄 **Following:** {profile.followees}"
    )

async def safe_instagram_request(
    func: Callable,
    *args,
    max_retries: int = 3,
    initial_delay: float = 2.0,
    **kwargs
) -> Any:
    """
    اجرای ایمن درخواست‌های اینستاگرام با قابلیت تلاش مجدد
    
    Args:
        func (Callable): تابع مورد نظر برای اجرا
        max_retries (int): حداکثر تعداد تلاش‌ها
        initial_delay (float): تاخیر اولیه بین تلاش‌ها (ثانیه)
        
    Returns:
        Any: نتیجه تابع
        
    Raises:
        Exception: در صورت شکست تمام تلاش‌ها
    """
    last_error = None
    
    for attempt in range(1, max_retries + 1):
        try:
            delay = initial_delay * (attempt + random.random())
            if attempt > 1:
                logger.warning(f"Retry {attempt} for {func.__name__}, waiting {delay:.1f}s")
                await asyncio.sleep(delay)
                
            return await func(*args, **kwargs)
            
        except FloodWait as e:
            wait_time = e.value + random.uniform(1, 3)
            logger.warning(f"Instagram flood wait, sleeping {wait_time:.1f}s")
            await asyncio.sleep(wait_time)
            last_error = e
        except Exception as e:
            last_error = e
            if attempt == max_retries:
                logger.error(f"Instagram request failed after {max_retries} attempts")
                raise
    
    raise last_error if last_error else Exception("Unknown error in safe request")

async def get_stories(username: str):
    """
    دریافت استوری‌های اینستاگرام
    
    Args:
        username (str): نام کاربری اینستاگرام
        
    Returns:
        List: لیست استوری‌ها
        
    Raises:
        Exception: در صورت عدم دسترسی به استوری‌ها
    """
    try:
        profile = await get_profile(username)
        return await safe_instagram_request(profile.get_stories)
    except Exception as e:
        logger.error(f"Story download failed: {e}")
        raise Exception("Could not fetch stories. Account may be private or you need to follow them.")