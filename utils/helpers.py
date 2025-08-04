# utils/helpers.py
import os
from telegram import Update
from telegram.ext import CallbackContext

def send_files(update: Update, context: CallbackContext, folder_path: str):
    """ارسال فایل‌های دانلود شده به تلگرام"""
    chat_id = update.message.chat_id
    if os.path.exists(folder_path):
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith(('.jpg', '.mp4', '.png')):  # فرمت‌های پشتیبانی‌شده
                    with open(file_path, 'rb') as f:
                        context.bot.send_document(chat_id=chat_id, document=f)
    else:
        update.message.reply_text("هیچ فایلی برای ارسال یافت نشد.")
