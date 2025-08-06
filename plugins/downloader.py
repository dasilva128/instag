import asyncio
from typing import List, Optional
from pyrogram.types import Message
from config import Config
from utils import download_insta, upload
from instaloader import Profile, StoryItem, Highlight, Post

async def download_posts(
    message: Message,
    username: str,
    post_type: str = "all",
    limit: Optional[int] = None
) -> bool:
    """Download posts from Instagram"""
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

async def download_stories(
    message: Message,
    username: str
) -> bool:
    """Download Instagram stories"""
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