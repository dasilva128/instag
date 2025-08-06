from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import Client, filters
from config import Config
import asyncio
import sys
import os

USER = Config.USER
OWNER = Config.OWNER
HOME_TEXT = Config.HOME_TEXT
HOME_TEXT_OWNER = Config.HOME_TEXT_OWNER
HELP = Config.HELP

@Client.on_message(filters.command("start") & filters.private)
async def start(bot, cmd):
    if str(cmd.from_user.id) != OWNER:
        await cmd.reply_text(
            HOME_TEXT.format(cmd.from_user.first_name, cmd.from_user.id, USER, USER, USER, OWNER),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("👨🏼‍💻 Developer", url='https://t.me/savior_128'),
                    InlineKeyboardButton("🤖 Other Bots", url="https://t.me/savior_128")
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
    else:
        await cmd.reply_text(
            HOME_TEXT_OWNER.format(cmd.from_user.first_name, cmd.from_user.id),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("👨🏼‍💻 Developer", url='https://t.me/savior_128'),
                    InlineKeyboardButton("🤖 Other Bots", url="https://t.me/savior_128")
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

@Client.on_message(filters.command("help") & filters.private)
async def help(bot, cmd):
    await cmd.reply_text(
        HELP,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("👨🏼‍💻 Developer", url='https://t.me/savior_128'),
                InlineKeyboardButton("🤖 Other Bots", url="https://t.me/savior_128"),
                InlineKeyboardButton("⚙️ Update Channel", url="https://t.me/savior_128")
            ],
            [
                InlineKeyboardButton("🔗 Source Code", url="https://github.com/savior_128/Instagram-Bot")
            ]
        ])
    )

@Client.on_message(filters.command("restart") & filters.private)
async def restart(bot, cmd):
    if str(cmd.from_user.id) != OWNER:
        await cmd.reply_text(
            HOME_TEXT.format(cmd.from_user.first_name, cmd.from_user.id, USER, USER, USER, OWNER),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("👨🏼‍💻 Developer", url='https://t.me/savior_128'),
                    InlineKeyboardButton("🤖 Other Bots", url="https://t.me/savior_128")
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
    msg = await bot.send_message(chat_id=cmd.from_user.id, text="Restarting your bot...")
    await asyncio.sleep(2)
    await msg.edit("All processes stopped and restarted.")
    os.execl(sys.executable, sys.executable, *sys.argv)