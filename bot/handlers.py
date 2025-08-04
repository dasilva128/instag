# bot/handlers.py
from telegram import Update
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters, CallbackContext
)
from bot.instagram import InstagramDownloader
from utils.helpers import send_files

class BotHandlers:
    def __init__(self):
        self.instagram = InstagramDownloader()

    def start(self, update: Update, context: CallbackContext):
        update.message.reply_text(
            "به ربات دانلود اینستاگرام خوش آمدید!\n"
            "دستورات:\n"
            "/posts <username> - دانلود پست‌های کاربر\n"
            "/stories <username> - دانلود استوری‌های کاربر\n"
            "یا لینک پست اینستاگرام را ارسال کنید."
        )

    def download_posts(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        if not context.args:
            update.message.reply_text("لطفاً نام کاربری را وارد کنید. مثال: /posts username")
            return
        username = context.args[0]
        update.message.reply_text(f"در حال دانلود پست‌های {username}...")
        folder_path = self.instagram.download_profile_content(username, chat_id, content_type="posts")
        if folder_path.startswith("خطا"):
            update.message.reply_text(folder_path)
        else:
            send_files(update, context, folder_path)

    def download_stories(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        if not context.args:
            update.message.reply_text("لطفاً نام کاربری را وارد کنید. مثال: /stories username")
            return
        username = context.args[0]
        update.message.reply_text(f"در حال دانلود استوری‌های {username}...")
        folder_path = self.instagram.download_profile_content(username, chat_id, content_type="stories")
        if folder_path.startswith("خطا"):
            update.message.reply_text(folder_path)
        else:
            send_files(update, context, folder_path)

    def handle_link(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        url = update.message.text
        if "instagram.com" not in url:
            update.message.reply_text("لطفاً یک لینک معتبر اینستاگرام ارسال کنید.")
            return
        update.message.reply_text("در حال دانلود از لینک...")
        folder_path = self.instagram.download_from_link(url, chat_id)
        if folder_path.startswith("خطا"):
            update.message.reply_text(folder_path)
        else:
            send_files(update, context, folder_path)
