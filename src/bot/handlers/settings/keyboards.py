from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def return_kb(callback_data: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="↩️Назад", callback_data=callback_data)]],
                                resize_keyboard=True)


def profile_info_kb() -> InlineKeyboardMarkup:
    buttons_list = [
            [InlineKeyboardButton(text='📜 История запросов', callback_data='show_history')],
            [InlineKeyboardButton(text='⚙️ Настройки', callback_data='settings')]
        ]
    return InlineKeyboardMarkup(inline_keyboard=buttons_list, resize_keyboard=True)


def show_history_kb(current_page_num: int, total_pages_num: int) -> InlineKeyboardMarkup:
    buttons_list = [
        [InlineKeyboardButton(text='⬅️10', callback_data='previous_page'),
         InlineKeyboardButton(text='{}/{}'.format(current_page_num, total_pages_num), callback_data='page_pos'),
         InlineKeyboardButton(text='10➡', callback_data='next_page')],
        [InlineKeyboardButton(text='↩️Назад', callback_data='profile')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons_list, resize_keyboard=True)


def show_settings_kb(notification_status) -> InlineKeyboardMarkup:
    buttons_list = [
        [InlineKeyboardButton(text='Изменить язык', callback_data='change_language')],
        [InlineKeyboardButton(text='{} уведомления'.format(notification_status),
                              callback_data='turn_notifications_{}'.format(notification_status))],
        [InlineKeyboardButton(text='↩️Назад', callback_data='profile')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons_list, resize_keyboard=True)


def change_language_kb(languages: list[tuple]) -> InlineKeyboardMarkup:
    buttons_list = [
        [InlineKeyboardButton(text=lang[1].split()[0], callback_data='set_language_' + lang[0])] for lang in languages
    ]
    buttons_list.append([InlineKeyboardButton(text='↩️ Назад', callback_data='settings')])
    return InlineKeyboardMarkup(inline_keyboard=buttons_list, resize_keyboard=True)
