from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import Client, filters
from config import Config
from utils import *
import os
from instaloader import Profile, TwoFactorAuthRequiredException, BadCredentialsException
from asyncio.exceptions import TimeoutError

USER = Config.USER
STATUS = Config.STATUS
OWNER = Config.OWNER
HOME_TEXT = Config.HOME_TEXT
insta = Config.L

@Client.on_message(filters.command("login") & filters.private)
async def login(bot, message):
    if str(message.from_user.id) != OWNER:
        await message.reply_text(
            HOME_TEXT.format(message.from_user.first_name, message.from_user.id, USER, USER, USER, OWNER),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("👨🏼‍💻 Developer", url='https://t.me/savior_128'),
                    InlineKeyboardButton("🤖 Other Bots", url="https://t.me/savior_128/122")
                ],
                [
                    InlineKeyboardButton("🔗 Source Code", url="https://github.com/savior_128/Instagram-Bot"),
                    InlineKeyboardButton("⚙️ Update Channel", url="https://t.me/savior_128")
                ],
                [
                    InlineKeyboardButton("👨🏼‍🦯 How To Use?", callback_data="help#subin")
                ]
            ])
        )
        return
    username = USER
    if 1 in STATUS:
        m = await bot.send_message(message.from_user.id, "Fetching details from Instagram")
        try:
            profile = Profile.own_profile(insta.context)
            mediacount = profile.mediacount
            name = profile.full_name
            bio = profile.biography
            profilepic = profile.profile_pic_url
            igtvcount = profile.igtvcount
            followers = profile.followers
            following = profile.followees
            await m.delete()
            await bot.send_photo(
                chat_id=message.from_user.id,
                caption=f"You are already logged in as {name}\n\n**Your Account Details**\n\n🏷 **Name**: {name}\n🔖 **Username**: {profile.username}\n📝 **Bio**: {bio}\n📍 **Account Type**: {acc_type(profile.is_private)}\n🏭 **Is Business Account?**: {yes_or_no(profile.is_business_account)}\n👥 **Total Followers**: {followers}\n👥 **Total Following**: {following}\n📸 **Total Posts**: {mediacount}\n📺 **IGTV Videos**: {igtvcount}",
                photo=profilepic
            )
        except Exception as e:
            await m.edit(f"Error fetching profile: {e}")
        return

    try:
        password = await bot.ask(
            text=f"Hello {USER}, enter your Instagram password to login into your account 🙈",
            chat_id=message.from_user.id,
            filters=filters.text,
            timeout=30
        )
    except TimeoutError:
        await bot.send_message(message.from_user.id, "Error: Request timed out.\nRestart by using /login")
        return

    passw = password.text
    try:
        insta.login(username, passw)
        insta.save_session_to_file(filename=f"./{username}")
        f = await bot.send_document(
            chat_id=message.from_user.id,
            document=f"./{username}",
            file_name=str(message.from_user.id),
            caption="⚠️ KEEP THIS SESSION FILE SAFE AND DO NOT SHARE WITH ANYBODY"
        )
        file_id = f.document.file_id
        await bot.send_message(
            message.from_user.id,
            f"Set the environment variable:\n\n**KEY**: <code>INSTA_SESSIONFILE_ID</code>\n\n**VALUE**: <code>{file_id}</code>\n\nIf you do not set this, you may need to login again after a restart.",
            disable_web_page_preview=True
        )
        STATUS.add(1)
        m = await bot.send_message(message.from_user.id, "Fetching details from Instagram")
        profile = Profile.from_username(insta.context, username)
        mediacount = profile.mediacount
        name = profile.full_name
        bio = profile.biography
        profilepic = profile.profile_pic_url
        igtvcount = profile.igtvcount
        followers = profile.followers
        following = profile.followees
        await m.delete()
        await bot.send_photo(
            chat_id=message.from_user.id,
            caption=f"🔓 Successfully logged in as {name}\n\n**Your Account Details**\n\n🏷 **Name**: {name}\n🔖 **Username**: {profile.username}\n📝 **Bio**: {bio}\n📍 **Account Type**: {acc_type(profile.is_private)}\n🏭 **Is Business Account?**: {yes_or_no(profile.is_business_account)}\n👥 **Total Followers**: {followers}\n👥 **Total Following**: {following}\n📸 **Total Posts**: {mediacount}\n📺 **IGTV Videos**: {igtvcount}",
            photo=profilepic
        )
    except TwoFactorAuthRequiredException:
        try:
            code = await bot.ask(
                text="Your Instagram account has Two Factor Authentication enabled 🔐\n\nAn OTP has been sent to your phone\nEnter the OTP",
                chat_id=message.from_user.id,
                filters=filters.text,
                timeout=30
            )
            codei = code.text
            try:
                codei = int(codei)
            except ValueError:
                await bot.send_message(message.from_user.id, "OTP should be an integer")
                return
            insta.two_factor_login(codei)
            insta.save_session_to_file(filename=f"./{username}")
            f = await bot.send_document(
                chat_id=message.from_user.id,
                document=f"./{username}",
                file_name=str(message.from_user.id),
                caption="⚠️ KEEP THIS SESSION FILE SAFE AND DO NOT SHARE WITH ANYBODY"
            )
            file_id = f.document.file_id
            await bot.send_message(
                message.from_user.id,
                f"Set the environment variable:\n\n**KEY**: <code>INSTA_SESSIONFILE_ID</code>\n\n**VALUE**: <code>{file_id}</code>\n\nIf you do not set this, you may need to login again after a restart.",
                disable_web_page_preview=True
            )
            STATUS.add(1)
            m = await bot.send_message(message.from_user.id, "Fetching details from Instagram")
            profile = Profile.from_username(insta.context, username)
            mediacount = profile.mediacount
            name = profile.full_name
            bio = profile.biography
            profilepic = profile.profile_pic_url
            igtvcount = profile.igtvcount
            followers = profile.followers
            following = profile.followees
            await m.delete()
            await bot.send_photo(
                chat_id=message.from_user.id,
                caption=f"🔓 Successfully logged in as {name}\n\n**Your Account Details**\n\n🏷 **Name**: {name}\n🔖 **Username**: {profile.username}\n📝 **Bio**: {bio}\n📍 **Account Type**: {acc_type(profile.is_private)}\n🏭 **Is Business Account?**: {yes_or_no(profile.is_business_account)}\n👥 **Total Followers**: {followers}\n👥 **Total Following**: {following}\n📸 **Total Posts**: {mediacount}\n📺 **IGTV Videos**: {igtvcount}",
                photo=profilepic
            )
        except BadCredentialsException:
            await bot.send_message(message.from_user.id, "Wrong credentials\n\n/login again")
        except Exception as e:
            await bot.send_message(message.from_user.id, f"Error: {e}\nTry /login again")
    except Exception as e:
        await bot.send_message(message.from_user.id, f"Error: {e}\nTry again or report this issue to [Developer](tg://user?id=626664225)")

@Client.on_message(filters.command("logout") & filters.private)
async def logout(bot, message):
    if str(message.from_user.id) != OWNER:
        await message.reply_text(
            HOME_TEXT.format(message.from_user.first_name, message.from_user.id, USER, USER, USER, OWNER),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("👨🏼‍💻 Developer", url='https://t.me/savior_128'),
                    InlineKeyboardButton("🤖 Other Bots", url="https://t.me/savior_128/122")
                ],
                [
                    InlineKeyboardButton("🔗 Source Code", url="https://github.com/savior_128/Instagram-Bot"),
                    InlineKeyboardButton("⚙️ Update Channel", url="https://t.me/savior_128")
                ],
                [
                    InlineKeyboardButton("👨🏼‍🦯 How To Use?", callback_data="help#subin")
                ]
            ])
        )
        return
    if 1 in STATUS:
        try:
            os.remove(f"./{USER}")
            STATUS.remove(1)
            await message.reply_text("Successfully logged out")
        except Exception as e:
            await message.reply_text(f"Error during logout: {e}")
    else:
        await message.reply_text("You are not logged in\nUse /login first")