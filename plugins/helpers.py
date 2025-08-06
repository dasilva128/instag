from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Optional

def create_keyboard(buttons: List[List[dict]]) -> InlineKeyboardMarkup:
    """Create inline keyboard from button structure"""
    keyboard = []
    for row in buttons:
        keyboard_row = []
        for btn in row:
            keyboard_row.append(
                InlineKeyboardButton(
                    text=btn.get("text", ""),
                    callback_data=btn.get("callback", "")
                )
            )
        keyboard.append(keyboard_row)
    return InlineKeyboardMarkup(keyboard)

def format_user_info(profile) -> str:
    """Format Instagram profile information"""
    return (
        f"👤 **{profile.full_name}** (@{profile.username})\n\n"
        f"📝 **Bio:** {profile.biography}\n"
        f"🔒 **Private:** {'✅ Yes' if profile.is_private else '❌ No'}\n"
        f"🏢 **Business:** {'✅ Yes' if profile.is_business_account else '❌ No'}\n"
        f"📸 **Posts:** {profile.mediacount}\n"
        f"🎥 **IGTV:** {profile.igtvcount}\n"
        f"👥 **Followers:** {profile.followers}\n"
        f"🔄 **Following:** {profile.followees}"
    )