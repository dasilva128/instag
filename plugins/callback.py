from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import Client, filters
from config import Config
from utils import *
import os
from instaloader import Profile
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong

HELP = Config.HELP
USER = Config.USER
session = f"./{USER}"
STATUS = Config.STATUS
insta = Config.L

@Client.on_callback_query()
async def cb_handler(bot: Client, query):
    try:
        cmd, username = query.data.split("#")
        profile = Profile.from_username(insta.context, username)
        mediacount = profile.mediacount
        name = profile.full_name
        profilepic = profile.profile_pic_url
        igtvcount = profile.igtvcount
        followers = profile.followers
        following = profile.followees

        if cmd == "help":
            await query.message.edit_text(
                HELP,
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("👨🏼‍💻 Developer", url='https://t.me/subinps'),
                        InlineKeyboardButton("🤖 Other Bots", url="https://t.me/subin_works/122"),
                        InlineKeyboardButton("⚙️ Update Channel", url="https://t.me/subin_works")
                    ],
                    [
                        InlineKeyboardButton("🔗 Source Code", url="https://github.com/subinps/Instagram-Bot"),
                        InlineKeyboardButton("🧩 Deploy Own Bot", url="https://heroku.com/deploy?template=https://github.com/subinps/Instagram-Bot")
                    ]
                ])
            )

        elif cmd == "ppic":
            await query.answer()
            await bot.send_document(
                chat_id=query.from_user.id,
                document=profilepic,
                file_name=f"{username}.jpg",
                force_document=True
            )

        elif cmd == "post":
            await query.message.delete()
            await bot.send_message(
                query.from_user.id,
                "What type of post do you want to download?",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("Photos", callback_data=f"photos#{username}"),
                        InlineKeyboardButton("Videos", callback_data=f"video#{username}")
                    ]
                ])
            )

        elif cmd == "photos":
            if mediacount == 0:
                await query.message.edit_text("There are no posts by the user.")
                return
            m = await query.message.edit_text("Starting downloading...\nThis may take time depending on the number of posts.")
            dir = f"{query.from_user.id}/{username}"
            command = [
                "instaloader",
                "--no-metadata-json",
                "--no-compress-json",
                "--no-profile-pic",
                "--no-videos",
                "--no-captions",
                "--no-video-thumbnails",
                "--login", USER,
                "-f", session,
                "--dirname-pattern", dir,
                username
            ]
            await download_insta(command, m, dir)
            await upload(m, bot, query.from_user.id, dir)

        elif cmd == "video":
            if mediacount == 0:
                await query.message.edit_text("There are no posts by the user.")
                return
            m = await query.message.edit_text("Starting downloading...\nThis may take longer depending on the number of posts.")
            dir = f"{query.from_user.id}/{username}"
            command = [
                "instaloader",
                "--no-metadata-json",
                "--no-compress-json",
                "--no-profile-pic",
                "--no-pictures",
                "--no-captions",
                "--no-video-thumbnails",
                "--login", USER,
                "-f", session,
                "--dirname-pattern", dir,
                username
            ]
            await download_insta(command, m, dir)
            await upload(m, bot, query.from_user.id, dir)

        elif cmd == "igtv":
            await query.message.delete()
            await bot.send_message(
                query.from_user.id,
                f"Do you want to download all IGTV posts?\nThere are {igtvcount} posts.",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("Yes", callback_data=f"yesigtv#{username}"),
                        InlineKeyboardButton("No", callback_data=f"no#{username}")
                    ]
                ])
            )

        elif cmd == "yesigtv":
            if igtvcount == 0:
                await query.message.edit_text("There are no IGTV posts by the user.")
                return
            m = await query.message.edit_text("Starting downloading...\nThis may take longer depending on the number of posts.")
            dir = f"{query.from_user.id}/{username}"
            command = [
                "instaloader",
                "--no-metadata-json",
                "--no-compress-json",
                "--no-profile-pic",
                "--no-posts",
                "--igtv",
                "--no-captions",
                "--no-video-thumbnails",
                "--login", USER,
                "-f", session,
                "--dirname-pattern", dir,
                username
            ]
            await download_insta(command, m, dir)
            await upload(m, bot, query.from_user.id, dir)

        elif cmd == "followers":
            await query.message.delete()
            m = await bot.send_message(query.from_user.id, f"Fetching Followers List of {name}")
            f = profile.get_followers()
            followers = f"**Followers List for {name}**\n\n"
            for p in f:
                followers += f"\n[{p.username}](https://www.instagram.com/{p.username})"
            try:
                await m.delete()
                await bot.send_message(chat_id=query.from_user.id, text=followers)
            except MessageTooLong:
                followers = f"**Followers List for {name}**\n\n"
                f = profile.get_followers()
                for p in f:
                    followers += f"\nName: {p.username} : Link to Profile: https://www.instagram.com/{p.username}"
                text_file = f"{username}_followers.txt"
                with open(text_file, "w") as f:
                    f.write(followers)
                await bot.send_document(
                    chat_id=query.from_user.id,
                    document=text_file,
                    caption=f"{name}'s followers\n\nA Project By [XTZ_Bots](https://t.me/subin_works)"
                )
                os.remove(text_file)

        elif cmd == "followees":
            await query.message.delete()
            m = await bot.send_message(query.from_user.id, f"Fetching Followees of {name}")
            f = profile.get_followees()
            followees = f"**Followees List for {name}**\n\n"
            for p in f:
                followees += f"\n[{p.username}](https://www.instagram.com/{p.username})"
            try:
                await m.delete()
                await bot.send_message(chat_id=query.from_user.id, text=followees)
            except MessageTooLong:
                followees = f"**Followees List for {name}**\n\n"
                f = profile.get_followees()
                for p in f:
                    followees += f"\nName: {p.username} : Link to Profile: https://www.instagram.com/{p.username}"
                text_file = f"{username}_followees.txt"
                with open(text_file, "w") as f:
                    f.write(followees)
                await bot.send_document(
                    chat_id=query.from_user.id,
                    document=text_file,
                    caption=f"{name}'s followees\n\nA Project By [XTZ_Bots](https://t.me/subin_works)"
                )
                os.remove(text_file)

        elif cmd == "no":
            await query.message.delete()

        else:
            dir = f"{query.from_user.id}/{username}"
            m = await bot.send_message(query.from_user.id, "Starting downloading...\nThis may take longer depending on the number of posts.")
            commands = {
                "feed": [
                    "instaloader", "--no-metadata-json", "--no-compress-json", "--no-profile-pic",
                    "--no-posts", "--no-captions", "--no-video-thumbnails", "--login", USER,
                    "-f", session, "--dirname-pattern", dir, ":feed"
                ],
                "saved": [
                    "instaloader", "--no-metadata-json", "--no-compress-json", "--no-profile-pic",
                    "--no-posts", "--no-captions", "--no-video-thumbnails", "--login", USER,
                    "-f", session, "--dirname-pattern", dir, ":saved"
                ],
                "tagged": [
                    "instaloader", "--no-metadata-json", "--no-compress-json", "--no-profile-pic",
                    "--no-posts", "--tagged", "--no-captions", "--no-video-thumbnails", "--login", USER,
                    "-f", session, "--dirname-pattern", dir, username
                ],
                "stories": [
                    "instaloader", "--no-metadata-json", "--no-compress-json", "--no-profile-pic",
                    "--no-posts", "--stories", "--no-captions", "--no-video-thumbnails", "--login", USER,
                    "-f", session, "--dirname-pattern", dir, username
                ],
                "fstories": [
                    "instaloader", "--no-metadata-json", "--no-compress-json", "--no-profile-pic",
                    "--no-captions", "--no-posts", "--no-video-thumbnails", "--login", USER,
                    "-f", session, "--dirname-pattern", dir, ":stories"
                ],
                "highlights": [
                    "instaloader", "--no-metadata-json", "--no-compress-json", "--no-profile-pic",
                    "--no-posts", "--highlights", "--no-captions", "--no-video-thumbnails", "--login", USER,
                    "-f", session, "--dirname-pattern", dir, username
                ]
            }
            command = commands.get(cmd)
            if command:
                await download_insta(command, m, dir)
                await upload(m, bot, query.from_user.id, dir)
    except Exception as e:
        await query.message.edit_text(f"Error: {e}")