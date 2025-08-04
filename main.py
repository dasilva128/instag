# main.py
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from bot.handlers import BotHandlers
from config import TELEGRAM_BOT_TOKEN

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    handlers = BotHandlers()

    # افزودن هندلرها
    dp.add_handler(CommandHandler("start", handlers.start))
    dp.add_handler(CommandHandler("posts", handlers.download_posts))
    dp.add_handler(CommandHandler("stories", handlers.download_stories))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handlers.handle_link))

    # شروع ربات
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
