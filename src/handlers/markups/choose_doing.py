from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types


def markup_choose_doing(tokens: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardBuilder()
    transcribe = types.InlineKeyboardButton(
        text=f"📝 Транскрибация ({tokens} токенов)",
        callback_data="transcribe"
    )
    summ = types.InlineKeyboardButton(
        text=f"✨ Суммаризация ({tokens * 2} токенов)",
        callback_data="summ"
    )
    chancel = types.InlineKeyboardButton(
        text="❌ Отмена",
        callback_data="cancel"
    )
    markup.add(transcribe, summ, chancel)
    markup.adjust(1, 1, 1)

    return markup.as_markup()
