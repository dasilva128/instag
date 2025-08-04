# bot/instagram.py
import instaloader
import os
from config import INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD

class InstagramDownloader:
    def __init__(self):
        self.loader = instaloader.Instaloader()
        self.logged_in = False

    def login(self):
        """ورود به حساب اینستاگرام"""
        try:
            self.loader.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
            self.logged_in = True
            return True
        except Exception as e:
            print(f"Login failed: {e}")
            return False

    def download_from_link(self, url, chat_id):
        """دانلود محتوا از لینک اینستاگرام"""
        try:
            shortcode = url.split("/")[-2] if url.split("/")[-1] == "" else url.split("/")[-1]
            post = instaloader.Post.from_shortcode(self.loader.context, shortcode)
            self.loader.download_post(post, target=f"downloads/{chat_id}")
            return f"downloads/{chat_id}"
        except Exception as e:
            return f"خطا در دانلود از لینک: {e}"

    def download_profile_content(self, username, chat_id, content_type="posts"):
        """دانلود پست‌ها یا استوری‌های یک کاربر"""
        try:
            if not self.logged_in:
                self.login()

            profile = instaloader.Profile.from_username(self.loader.context, username)
            download_path = f"downloads/{chat_id}/{username}_{content_type}"
            os.makedirs(download_path, exist_ok=True)

            if content_type == "posts":
                for post in profile.get_posts():
                    self.loader.download_post(post, target=download_path)
            elif content_type == "stories":
                self.loader.download_stories(userids=[profile.userid], filename_target=download_path)
            return download_path
        except Exception as e:
            return f"خطا در دانلود {content_type}: {e}"
