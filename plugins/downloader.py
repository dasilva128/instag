import asyncio
from typing import List, Optional
from pyrogram.types import Message
from config import Config
from utils import download_insta, upload, safe_instagram_request, get_profile
from instaloader import Profile, StoryItem, Highlight, Post
import logging

logger = logging.getLogger(__name__)

async def download_posts(
    message: Message,
    username: str,
    post_type: str = "all",
    limit: Optional[int] = None
) -> bool:
    """
    دانلود پست‌های اینستاگرام
    
    Args:
        message (Message): پیام تلگرامی
        username (str): نام کاربری اینستاگرام
        post_type (str): نوع پست (all/photos/videos)
        limit (Optional[int]): حداکثر تعداد پست‌ها برای دانلود
        
    Returns:
        bool: True در صورت موفقیت، False در صورت شکست
    """
    try:
        profile = await safe_instagram_request(
            Profile.from_username,
            Config.L.context,
            username
        )
        
        dir_path = f"{message.from_user.id}/{username}"
        
        command = [
            "instaloader",
            "--no-metadata-json",
            "--no-compress-json",
            "--no-captions",
            "--no-video-thumbnails",
            "--login", Config.USER,
            "-f", f"./{Config.USER}",
            "--dirname-pattern", dir_path
        ]
        
        if post_type == "photos":
            command.extend(["--no-videos"])
        elif post_type == "videos":
            command.extend(["--no-pictures"])
        
        if limit:
            command.extend(["--count", str(limit)])
        
        command.append(f"--{username}")
        
        await download_insta(command, message, dir_path)
        await upload(message, message._client, message.from_user.id, dir_path)
        return True
    except Exception as e:
        await message.reply(f"❌ Error downloading posts: {e}")
        logger.error(f"Post download error: {e}", exc_info=True)
        return False

async def download_stories(
    message: Message,
    username: str
) -> bool:
    """
    دانلود استوری‌های اینستاگرام
    
    Args:
        message (Message): پیام تلگرامی
        username (str): نام کاربری اینستاگرام
        
    Returns:
        bool: True در صورت موفقیت، False در صورت شکست
    """
    try:
        profile = await get_profile(username)
        if profile.is_private and not profile.followed_by_viewer:
            await message.reply("🔒 حساب کاربری خصوصی است و شما دنبال‌کننده نیستید")
            return False
            
        dir_path = f"{message.from_user.id}/{username}_stories"
        
        command = [
            "instaloader",
            "--no-metadata-json",
            "--no-compress-json",
            "--no-captions",
            "--no-video-thumbnails",
            "--login", Config.USER,
            "-f", f"./{Config.USER}",
            "--dirname-pattern", dir_path,
            "--stories",
            "--", username
        ]
        
        await download_insta(command, message, dir_path)
        await upload(message, message._client, message.from_user.id, dir_path)
        return True
    except Exception as e:
        await message.reply(f"❌ Error downloading stories: {e}")
        logger.error(f"Story download error: {e}", exc_info=True)
        return False