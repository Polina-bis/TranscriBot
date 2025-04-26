import os
from src.downloader.downloader import Downloader
from aiogram import Bot


class CircleDownloader(Downloader):
    def __init__(self, bot):
        self.bot: Bot = bot

    def download_source(self, directory: str, source_id: str) -> str:
        # проверяем есть ли папка, в которую хотим сохранить
        if not os.path.exists(directory):
            os.makedirs(directory)

        full_path = f"{directory}/{source_id}.mp4"
        # проверяем сохранен ли такой файл
        if os.path.exists(full_path):
            print(f"Файл {full_path} уже существует!")
        else:
            self.bot.download(source_id, destination=full_path)

        return full_path