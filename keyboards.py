from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="⭐ Баланс")],
            [KeyboardButton(text="📋 Задание"), KeyboardButton(text="💸 Вывод")],
        ],
        resize_keyboard=True,
    )
