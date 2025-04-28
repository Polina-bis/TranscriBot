import os
from src.downloader.downloader import Downloader
from aiogram import Bot


class VoiceDownloader(Downloader):
    def __init__(self, bot):
        self.bot: Bot = bot

    def download_source(self, directory: str, source_id: str) -> str:
        # проверяем есть ли папка, в которую хотим сохранить
        if not os.path.exists(directory):
            os.makedirs(directory)

        full_path = f"{directory}/{source_id}.ogg"
        # проверяем сохранен ли такой файл
        if os.path.exists(full_path):
            print(f"Файл {full_path} уже существует!")
        else:
            self.bot.download(source_id, destination=full_path)

        return full_path


if __name__ == "__main__":
    downl = VoiceDownloader(bot = Bot(token="7258847191:AAGCd4xDlAM4MjDlnGBfHtEmUNTU19Xc7E8"))
    downl.download_source("../../voices", "3452546")