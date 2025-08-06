import asyncio
import os
from pyrogram import Client
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid, UserIsBlocked
from instaloader import Instaloader, TwoFactorAuthRequiredException, BadCredentialsException

async def generate():
    L = Instaloader()
    try:
        print("Enter your Telegram API_ID")
        API_ID = input().strip()
        print("Enter API_HASH")
        API_HASH = input().strip()
        print("Enter Your BOT_TOKEN from Botfather")
        BOT_TOKEN = input().strip()

        async with Client("INSTASESSION", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN) as bot:
            print("Now Enter your Instagram username")
            id = input().strip()
            print("Enter Your Instagram Password")
            pwd = input().strip()

            try:
                L.login(id, pwd)
                L.save_session_to_file(filename=f"./{id}")
            except TwoFactorAuthRequiredException:
                print("Your account has Two Factor authentication Enabled.\nNow Enter the code received on your mobile.")
                code = input().strip()
                L.two_factor_login(code)
                L.save_session_to_file(filename=f"./{id}")
            except BadCredentialsException:
                print("Invalid Instagram credentials.")
                return
            except Exception as e:
                print(f"Error during Instagram login: {e}")
                return

            print("Successfully logged into Instagram")
            while True:
                print("To send your Session file, enter Your Telegram ID as Integer")
                tg_id = input().strip()
                try:
                    owner = int(tg_id)
                    break
                except ValueError:
                    print("Invalid Telegram ID, please enter an integer.")

            try:
                f = await bot.send_document(
                    chat_id=owner,
                    document=f"./{id}",
                    file_name=str(owner),
                    caption="⚠️ KEEP THIS SESSION FILE SAFE AND DO NOT SHARE WITH ANYBODY"
                )
                file_id = f.document.file_id
                await bot.send_message(
                    chat_id=owner,
                    text=f"Here is Your <code>INSTA_SESSIONFILE_ID</code>\n\n<code>{file_id}</code>\n\n\n⚠️ KEEP THIS SESSION FILE SAFE AND DO NOT SHARE WITH ANYBODY"
                )
                print("I have messaged you the INSTA_SESSIONFILE_ID. Check your Telegram messages")
            except PeerIdInvalid:
                print("Invalid Telegram ID or you haven't started the bot. Send /start to your bot first and try again.")
            except UserIsBlocked:
                print("You have blocked the bot. Unblock the bot and try again.")
            except Exception as e:
                print(f"Error sending session file: {e}")
    finally:
        if os.path.exists(f"./{id}"):
            os.remove(f"./{id}")
        if os.path.exists("INSTASESSION.session"):
            os.remove("INSTASESSION.session")

if __name__ == "__main__":
    asyncio.run(generate())