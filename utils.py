import asyncio
import shutil
import glob
import pytz
from datetime import datetime
from typing import Optional, List
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

IST = pytz.timezone('Asia/Tehran')
USER = Config.USER
session = f"./{USER}"

async def download_insta(command: List[str], message: Message, directory: str) -> bool:
    """Run instaloader command and update progress"""
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

async def upload(
    message: Message, 
    bot: Client, 
    chat_id: int, 
    directory: str
) -> None:
    """Upload downloaded content to Telegram"""
    videos = glob.glob(f"{directory}/*.mp4")
    pics = glob.glob(f"{directory}/*.jpg")
    
    media = []
    for video in videos:
        try:
            get_audio_properties(video)  # Check if video has audio
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
        
        # Split media into chunks of 10 (Telegram limit)
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
        shutil.rmtree(directory, ignore_errors=True)

def acc_type(is_private: bool) -> str:
    return "🔒 Private" if is_private else "🔓 Public"

def yes_or_no(value: bool) -> str:
    return "✅ Yes" if value else "❌ No"