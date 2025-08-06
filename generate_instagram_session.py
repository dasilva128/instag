import asyncio
import os
from pyrogram import Client
from pyrogram.errors import PeerIdInvalid, UserIsBlocked
from instaloader import Instaloader, TwoFactorAuthRequiredException
from typing import Optional

L = Instaloader()

async def generate_session():
    print("🔑 Enter your Telegram API_ID:")
    API_ID = input().strip()
    
    print("🔑 Enter API_HASH:")
    API_HASH = input().strip()
    
    print("🤖 Enter Your BOT_TOKEN from @BotFather:")
    BOT_TOKEN = input().strip()
    
    async with Client("INSTASESSION", API_ID, API_HASH, bot_token=BOT_TOKEN) as bot:
        print("\n📱 Enter your Instagram username:")
        username = input().strip().lower()
        
        print("🔒 Enter Your Instagram password:")
        password = input().strip()
        
        try:
            L.login(username, password)
            print("✅ Successfully logged in to Instagram")
        except TwoFactorAuthRequiredException:
            print("\n🔐 2FA enabled. Enter the code sent to your phone:")
            code = input().strip()
            L.two_factor_login(code)
            print("✅ 2FA verification successful")
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return
        
        session_file = f"./{username}"
        L.save_session_to_file(filename=session_file)
        
        print("\n👤 Enter your Telegram User ID (e.g., 12345678):")
        while True:
            try:
                owner_id = int(input().strip())
                break
            except ValueError:
                print("Invalid ID. Please enter a numeric user ID:")
        
        try:
            msg = await bot.send_document(
                chat_id=owner_id,
                document=session_file,
                file_name=f"insta_session_{username}",
                caption="⚠️ KEEP THIS SESSION FILE SAFE AND PRIVATE"
            )
            
            await bot.send_message(
                chat_id=owner_id,
                text=f"🔑 Your `INSTA_SESSIONFILE_ID`:\n\n`{msg.document.file_id}`\n\n"
                     "⚠️ Add this to your environment variables"
            )
            
            print("\n✅ Session file sent to your Telegram. Check your messages!")
            
        except (PeerIdInvalid, UserIsBlocked):
            print("\n❌ Error: You haven't started the bot or have blocked it")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            if os.path.exists(session_file):
                os.remove(session_file)

if __name__ == "__main__":
    asyncio.run(generate_session())