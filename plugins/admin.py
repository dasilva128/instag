from pyrogram import filters
from pyrogram.types import Message
from config import Config

async def is_admin(message: Message) -> bool:
    """Check if user is admin/owner"""
    return str(message.from_user.id) == Config.OWNER

@Client.on_message(filters.command("stats") & filters.private)
async def stats_command(bot: Client, message: Message):
    if not await is_admin(message):
        return
        
    from instaloader import Profile
    profile = Profile.own_profile(Config.L.context)
    
    await message.reply(
        "📊 **Bot Statistics**\n\n"
        f"🖼 **Posts Downloaded:** {profile.mediacount}\n"
        f"🎥 **IGTV Downloaded:** {profile.igtvcount}\n"
        f"👥 **Followers Tracked:** {profile.followers}\n"
        f"🔄 **Following Tracked:** {profile.followees}"
    )

@Client.on_message(filters.command("clean") & filters.private)
async def clean_command(bot: Client, message: Message):
    if not await is_admin(message):
        return
        
    import shutil
    shutil.rmtree(f"./{Config.USER}", ignore_errors=True)
    await message.reply("🧹 Cache cleaned successfully!")