import re
import logging
from typing import Optional, Union
from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from instaloader import Profile, Post
from config import Config
from utils import (
    download_insta,
    upload,
    acc_type,
    yes_or_no,
    format_user_info  # تابع جدید از helpers
)
from plugins.helpers import create_keyboard
from plugins.downloader import download_posts, download_stories

# تنظیمات لاگ
logger = logging.getLogger(__name__)

# دستور /account
@Client.on_message(filters.command("account") & filters.private)
async def account_info(client: Client, message: Message):
    """نمایش اطلاعات حساب اینستاگرام متصل"""
    if str(message.from_user.id) != Config.OWNER:
        return await message.reply("⛔ دسترسی محدود به مالک ربات")

    if 1 not in Config.STATUS:
        return await message.reply("🔒 لطفا ابتدا وارد شوید /login")

    try:
        profile = Profile.own_profile(Config.L.context)
        
        # ایجاد کیبورد با قابلیت‌های مختلف
        buttons = [
            [
                {"text": "📸 عکس پروفایل", "callback": f"ppic#{profile.username}"},
                {"text": "📥 تمام پست‌ها", "callback": f"post#{profile.username}"}
            ],
            [
                {"text": "🎥 IGTV", "callback": f"igtv#{profile.username}"},
                {"text": "🌟 هایلایت‌ها", "callback": f"highlights#{profile.username}"}
            ],
            [
                {"text": "📲 استوری‌ها", "callback": f"stories#{profile.username}"},
                {"text": "👥 دنبال‌کنندگان", "callback": f"followers#{profile.username}"}
            ],
            [
                {"text": "🔄 افراد دنبال‌شده", "callback": f"followees#{profile.username}"},
                {"text": "📌 پست‌های تگ شده", "callback": f"tagged#{profile.username}"}
            ]
        ]

        await message.reply_photo(
            photo=profile.profile_pic_url,
            caption=format_user_info(profile),
            reply_markup=create_keyboard(buttons)
        )

    except Exception as e:
        logger.error(f"Error in account_info: {e}")
        await message.reply(f"❌ خطا: {str(e)}")

# پردازش متن دریافتی (یوزرنیم یا لینک)
@Client.on_message(filters.text & filters.private & ~filters.command)
async def handle_instagram_input(client: Client, message: Message):
    """پردازش یوزرنیم یا لینک اینستاگرام"""
    if str(message.from_user.id) != Config.OWNER:
        return

    if 1 not in Config.STATUS:
        return await message.reply("🔒 لطفا ابتدا وارد شوید /login")

    input_text = message.text.strip()

    # پردازش لینک اینستاگرام
    if "instagram.com" in input_text:
        return await handle_instagram_url(client, message, input_text)

    # پردازش یوزرنیم
    await handle_instagram_username(client, message, input_text)

async def handle_instagram_url(client: Client, message: Message, url: str):
    """پردازش لینک اینستاگرام"""
    try:
        # شناسایی نوع لینک
        patterns = {
            "post": r"(?:https?://)?(?:www\.)?instagram\.com/p/([^/]+)",
            "reel": r"(?:https?://)?(?:www\.)?instagram\.com/reel/([^/]+)",
            "igtv": r"(?:https?://)?(?:www\.)?instagram\.com/tv/([^/]+)",
            "story": r"(?:https?://)?(?:www\.)?instagram\.com/stories/([^/]+)/(\d+)"
        }

        for post_type, pattern in patterns.items():
            match = re.match(pattern, url)
            if match:
                if post_type == "story":
                    username, story_id = match.groups()
                    return await handle_story(client, message, username, story_id)
                
                shortcode = match.group(1)
                return await handle_post(client, message, shortcode, post_type)

        await message.reply("⚠️ لینک نامعتبر. فقط پست، رییل، IGTV و استوری پشتیبانی می‌شود")

    except Exception as e:
        logger.error(f"Error processing URL: {e}")
        await message.reply(f"❌ خطا در پردازش لینک: {str(e)}")

async def handle_post(client: Client, message: Message, shortcode: str, post_type: str):
    """دانلود پست اینستاگرام"""
    loading_msg = await message.reply(f"🔍 در حال دریافت {post_type}...")
    
    try:
        post = Post.from_shortcode(Config.L.context, shortcode)
        dir_path = f"{message.from_user.id}/{shortcode}"
        
        command = [
            "instaloader",
            "--no-metadata-json",
            "--no-compress-json",
            "--no-captions",
            "--no-video-thumbnails",
            "--login", Config.USER,
            "-f", f"./{Config.USER}",
            "--dirname-pattern", dir_path,
            "--", f"-{shortcode}"
        ]

        await download_insta(command, loading_msg, dir_path)
        await upload(loading_msg, client, message.from_user.id, dir_path)

    except Exception as e:
        await loading_msg.edit(f"❌ خطا در دانلود: {str(e)}")
        logger.error(f"Post download error: {e}")

async def handle_story(client: Client, message: Message, username: str, story_id: str):
    """دانلود استوری اینستاگرام"""
    try:
        profile = Profile.from_username(Config.L.context, username)
        
        if profile.is_private and not profile.followed_by_viewer:
            return await message.reply("🔒 حساب کاربری خصوصی است و شما دنبال‌کننده نیستید")

        await download_stories(message, username)
        
    except Exception as e:
        await message.reply(f"❌ خطا در دریافت استوری: {str(e)}")
        logger.error(f"Story download error: {e}")

async def handle_instagram_username(client: Client, message: Message, username: str):
    """پردازش یوزرنیم اینستاگرام"""
    try:
        profile = Profile.from_username(Config.L.context, username)
        
        # ایجاد کیبورد تعاملی
        buttons = [
            [
                {"text": "📸 عکس پروفایل", "callback": f"ppic#{username}"},
                {"text": "📥 پست‌ها", "callback": f"post#{username}"}
            ],
            [
                {"text": "🎥 IGTV", "callback": f"igtv#{username}"},
                {"text": "📲 استوری‌ها", "callback": f"stories#{username}"}
            ],
            [
                {"text": "👥 دنبال‌کنندگان", "callback": f"followers#{username}"},
                {"text": "🔄 افراد دنبال‌شده", "callback": f"followees#{username}"}
            ]
        ]

        if profile.is_private and not profile.followed_by_viewer:
            buttons = [[buttons[0][0]]  # فقط دکمه عکس پروفایل

        await message.reply_photo(
            photo=profile.profile_pic_url,
            caption=format_user_info(profile),
            reply_markup=create_keyboard(buttons)
        )

    except Exception as e:
        await message.reply(f"❌ خطا: {str(e)}")
        logger.error(f"Username handling error: {e}")

# کال‌بک‌های کیبورد
@Client.on_callback_query(filters.regex(r"^ppic#"))
async def send_profile_pic(client: Client, callback: CallbackQuery):
    """ارسال عکس پروفایل"""
    try:
        username = callback.data.split("#")[1]
        profile = Profile.from_username(Config.L.context, username)
        
        await callback.message.reply_photo(
            photo=profile.profile_pic_url,
            caption=f"📸 عکس پروفایل @{username}"
        )
        await callback.answer()
        
    except Exception as e:
        await callback.answer("❌ خطا در دریافت عکس پروفایل", show_alert=True)
        logger.error(f"Profile pic error: {e}")