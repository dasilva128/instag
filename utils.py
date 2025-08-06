import pytz
import asyncio
from config import Config
from datetime import datetime
import shutil
import glob
from videoprops import get_audio_properties
from pyrogram.errors import FloodWait
from pyrogram.types import InputMediaPhoto, InputMediaVideo, InlineKeyboardMarkup, InlineKeyboardButton

IST = pytz.timezone('Asia/Tehran')
USER = Config.USER
session = f"./{USER}"

async def download_insta(command, m, dir):
    try:
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        while True:
            output = await process.stdout.readline()
            if output == b'':
                break
            if output:
                datetime_ist = datetime.now(IST)
                ISTIME = datetime_ist.strftime("%I:%M:%S %p - %d %B %Y")
                msg = f"CURRENT_STATUS ⚙️: <code>{output.decode('UTF-8')}</code>\nLast Updated: <code>{ISTIME}</code>"
                msg = msg.replace(f'{dir}/', 'DOWNLOADED: ')
                try:
                    await m.edit(msg)
                except:
                    pass

        while True:
            error = await process.stderr.readline()
            if error == b'':
                break
            if error:
                datetime_ist = datetime.now(IST)
                ISTIME = datetime_ist.strftime("%I:%M:%S %p - %d %B %Y")
                ermsg = f"ERROR ❌: <code>{error.decode('UTF-8')}</code>\nLast Updated: <code>{ISTIME}</code>"
                try:
                    await m.edit(ermsg)
                except:
                    pass
        return True
    except Exception as e:
        await m.edit(f"Error during download: {e}")
        return False

def acc_type(val):
    return "🔒Private🔒" if val else "🔓Public🔓"

def yes_or_no(val):
    return "Yes" if val else "No"

async def upload(m, bot, chat_id, dir):
    try:
        videos = glob.glob(f"{dir}/*.mp4")
        VDO = []
        GIF = []

        for video in videos:
            try:
                has_audio = get_audio_properties(video)
                VDO.append(video)
            except Exception:
                GIF.append(video)

        PIC = glob.glob(f"{dir}/*.jpg")
        total_pics = len(PIC)
        total_videos = len(VDO)
        total_gifs = len(GIF)
        TOTAL = total_pics + total_videos + total_gifs

        if TOTAL == 0:
            await m.edit("There is nothing to download.")
            return

        await m.edit("Now starting upload to Telegram...")
        await m.pin(disable_notification=False, both_sides=True)

        up = 0
        rm = TOTAL

        if total_pics == 1:
            pic = PIC[0]
            await bot.send_photo(chat_id=chat_id, photo=pic)
            up += 1
            rm -= 1
            await m.edit(f"Total: {TOTAL}\nUploaded: {up} Remaining to upload: {rm}")

        if total_videos == 1:
            video = VDO[0]
            await bot.send_video(chat_id=chat_id, video=video)
            up += 1
            rm -= 1
            await m.edit(f"Total: {TOTAL}\nUploaded: {up} Remaining to upload: {rm}")

        if total_gifs == 1:
            gif = GIF[0]
            await bot.send_video(chat_id=chat_id, video=gif)
            up += 1
            rm -= 1
            await m.edit(f"Total: {TOTAL}\nUploaded: {up} Remaining to upload: {rm}")

        if total_pics >= 2:
            for i in range(0, len(PIC), 10):
                chunk = PIC[i:i + 10]
                media = [InputMediaPhoto(media=photo) for photo in chunk]
                try:
                    await bot.send_media_group(chat_id=chat_id, media=media, disable_notification=True)
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    await bot.send_media_group(chat_id=chat_id, media=media, disable_notification=True)
                up += len(chunk)
                rm -= len(chunk)
                await m.edit(f"Total: {TOTAL}\nUploaded: {up} Remaining to upload: {rm}")

        if total_videos >= 2:
            for i in range(0, len(VDO), 10):
                chunk = VDO[i:i + 10]
                media = [InputMediaVideo(media=video) for video in chunk]
                try:
                    await bot.send_media_group(chat_id=chat_id, media=media, disable_notification=True)
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    await bot.send_media_group(chat_id=chat_id, media=media, disable_notification=True)
                up += len(chunk)
                rm -= len(chunk)
                await m.edit(f"Total: {TOTAL}\nUploaded: {up} Remaining to upload: {rm}")

        if total_gifs >= 2:
            for gif in GIF:
                try:
                    await bot.send_video(chat_id=chat_id, video=gif)
                    up += 1
                    rm -= 1
                    await m.edit(f"Total: {TOTAL}\nUploaded: {up} Remaining to upload: {rm}")
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    await bot.send_video(chat_id=chat_id, video=gif)
                    up += 1
                    rm -= 1
                    await m.edit(f"Total: {TOTAL}\nUploaded: {up} Remaining to upload: {rm}")

        await m.unpin()
        await bot.send_message(
            chat_id=chat_id,
            text=f"Successfully uploaded {up} files to Telegram.\nIf you found me helpful, join my updates channel!",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("👨🏼‍💻 Developer", url='https://t.me/subinps'),
                    InlineKeyboardButton("🤖 Other Bots", url="https://t.me/subin_works/122")
                ],
                [
                    InlineKeyboardButton("🔗 Source Code", url="https://github.com/subinps/Instagram-Bot"),
                    InlineKeyboardButton("⚡️ Update Channel", url="https://t.me/subin_works")
                ]
            ])
        )
    except Exception as e:
        await m.edit(f"Error during upload: {e}")
    finally:
        shutil.rmtree(dir, ignore_errors=True)