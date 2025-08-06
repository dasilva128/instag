from pyrogram import Client, idle
from config import Config

bot = Client(
    "InstaSession",
    bot_token=Config.BOT_TOKEN,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    workers=50,
    plugins=dict(root="plugins")
)

async def main():
    try:
        async with bot:
            if Config.INSTA_SESSIONFILE_ID:
                await bot.download_media(Config.INSTA_SESSIONFILE_ID, file_name=f"./{Config.USER}")
                Config.L.load_session_from_file(Config.USER, filename=f"./{Config.USER}")
                Config.STATUS.add(1)
            await idle()
    except Exception as e:
        print(f"Error in main: {e}")

if __name__ == "__main__":
    bot.run(main())