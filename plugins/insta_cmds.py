from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import Client, filters
from config import Config
from instaloader import Profile
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong
import os
from utils import *

USER = Config.USER
OWNER = Config.OWNER
HOME_TEXT = Config.HOME_TEXT
HELP = Config.HELP
session = f"./{USER}"
STATUS = Config.STATUS
insta = Config.L

buttons = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("👨🏼‍💻 Developer", url='https://t.me/subinps'),
        InlineKeyboardButton("🤖 Other Bots", url="https://t.me/subin_works/122")
    ],
    [
        InlineKeyboardButton("🔗 Source Code", url="https://github.com/subinps/Instagram-Bot"),
        InlineKeyboardButton("⚙️ Update Channel", url="https://t.me/subin_works")
    ],
    [
        InlineKeyboardButton("👨🏼‍🦯 How To Use?", callback_data="help#subin")
    ]
])

async def check_private_account(bot, message, username):
    if str(message.from_user.id) != OWNER:
        await message.reply_text(
            HOME_TEXT.format(message.from_user.first_name, message.from_user.id, USER, USER, USER, OWNER),
            reply_markup=buttons,
            disable_web_page_preview=True
        )
        return False
    if 1 not in STATUS:
        await message.reply_text("You must login first /login")
        return False
    if username != USER:
        profile = Profile.from_username(insta.context, username)
        is_followed = yes_or_no(profile.followed_by_viewer)
        if profile.is_private and is_followed == "No":
            await message.reply_text(f"Sorry!\nI can't fetch details from @{username}.\nSince it's a private account and you are not following it.")
            return False
    return True

@Client.on_message(filters.command("posts") & filters.private)
async def post(bot, message):
    text = message.text
    username = USER
    if " " in text:
        cmd, username = text.split(' ')
    if not await check_private_account(bot, message, username):
        return
    await bot.send_message(
        message.from_user.id,
        "What type of post do you want to download?",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Photos", callback_data=f"photos#{username}"),
                InlineKeyboardButton("Videos", callback_data=f"video#{username}")
            ]
        ])
    )

@Client.on_message(filters.command("igtv") & filters.private)
async def igtv(bot, message):
    text = message.text
    username = USER
    if " " in text:
        cmd, username = text.split(' ')
    if not await check_private_account(bot, message, username):
        return
    m = await message.reply_text(f"Fetching IGTV from <code>@{username}</code>")
    profile = Profile.from_username(insta.context, username)
    igtvcount = profile.igtvcount
    await m.edit(
        text=f"Do you want to download all IGTV posts?\nThere are {igtvcount} posts.",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Yes", callback_data=f"yesigtv#{username}"),
                InlineKeyboardButton("No", callback_data=f"no#{username}")
            ]
        ])
    )

@Client.on_message(filters.command("followers") & filters.private)
async def followers(bot, message):
    text = message.text
    username = USER
    if " " in text:
        cmd, username = text.split(' ')
    if not await check_private_account(bot, message, username):
        return
    profile = Profile.from_username(insta.context, username)
    name = profile.full_name
    m = await message.reply_text(f"Fetching Followers list of <code>@{username}</code>")
    chat_id = message.from_user.id
    f = profile.get_followers()
    followers = f"**Followers List for {name}**\n\n"
    for p in f:
        followers += f"\n[{p.username}](https://www.instagram.com/{p.username})"
    try:
        await m.delete()
        await bot.send_message(chat_id=chat_id, text=followers)
    except MessageTooLong:
        followers = f"**Followers List for {name}**\n\n"
        f = profile.get_followers()
        for p in f:
            followers += f"\nName: {p.username} : Link to Profile: https://www.instagram.com/{p.username}"
        text_file = f"{username}_followers.txt"
        with open(text_file, "w") as f:
            f.write(followers)
        await bot.send_document(
            chat_id=chat_id,
            document=text_file,
            caption=f"{name}'s followers\n\nA Project By [XTZ_Bots](https://t.me/subin_works)"
        )
        os.remove(text_file)

@Client.on_message(filters.command("followees") & filters.private)
async def followees(bot, message):
    text = message.text
    username = USER
    if " " in text:
        cmd, username = text.split(' ')
    if not await check_private_account(bot, message, username):
        return
    profile = Profile.from_username(insta.context, username)
    name = profile.full_name
    m = await message.reply_text(f"Fetching Followees list of <code>@{username}</code>")
    chat_id = message.from_user.id
    f = profile.get_followees()
    followees = f"**Followees List for {name}**\n\n"
    for p in f:
        followees += f"\n[{p.username}](https://www.instagram.com/{p.username})"
    try:
        await m.delete()
        await bot.send_message(chat_id=chat_id, text=followees)
    except MessageTooLong:
        followees = f"**Followees List for {name}**\n\n"
        f = profile.get_followees()
        for p in f:
            followees += f"\nName: {p.username} : Link to Profile: https://www.instagram.com/{p.username}"
        text_file = f"{username}_followees.txt"
        with open(text_file, "w") as f:
            f.write(followees)
        await bot.send_document(
            chat_id=chat_id,
            document=text_file,
            caption=f"{name}'s followees\n\nA Project By [XTZ_Bots](https://t.me/subin_works)"
        )
        os.remove(text_file)

@Client.on_message(filters.command("fans") & filters.private)
async def fans(bot, message):
    text = message.text
    username = USER
    if " " in text:
        cmd, username = text.split(' ')
    if not await check_private_account(bot, message, username):
        return
    profile = Profile.from_username(insta.context, username)
    name = profile.full_name
    m = await message.reply_text(f"Fetching list of followees of <code>@{username}</code> who follows <code>@{username}</code>.")
    chat_id = message.from_user.id
    f = profile.get_followers()
    fl = profile.get_followees()
    flist = [fn.username for fn in f]
    fmlist = [fm.username for fm in fl]
    fans = [value for value in fmlist if value in flist]
    followers = f"**Fans List for {name}**\n\n"
    for p in fans:
        followers += f"\n[{p}](https://www.instagram.com/{p})"
    try:
        await m.delete()
        await bot.send_message(chat_id=chat_id, text=followers)
    except MessageTooLong:
        followers = f"**Fans List for {name}**\n\n"
        for p in fans:
            followers += f"\nName: {p} : Link to Profile: https://www.instagram.com/{p}"
        text_file = f"{username}_fans.txt"
        with open(text_file, "w") as f:
            f.write(followers)
        await bot.send_document(
            chat_id=chat_id,
            document=text_file,
            caption=f"{name}'s fans\n\nA Project By [XTZ_Bots](https://t.me/subin_works)"
        )
        os.remove(text_file)

@Client.on_message(filters.command("notfollowing") & filters.private)
async def nfans(bot, message):
    text = message.text
    username = USER
    if " " in text:
        cmd, username = text.split(' ')
    if not await check_private_account(bot, message, username):
        return
    profile = Profile.from_username(insta.context, username)
    name = profile.full_name
    m = await message.reply_text(f"Fetching list of followees of <code>@{username}</code> who is <b>not</b> following <code>@{username}</code>.")
    chat_id = message.from_user.id
    f = profile.get_followers()
    fl = profile.get_followees()
    flist = [fn.username for fn in f]
    fmlist = [fm.username for fm in fl]
    fans = list(set(fmlist) - set(flist))
    followers = f"**Followees of <code>@{username}</code> who is <b>not</b> following <code>@{username}</code>**\n\n"
    for p in fans:
        followers += f"\n[{p}](https://www.instagram.com/{p})"
    try:
        await m.delete()
        await bot.send_message(chat_id=chat_id, text=followers)
    except MessageTooLong:
        followers = f"**Followees of <code>@{username}</code> who is <b>not</b> following <code>@{username}</code>**\n\n"
        for p in fans:
            followers += f"\nName: {p} : Link to Profile: https://www.instagram.com/{p}"
        text_file = f"{username}_non_followers.txt"
        with open(text_file, "w") as f:
            f.write(followers)
        await bot.send_document(
            chat_id=chat_id,
            document=text_file,
            caption=f"{name}'s non-followers\n\nA Project By [XTZ_Bots](https://t.me/subin_works)"
        )
        os.remove(text_file)

@Client.on_message(filters.command("feed") & filters.private)
async def feed(bot, message):
    if str(message.from_user.id) != OWNER:
        await message.reply_text(
            HOME_TEXT.format(message.from_user.first_name, message.from_user.id, USER, USER, USER, OWNER),
            reply_markup=buttons,
            disable_web_page_preview=True
        )
        return
    text = message.text
    count = None
    if " " in text:
        cmd, count = text.split(' ')
    if 1 not in STATUS:
        await message.reply_text("You must login first /login")
        return
    m = await message.reply_text("Fetching posts in your feed.")
    chat_id = message.from_user.id
    dir = f"{chat_id}/{USER}"
    await m.edit("Starting downloading...\nThis may take longer depending on the number of posts.")
    command = [
        "instaloader",
        "--no-metadata-json",
        "--no-compress-json",
        "--no-profile-pic",
        "--no-captions",
        "--no-video-thumbnails",
        "--login", USER,
        "-f", session,
        "--dirname-pattern", dir,
        ":feed"
    ]
    if count:
        command.extend(["--count", count])
    await download_insta(command, m, dir)
    await upload(m, bot, chat_id, dir)

@Client.on_message(filters.command("saved") & filters.private)
async def saved(bot, message):
    if str(message.from_user.id) != OWNER:
        await message.reply_text(
            HOME_TEXT.format(message.from_user.first_name, message.from_user.id, USER, USER, USER, OWNER),
            reply_markup=buttons,
            disable_web_page_preview=True
        )
        return
    text = message.text
    count = None
    if " " in text:
        cmd, count = text.split(' ')
    if 1 not in STATUS:
        await message.reply_text("You must login first /login")
        return
    m = await message.reply_text("Fetching your saved posts.")
    chat_id = message.from_user.id
    dir = f"{chat_id}/{USER}"
    await m.edit("Starting downloading...\nThis may take longer depending on the number of posts.")
    command = [
        "instaloader",
        "--no-metadata-json",
        "--no-compress-json",
        "--no-profile-pic",
        "--no-captions",
        "--no-video-thumbnails",
        "--login", USER,
        "-f", session,
        "--dirname-pattern", dir,
        ":saved"
    ]
    if count:
        command.extend(["--count", count])
    await download_insta(command, m, dir)
    await upload(m, bot, chat_id, dir)

@Client.on_message(filters.command("tagged") & filters.private)
async def tagged(bot, message):
    text = message.text
    username = USER
    if " " in text:
        cmd, username = text.split(' ')
    if not await check_private_account(bot, message, username):
        return
    m = await message.reply_text(f"Fetching the posts in which <code>@{username}</code> is tagged.")
    chat_id = message.from_user.id
    dir = f"{chat_id}/{username}"
    await m.edit("Starting downloading...\nThis may take longer depending on the number of posts.")
    command = [
        "instaloader",
        "--no-metadata-json",
        "--no-compress-json",
        "--no-profile-pic",
        "--tagged",
        "--no-captions",
        "--no-video-thumbnails",
        "--login", USER,
        "-f", session,
        "--dirname-pattern", dir,
        username
    ]
    await download_insta(command, m, dir)
    await upload(m, bot, chat_id, dir)

@Client.on_message(filters.command("story") & filters.private)
async def story(bot, message):
    text = message.text
    username = USER
    if " " in text:
        cmd, username = text.split(' ')
    if not await check_private_account(bot, message, username):
        return
    m = await message.reply_text(f"Fetching stories of <code>@{username}</code>")
    chat_id = message.from_user.id
    dir = f"{chat_id}/{username}"
    await m.edit("Starting downloading...\nThis may take longer depending on the number of posts.")
    command = [
        "instaloader",
        "--no-metadata-json",
        "--no-compress-json",
        "--no-profile-pic",
        "--stories",
        "--no-captions",
        "--no-video-thumbnails",
        "--login", USER,
        "-f", session,
        "--dirname-pattern", dir,
        username
    ]
    await download_insta(command, m, dir)
    await upload(m, bot, chat_id, dir)

@Client.on_message(filters.command("stories") & filters.private)
async def stories(bot, message):
    if str(message.from_user.id) != OWNER:
        await message.reply_text(
            HOME_TEXT.format(message.from_user.first_name, message.from_user.id, USER, USER, USER, OWNER),
            reply_markup=buttons,
            disable_web_page_preview=True
        )
        return
    if 1 not in STATUS:
        await message.reply_text("You must login first /login")
        return
    m = await message.reply_text("Fetching stories of all your followees")
    chat_id = message.from_user.id
    dir = f"{chat_id}/{USER}"
    await m.edit("Starting downloading...\nThis may take longer depending on the number of posts.")
    command = [
        "instaloader",
        "--no-metadata-json",
        "--no-compress-json",
        "--no-profile-pic",
        "--no-captions",
        "--no-video-thumbnails",
        "--login", USER,
        "-f", session,
        "--dirname-pattern", dir,
        ":stories"
    ]
    await download_insta(command, m, dir)
    await upload(m, bot, chat_id, dir)

@Client.on_message(filters.command("highlights") & filters.private)
async def highlights(bot, message):
    text = message.text
    username = USER
    if " " in text:
        cmd, username = text.split(' ')
    if not await check_private_account(bot, message, username):
        return
    m = await message.reply_text(f"Fetching highlights from profile <code>@{username}</code>")
    chat_id = message.from_user.id
    dir = f"{chat_id}/{username}"
    await m.edit("Starting downloading...\nThis may take longer depending on the number of posts.")
    command = [
        "instaloader",
        "--no-metadata-json",
        "--no-compress-json",
        "--no-profile-pic",
        "--highlights",
        "--no-captions",
        "--no-video-thumbnails",
        "--login", USER,
        "-f", session,
        "--dirname-pattern", dir,
        username
    ]
    await download_insta(command, m, dir)
    await upload(m, bot, chat_id, dir)