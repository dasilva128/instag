import re
from config import Config
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import *
from instaloader import Profile

USER = Config.USER
OWNER = Config.OWNER
HOME_TEXT = Config.HOME_TEXT
HELP = Config.HELP
session = f"./{USER}"
STATUS = Config.STATUS
insta = Config.L

@Client.on_message(filters.command("account") & filters.private)
async def account(bot, message):
    if str(message.from_user.id) != OWNER:
        await message.reply_text(
            HOME_TEXT.format(message.from_user.first_name, message.from_user.id, USER, USER, USER, int(OWNER)),
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
    if 1 not in STATUS:
        await message.reply_text("You must login first by /login")
        return
    m = await message.reply_text("Getting your data")
    try:
        profile = Profile.own_profile(insta.context)
        mediacount = profile.mediacount
        name = profile.full_name
        bio = profile.biography
        profilepic = profile.profile_pic_url
        username = profile.username
        igtvcount = profile.igtvcount
        followers = profile.followers
        following = profile.followees
        reply_markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Download My Profile Pic", callback_data=f"ppic#{username}")
            ],
            [
                InlineKeyboardButton("Download All My Post", callback_data=f"post#{username}"),
                InlineKeyboardButton("Download All Tagged Posts", callback_data=f"tagged#{username}")
            ],
            [
                InlineKeyboardButton("Download Posts In My Feed", callback_data=f"feed#{username}"),
                InlineKeyboardButton("Download My Saved Posts", callback_data=f"saved#{username}")
            ],
            [
                InlineKeyboardButton("Download My IGTV Posts", callback_data=f"igtv#{username}"),
                InlineKeyboardButton("Download My Highlights", callback_data=f"highlights#{username}")
            ],
            [
                InlineKeyboardButton("Download My Stories", callback_data=f"stories#{username}"),
                InlineKeyboardButton("Download Stories of My Followees", callback_data=f"fstories#{username}")
            ],
            [
                InlineKeyboardButton("Get a List Of My Followers", callback_data=f"followers#{username}"),
                InlineKeyboardButton("Get a List Of My Followees", callback_data=f"followees#{username}")
            ]
        ])
        await m.delete()
        await bot.send_photo(
            chat_id=message.from_user.id,
            photo=profilepic,
            caption=f"🏷 **Name**: {name}\n🔖 **Username**: {profile.username}\n📝 **Bio**: {bio}\n📍 **Account Type**: {acc_type(profile.is_private)}\n🏭 **Is Business Account?**: {yes_or_no(profile.is_business_account)}\n👥 **Total Followers**: {followers}\n👥 **Total Following**: {following}\n📸 **Total Posts**: {mediacount}\n📺 **IGTV Videos**: {igtvcount}",
            reply_markup=reply_markup
        )
    except Exception as e:
        await m.edit(f"Error: {e}")

@Client.on_message(filters.text & filters.private & filters.incoming)
async def _insta_post_batch(bot, message):
    if str(message.from_user.id) != OWNER:
        await message.reply_text(
            HOME_TEXT.format(message.from_user.first_name, message.from_user.id, USER, USER, USER, int(OWNER)),
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
    if 1 not in STATUS:
        await message.reply_text("You must login first /login")
        return
    m = await message.reply_text("Fetching data from Instagram 🔗")
    chat_id = message.from_user.id
    username = message.text
    if "https://instagram.com/stories/" in username:
        await m.edit("Stories from links are not yet supported 🥴\n\nYou can download stories from Username.")
        return

    link = r'^https://www\.instagram\.com/([A-Za-z0-9._]+/)?(p|tv|reel)/([A-Za-z0-9\-_]*)'
    result = re.search(link, username)

    if result:
        Post_type = {'p': 'POST', 'tv': 'IGTV', 'reel': 'REELS'}
        supported = Post_type.get(result.group(2))
        if not supported:
            await m.edit('Unsupported format')
            return
        sent = await m.edit(f'Fetching {supported} content from Instagram.')
        shortcode = result.group(3)
        try:
            dir = f"{chat_id}/{shortcode}"
            command = [
                "instaloader",
                "--no-metadata-json",
                "--no-compress-json",
                "--no-captions",
                "--no-video-thumbnails",
                "--login", USER,
                "-f", session,
                "--dirname-pattern", dir,
                f"-{shortcode}"
            ]
            await download_insta(command, sent, dir)
            await upload(sent, bot, chat_id, dir)
        except Exception as e:
            await bot.send_message(chat_id=chat_id, text=f"Error: {e}")
    elif "https://" in username:
        await m.edit('Unsupported format')
    else:
        await m.edit(f"Fetching details for <code>@{username}</code>")
        try:
            profile = Profile.from_username(insta.context, username)
            mediacount = profile.mediacount
            name = profile.full_name
            profilepic = profile.profile_pic_url
            igtvcount = profile.igtvcount
            bio = profile.biography
            followers = profile.followers
            following = profile.followees
            is_followed = yes_or_no(profile.followed_by_viewer)
            is_following = yes_or_no(profile.follows_viewer)
            type = acc_type(profile.is_private)
            reply_markup = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("Profile Pic", callback_data=f"ppic#{username}")
                ],
                [
                    InlineKeyboardButton("All Post", callback_data=f"post#{username}"),
                    InlineKeyboardButton("All Tagged Posts", callback_data=f"tagged#{username}")
                ],
                [
                    InlineKeyboardButton("All IGTV", callback_data=f"igtv#{username}"),
                    InlineKeyboardButton("Stories", callback_data=f"stories#{username}"),
                    InlineKeyboardButton("Highlights", callback_data=f"highlights#{username}")
                ],
                [
                    InlineKeyboardButton(f"{name}'s Followers", callback_data=f"followers#{username}"),
                    InlineKeyboardButton(f"{name}'s Followees", callback_data=f"followees#{username}")
                ]
            ] if type == "🔓Public🔓" or is_followed == "Yes" else [
                [
                    InlineKeyboardButton("Download Profile Pic", callback_data=f"ppic#{username}")
                ]
            ])
            await m.delete()
            await bot.send_photo(
                chat_id=chat_id,
                photo=profilepic,
                caption=f"🏷 **Name**: {name}\n🔖 **Username**: {profile.username}\n📝 **Bio**: {bio}\n📍 **Account Type**: {type}\n🏭 **Is Business Account?**: {yes_or_no(profile.is_business_account)}\n👥 **Total Followers**: {followers}\n👥 **Total Following**: {following}\n**👤 Is {name} Following You?**: {is_following}\n**👤 Are You Following {name}?**: {is_followed}\n📸 **Total Posts**: {mediacount}\n📺 **IGTV Videos**: {igtvcount}",
                reply_markup=reply_markup
            )
        except Exception as e:
            await m.edit(f"Error: {e}")