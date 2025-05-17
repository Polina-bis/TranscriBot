import datetime
import time

from aiogram import types, Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.db_helper.db_helper import DbHelper
from src.downloader.youtube_dw import YouTubeDownloader
from src.bot.filter.is_youtube_link import YoutubeLinkFilter
from src.bot.handlers.markups.choose_doing import markup_choose_doing
from src.bot.handlers.summ_and_transcrib.message_text import create_answer_not_enough_tokens, \
    create_answer_message_in_queue, youtube_texts
from src.bot.states.youtube_states import YoutubeStates

router = Router()


@router.message(F.text.endswith("Видео на Ютуб"))
async def start_youtube(message: types.Message, state: FSMContext):
    # Инициализируем список для хранения ID сообщений
    await state.update_data(message_ids=[message.message_id])
    answer = await message.answer(youtube_texts["start_youtube"])
    # Добавляем ID нового сообщения в state
    data = await state.get_data()
    message_ids = data.get("message_ids", [])
    message_ids.append(answer.message_id)
    await state.update_data(message_ids=message_ids)
    await state.set_state(YoutubeStates.wait_link)


@router.message(YoutubeLinkFilter(), YoutubeStates.wait_link)
async def download_youtube(message: types.Message, state: FSMContext, bot: Bot):
    # Добавляем ID голосового сообщения в state
    data = await state.get_data()
    message_ids = data.get("message_ids", [])
    message_ids.append(message.message_id)
    await state.update_data(message_ids=message_ids)

    # скачиваем
    downloader = YouTubeDownloader()
    file_path, length_video = downloader.download_source("../../src/data/cash/youtube/transcrib", message.text)
    # сохраняем путь
    await state.update_data({"youtube_path": file_path})
    await state.update_data({"tokens": length_video})

    answer = await message.answer(youtube_texts["choose_doing"], reply_markup=markup_choose_doing(length_video))
    # Добавляем ID нового сообщения в state
    message_ids.append(answer.message_id)
    await state.update_data(message_ids=message_ids)
    await state.set_state(YoutubeStates.wait_doing)


@router.message(YoutubeStates.wait_link)
async def download_youtube(message: types.Message, state: FSMContext):
    # Добавляем ID сообщения в state
    data = await state.get_data()
    message_ids = data.get("message_ids", [])
    message_ids.append(message.message_id)
    await state.update_data(message_ids=message_ids)

    markup = InlineKeyboardBuilder()
    chancel = types.InlineKeyboardButton(
        text="❌ Отмена",
        callback_data="cancel"
    )
    markup.add(chancel)

    answer = await message.answer(youtube_texts["wrong_media"], reply_markup=markup.as_markup())
    # Добавляем ID нового сообщения в state
    message_ids.append(answer.message_id)
    await state.update_data(message_ids=message_ids)
    await state.set_state(YoutubeStates.wait_link)


@router.callback_query(F.data.in_({"transcribe", "summ"}), YoutubeStates.wait_doing)
async def process_youtube(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    tokens = data["tokens"]

    db_helper = DbHelper()
    current_tokens = db_helper.select_rows(
        "users",
        ["tokens_amount"],
        {"user_id": callback.message.chat.id}
    )[0][0]

    # Определяем нужное количество токенов
    required_tokens = tokens * 2 if callback.data == "summ" else tokens

    if current_tokens < required_tokens:
        # Редактируем сообщение с кнопками вместо отправки нового
        text = create_answer_not_enough_tokens(current_tokens, required_tokens)
        await callback.message.edit_text(text)
        await state.clear()
        return

    # Редактируем сообщение с информацией об очереди
    position = 2  # TODO: Реальная позиция в очереди
    text = create_answer_message_in_queue(position)
    await callback.message.edit_text(text)
    time.sleep(5)

    if callback.data == "transcribe":
        result_file = data["youtube_path"]
    else:
        #  вызываем суммариз
        result_file = ""

    with open(result_file, 'r', encoding='utf-8') as file:
        result = file.read()
        if len(result) <= 4096:
            await callback.message.edit_text(result)
        else:
            # Если текст слишком длинный
            await callback.message.edit_text(youtube_texts["long_answer"])
            file = FSInputFile(result_file)
            await callback.message.answer_document(file)

    # снимаем со счета пользователя
    db_helper.update_row(
        "users",
        {"user_id": callback.message.chat.id},
        {"tokens_amount": current_tokens - required_tokens}
    )

    # записываем историю поиска
    history_param = {
        "user_id": callback.message.chat.id,
        "date": datetime.date.today(),
        "operation_type": "tran" if callback.data == "transcribe" else "summ",
        "source_type": "yt",
        "source_link": result_file
    }
    db_helper.insert_row("user_history", history_param)

    await state.clear()


@router.callback_query(F.data == "cancel")
async def cancel(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    # Получаем список ID сообщений из state
    data = await state.get_data()
    message_ids = data.get("message_ids", [])

    # Удаляем все сообщения
    for message_id in message_ids:
        try:
            await bot.delete_message(chat_id=callback.message.chat.id, message_id=message_id)
        except Exception as e:
            print(f"Не удалось удалить сообщение {message_id}: {e}")

    await state.clear()