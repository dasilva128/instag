import re
import logging
import random
import time
from pyrogram import Client, filters, ContinuePropagation
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from instaloader import Profile, Post, StoryItem
from config import Config
from utils import (
    download_insta,
    upload,
    acc_type,
    yes_or_no,
    safe_instagram_request,
    get_profile,
    format_user_info
)
from plugins.helpers import create_keyboard

logger = logging.getLogger(__name__)

# تنظیمات تلاش مجدد
MAX_RETRIES = 3
RETRY_DELAY = 5

async def get_profile_safe(username: str) -> Profile:
    """
    دریافت پروفایل با مدیریت خطاها و تلاش مجدد
    
    Args:
        username (str): نام کاربری اینستاگرام
        
    Returns:
        Profile: پروفایل اینستاگرام
        
    Raises:
        Exception: در صورت عدم دسترسی به پروفایل
    """
    for attempt in range(MAX_RETRIES):
        try:
            return await get_profile(username)
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                raise
            delay = RETRY_DELAY * (attempt + 1) + random.uniform(0, 3)
            logger.warning(f"Retry {attempt + 1} for {username} after {delay:.1f}s")
            time.sleep(delay)

@Client.on_message(filters.command("account") & filters.private)
async def account_info(client: Client, message: Message):
    """
    نمایش اطلاعات حساب متصل
    
    Args:
        client (Client): نمونه ربات Pyrogram
        message (Message): پیام تلگرامی
    """
    if str(message.from_user.id) != Config.OWNER:
        return await message.reply("⛔ دسترسی محدود به مالک ربات")

    if 1 not in Config.STATUS:
        return await message.reply("🔒 لطفا ابتدا وارد شوید /login")

    try:
        profile = await get_profile_safe(Config.USER)
        
        buttons = [
            [
                {"text": "📸 عکس پروفایل", "callback": f"ppic#{profile.username}"},
                {"text": "📥 تمام پست‌ها", "callback": f"post#{profile.username}"}
            ],
            [
                {"text": "🎥 IGTV", "callback": f"igtv#{profile.username}"},
                {"text": "🌟 هایلایت‌ها", "callback": f"highlights#{profile.username}"}
            ]
        ]

        await message.reply_photo(
            photo=profile.profile_pic_url,
            caption=format_user_info(profile),
            reply_markup=create_keyboard(buttons)
        )

    except Exception as e:
        error_msg = "خطا در دریافت اطلاعات از اینستاگرام"
        if "401 Unauthorized" in str(e):
            error_msg += "\n🔒 ممکن است نیاز به لاگین مجدد داشته باشید (/relogin)"
        await message.reply(f"❌ {error_msg}")
        logger.error(f"Account info error: {e}", exc_info=True)

@Client.on_message(filters.text & filters.private & ~filters.command([]))
async def handle_instagram_input(client: Client, message: Message):
    """
    پردازش پیام‌های متنی (یوزرنیم یا لینک)
    
    Args:
        client (Client): نمونه ربات Pyrogram
        message (Message): پیام تلگرامی
    """
    if str(message.from_user.id) != Config.OWNER:
        return

    if 1 not in Config.STATUS:
        return await message.reply("🔒 لطفا ابتدا وارد شوید /login")

    input_text = message.text.strip()

    if "instagram.com" in input_text:
        await handle_instagram_url(client, message, input_text)
    else:
        await handle_instagram_username(client, message, input_text)

async def handle_instagram_url(client: Client, message: Message, url: str):
    """
    پردازش لینک‌های اینستاگرام
    
    Args:
        client (Client): نمونه ربات Pyrogram
        message (Message): پیام تلگرامی
        url (str): لینک اینستاگرام
    """
    try:
        url_patterns = {
            "post": r"(?:https?://)?(?:www\.)?instagram\.com/p/([^/?#]+)",
            "reel": r"(?:https?://)?(?:www\.)?instagram\.com/reel/([^/?#]+)",
            "story": r"(?:https?://)?(?:www\.)?instagram\.com/stories/([^/]+)/(\d+)"
        }

        for content_type, pattern in url_patterns.items():
            match = re.search(pattern, url)
            if match:
                if content_type == "story":
                    username, story_id = match.groups()
                    return await handle_story(client, message, username, story_id)
                
                shortcode = match.group(1)
                return await handle_post(client, message, shortcode, content_type)

        await message.reply("⚠️ لینک نامعتبر. فقط پست، رییل و استوری پشتیبانی می‌شوند")

    except Exception as e:
        await handle_instagram_error(message, e, "پردازش لینک")

async def handle_post(client: Client, message: Message, shortcode: str, post_type: str):
    """
    دانلود پست اینستاگرام
    
    Args:
        client (Client): نمونه ربات Pyrogram
        message (Message): پیام تلگرامی
        shortcode (str): کد کوتاه پست
        post_type (str): نوع پست (post/reel)
    """
    loading_msg = await message.reply(f"🔍 در حال دریافت {post_type}...")
    
    try:
        post = await safe_instagram_request(
            Post.from_shortcode,
            Config.L.context,
            shortcode
        )
        
        dir_path = f"{message.from_user.id}/{shortcode}"
        command = [
            "instaloader",
            "--no-metadata-json",
            "--no-captions",
            "--no-video-thumbnails",
            "--login", Config.USER,
            "--sessionfile", f"./{Config.USER}",
            "--dirname-pattern", dir_path,
            "--", f"-{shortcode}"
        ]

        await download_insta(command, loading_msg, dir_path)
        await upload(loading_msg, client, message.from_user.id, dir_path)

    except Exception as e:
        await handle_instagram_error(loading_msg, e, "دانلود پست")

async def handle_story(client: Client, message: Message, username: str, story_id: str):
    """
    دانلود استوری اینستاگرام
    
    Args:
        client (Client): نمونه ربات Pyrogram
        message (Message): پیام تلگرامی
        username (str): نام کاربری اینستاگرام
        story_id (str): شناسه استوری
    """
    try:
        profile = await get_profile_safe(username)
        
        if profile.is_private and not profile.followed_by_viewer:
            return await message.reply("🔒 حساب کاربری خصوصی است و شما دنبال‌کننده نیستید")

        await message.reply("⏳ در حال دریافت استوری...")
        # پیاده‌سازی دانلود استوری اینجا
        
    except Exception as e:
        await handle_instagram_error(message, e, "دریافت استوری")

async def handle_instagram_username(client: Client, message: Message, username: str):
    """
    پردازش یوزرنیم اینستاگرام
    
    Args:
        client (Client): نمونه ربات Pyrogram
        message (Message): پیام تلگرامی
        username (str): نام کاربری اینستاگرام
    """
    try:
        profile = await get_profile_safe(username)
        
        buttons = [
            [
                {"text": "📸 عکس پروفایل", "callback": f"ppic#{username}"},
                {"text": "📥 پست‌ها", "callback": f"post#{username}"}
            ]
        ]

        if not profile.is_private or profile.followed_by_viewer:
            buttons.extend([
                [
                    {"text": "🎥 IGTV", "callback": f"igtv#{username}"},
                    {"text": "📲 استوری‌ها", "callback": f"stories#{username}"}
                ],
                [
                    {"text": "👥 دنبال‌کنندگان", "callback": f"followers#{username}"},
                    {"text": "🔄 دنبال‌شده‌ها", "callback": f"followees#{username}"}
                ]
            ])

        await message.reply_photo(
            photo=profile.profile_pic_url,
            caption=format_user_info(profile),
            reply_markup=create_keyboard(buttons)
        )

    except Exception as e:
        await handle_instagram_error(message, e, "پردازش یوزرنیم")

async def handle_instagram_error(message: Message, error: Exception, context: str):
    """
    مدیریت خطاهای اینستاگرام
    
    Args:
        message (Message): پیام تلگرامی
        error (Exception): خطای رخ‌داده
        context (str): زمینه خطا
    """
    error_msg = f"❌ خطا در {context}: "
    
    if "401 Unauthorized" in str(error):
        error_msg += "نیاز به ورود مجدد دارید (/relogin)"
    elif "404 Not Found" in str(error):
        error_msg += "کاربر یا محتوا یافت نشد"
    elif "rate limit" in str(error).lower():
        error_msg += "محدودیت درخواست. لطفاً چند دقیقه دیگر تلاش کنید"
    else:
        error_msg += str(error)
    
    await message.reply(error_msg)
    logger.error(f"{context} error: {error}", exc_info=True)

@Client.on_callback_query(filters.regex(r"^ppic#"))
async def send_profile_pic(client: Client, callback: CallbackQuery):
    """
    ارسال عکس پروفایل
    
    Args:
        client (Client): نمونه ربات Pyrogram
        callback (CallbackQuery): درخواست callback
    """
    try:
        username = callback.data.split("#")[1]
        profile = await get_profile_safe(username)
        
        await callback.message.reply_photo(
            photo=profile.profile_pic_url,
            caption=f"📸 عکس پروفایل @{username}"
        )
        await callback.answer()
        
    except Exception as e:
        await callback.answer("❌ خطا در دریافت عکس پروفایل", show_alert=True)
        logger.error(f"Profile pic error: {e}", exc_info=True)