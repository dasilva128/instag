from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors import MessageTooLong
from config import Config
from utils import *
import os
from instaloader import Profile
from typing import Tuple

HELP = Config.HELP
session = f"./{Config.USER}"
STATUS = Config.STATUS
insta = Config.L

async def parse_callback_data(data: str) -> Tuple[str, str]:
    """Split callback data into command and username"""
    return data.split("#", 1) if "#" in data else (data, "")

@Client.on_callback_query(filters.regex(r"^help"))
async def help_callback(bot: Client, query: CallbackQuery):
    await query.message.edit_text(
        HELP,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/savior_128"),
                InlineKeyboardButton("⚙️ Updates", url="https://t.me/savior_128")
            ],
            [
                InlineKeyboardButton("🔐 Close", callback_data="close")
            ]
        ])
    )

@Client.on_callback_query(filters.regex(r"^ppic#"))
async def profile_pic_callback(bot: Client, query: CallbackQuery):
    cmd, username = await parse_callback_data(query.data)
    profile = Profile.from_username(insta.context, username)
    await query.answer("Downloading profile picture...")
    await bot.send_photo(
        query.from_user.id,
        photo=profile.profile_pic_url,
        caption=f"📸 Profile picture of @{username}"
    )

@Client.on_callback_query(filters.regex(r"^(post|photo|video|igtv|tagged|stories|highlights)#"))
async def content_callback(bot: Client, query: CallbackQuery):
    cmd, username = await parse_callback_data(query.data)
    
    if cmd == "post":
        await query.message.delete()
        await bot.send_message(
            query.from_user.id,
            f"📂 What type of content from @{username}?",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📷 Photos", callback_data=f"photos#{username}"),
                    InlineKeyboardButton("🎥 Videos", callback_data=f"video#{username}")
                ]
            ])
        )
        return
    
    m = await query.message.edit_text(f"⏳ Preparing {cmd} from @{username}...")
    dir_path = f"{query.from_user.id}/{username}"
    
    command = ["instaloader"]
    common_options = [
        "--no-metadata-json",
        "--no-compress-json",
        "--no-captions",
        "--no-video-thumbnails",
        "--login", Config.USER,
        "-f", session,
        "--dirname-pattern", dir_path
    ]
    
    if cmd == "photos":
        command.extend(["--no-videos", "--no-profile-pic"])
    elif cmd == "video":
        command.extend(["--no-pictures", "--no-profile-pic"])
    elif cmd == "igtv":
        command.extend(["--igtv", "--no-posts"])
    elif cmd == "tagged":
        command.extend(["--tagged", "--no-posts"])
    elif cmd == "stories":
        command.extend(["--stories", "--no-posts"])
    elif cmd == "highlights":
        command.extend(["--highlights", "--no-posts"])
    
    command.extend(common_options + ["--", username])
    
    await download_insta(command, m, dir_path)
    await upload(m, bot, query.from_user.id, dir_path)

@Client.on_callback_query(filters.regex(r"^close"))
async def close_callback(bot: Client, query: CallbackQuery):
    await query.message.delete()