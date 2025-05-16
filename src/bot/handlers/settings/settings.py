from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from src.bot.handlers.settings.keyboards import *
from src.db_helper.db_helper import DbHelper
from datetime import date


texts = {'profile_info': '👤 Ваш профиль:\n\n- Маскимально доступное число токенов: {}\n- Доступно токенов сейчас: {}\
         \n- Запросов сегодня: {}',
         'history_header': 'История Вашего поиска:\n',
         'settings_info': '⚙️ Настройки:\n\n- 🔔 Уведомления: {}\n- 🌐 Язык транскрибации: {}',
         'notification_info': 'Уведомления {}',
         'choose_language': 'Выберите язык, на котором\n хотите получать тексты:',
         'output_info': '{}',
         'success_info': 'Хорошо! Я учёл эту информацию',
         'history_empty': 'Здесь пока ничего нет(\n Самое время транскрибировать или суммаризировать что-нибудь!'}

settings_router = Router()
db = DbHelper()
from src.run_bot import bot


def get_user_profile_info(user_id: int) -> tuple:

    total_tokens_amount = 120
    available_tokens_amount = db.select_rows('users', ['tokens_amount'],
                                             {'user_id': user_id})[0][0]

    today_requests = db.select_rows('user_history', ['record_id'],
                                    {'user_id': user_id, 'date': date.today()})
    today_requests_amount = len(today_requests)

    return total_tokens_amount, available_tokens_amount, today_requests_amount


def get_user_history_in_strings(user_id: int) -> list:
    user_history_in_tuples = db.get_printable_user_history(user_id)
    user_history_in_strings = []
    i = 1

    for tuple_record in user_history_in_tuples:
        history_record = f"{i}. {tuple_record[0]} - {tuple_record[1]} ({tuple_record[2]}) [Готово]"
        user_history_in_strings.append(history_record)
        i += 1

    return user_history_in_strings


@settings_router.message(F.text == "👤 Личный кабинет")
async def start_settings(message: Message):
    user_info = get_user_profile_info(message.from_user.id)
    await message.answer(
        texts['profile_info'].format(user_info[0], user_info[1], user_info[2]), reply_markup=profile_info_kb())


@settings_router.callback_query(F.data == 'profile')
async def start_settings(call: CallbackQuery):
    user_info = get_user_profile_info(call.from_user.id)

    await bot.edit_message_text(
        text=texts['profile_info'].format(user_info[0], user_info[1], user_info[2]),
        chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=profile_info_kb())


@settings_router.callback_query(F.data == 'show_history')
async def handle_show_history(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    user_history = get_user_history_in_strings(user_id)

    if len(user_history) < 11:
        answer = texts['history_empty'] if len(user_history) == 0 else texts['history_header'] + '\n'.join(user_history)
        await bot.edit_message_text(text=answer, chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    reply_markup=return_kb('profile'))
    else:
        max_page_num = (len(user_history)//10) + bool(len(user_history)%10)
        answer = texts['history_header'] + '\n'.join(user_history[:10])

        await state.update_data(current_page_num=1, max_page_num=max_page_num)
        await bot.edit_message_text(text=answer, chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    reply_markup=show_history_kb(1, max_page_num))


@settings_router.callback_query(F.data == 'next_page')
async def show_next_page(call: CallbackQuery, state: FSMContext):
    pages_data = await state.get_data()
    current_page_num = pages_data.get('current_page_num')
    max_page_num = pages_data.get('max_page_num')

    if current_page_num < max_page_num:
        user_id = call.from_user.id
        user_history = get_user_history_in_strings(user_id)

        if current_page_num + 1 == max_page_num:
            answer = texts['history_header'] + '\n'.join(user_history[current_page_num*10:])
        else:
            answer = texts['history_header'] + '\n'.join(user_history[current_page_num*10: (current_page_num+1)*10])

        await state.update_data(current_page_num=current_page_num+1)
        await bot.edit_message_text(text=answer, chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    reply_markup=show_history_kb(current_page_num+1, max_page_num))


@settings_router.callback_query(F.data == 'previous_page')
async def show_next_page(call: CallbackQuery, state: FSMContext):
    pages_data = await state.get_data()
    current_page_num = pages_data.get('current_page_num')
    max_page_num = pages_data.get('max_page_num')

    if current_page_num > 1:
        user_id = call.from_user.id
        user_history = get_user_history_in_strings(user_id)
        answer = texts['history_header'] + '\n'.join(user_history[(current_page_num-2)*10: (current_page_num-1)*10])

        await state.update_data(current_page_num=current_page_num-1)
        await bot.edit_message_text(text=answer, chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    reply_markup=show_history_kb(current_page_num-1, max_page_num))


@settings_router.callback_query(F.data == 'page_pos')
async def show_page_pos(call: CallbackQuery):
    await call.answer('Текущая страница')


@settings_router.callback_query(F.data == 'settings')
async def show_settings(call: CallbackQuery):
    user_id = call.from_user.id
    user_info = db.select_rows('users', ['notifications_status', 'transcription_language'],
                               {'user_id': user_id})[0]

    notification_status = 'Вкл' if user_info[0] == 1 else 'Выкл'

    transcription_language = db.select_rows('codes', ['rus_equivalent'],
                                            {'code_name': user_info[1]})[0][0].split()[0]

    answer = texts['settings_info'].format(notification_status, transcription_language)

    await bot.edit_message_text(text=answer, chat_id=call.message.chat.id, message_id=call.message.message_id,
                                reply_markup=show_settings_kb('Вкл' if notification_status == 'Выкл' else 'Выкл'))


@settings_router.callback_query(F.data == 'change_language')
async def change_language(call: CallbackQuery):
    languages = db.select_rows('codes', ['code_name', 'rus_equivalent'],
                               {'code_type': 'transcription_language'})
    await bot.edit_message_text(text=texts['choose_language'], chat_id=call.message.chat.id,
                                message_id=call.message.message_id, reply_markup=change_language_kb(languages))


@settings_router.callback_query(F.data.startswith('set_language'))
async def set_new_language(call: CallbackQuery):
    user_id = call.from_user.id
    new_language_code = call.data.replace('set_language_', '')
    db.update_row('users', {'user_id': user_id},
                  {'transcription_language': new_language_code})

    await bot.edit_message_text(text=texts['success_info'], chat_id=call.message.chat.id,
                                message_id=call.message.message_id, reply_markup=return_kb('settings'))


@settings_router.callback_query(F.data.startswith('turn_notifications'))
async def turn_notifications(call: CallbackQuery):
    user_id = call.from_user.id
    notifications_status = call.data.replace('turn_notifications_', '')

    if notifications_status == 'Выкл':
        notifications_status_text = 'выключены'
        db.update_row('users', {'user_id': user_id}, {'notifications_status': 0})
    else:
        notifications_status_text = 'включены'
        db.update_row('users', {'user_id': user_id}, {'notifications_status': 1})

    await bot.edit_message_text(text=texts['notification_info'].format(notifications_status_text),
                                chat_id=call.message.chat.id, message_id=call.message.message_id,
                                reply_markup=return_kb('settings'))
