import os
from instaloader import Instaloader
from dotenv import load_dotenv
from typing import Set

load_dotenv()

class Config:
    """تنظیمات ربات و اینستاگرام"""
    
    # Telegram Config
    API_ID = int(os.getenv("API_ID", 0))
    API_HASH = os.getenv("API_HASH", "")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    OWNER = os.getenv("OWNER_ID", "")
    
    # Instagram Config
    USER = os.getenv("INSTAGRAM_USERNAME", "")
    INSTA_SESSIONFILE_ID = os.getenv("INSTA_SESSIONFILE_ID", None)
    
    # Bot Status
    S = "0"
    STATUS: Set[int] = set(int(x) for x in S.split())
    
    # Instaloader instance
    L = Instaloader(
        quiet=True,
        download_video_thumbnails=False,
        compress_json=False,
        save_metadata=False,
        max_connection_attempts=3,
        request_timeout=30
    )
    
    # تنظیم پروکسی (در صورت وجود)
    proxy = os.getenv("INSTA_PROXY")
    if proxy:
        L.context._session.proxies = {
            "http": proxy,
            "https": proxy
        }
    
    # Help Text
    HELP = """
    **Instagram Bot Help** 📚
    
    You can download almost anything from Instagram:
    
    **📥 Downloadable Content:**
    - Profile pictures
    - Posts (photos/videos)
    - Stories
    - Highlights
    - IGTV videos
    - Saved posts
    - Tagged posts
    - Followers/Following lists
    
    **🛠 Available Commands:**
    /start - Start the bot
    /help - Show this help
    /login - Login to Instagram
    /logout - Logout from Instagram
    /account - Show account info
    /posts [username] - Download posts
    /igtv [username] - Download IGTV
    /stories [username] - Download stories
    /highlights [username] - Download highlights
    /followers [username] - Get followers list
    /followees [username] - Get following list
    
    **🔗 Support:** [Developer](https://t.me/savior_128)
    """
    
    HOME_TEXT = """
    👋 Hello {0}!
    
    🤖 I'm an Instagram assistant bot for @{1}
    
    🔍 Use /help to see what I can do
    """
    
    HOME_TEXT_OWNER = """
    👋 Welcome back {0}!
    
    🤖 Your Instagram assistant is ready
    
    🔍 Use /help for command list
    """