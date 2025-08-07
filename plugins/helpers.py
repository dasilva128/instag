from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List

def create_keyboard(buttons: List[List[dict]]) -> InlineKeyboardMarkup:
    """
    ایجاد کیبورد اینلاین از ساختار دکمه‌ها
    
    Args:
        buttons (List[List[dict]]): لیست دکمه‌ها
        
    Returns:
        InlineKeyboardMarkup: کیبورد اینلاین
    """
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