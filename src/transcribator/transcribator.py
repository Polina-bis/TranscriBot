import os
from src.db_helper.db_helper import DbHelper


class Transcribator:
    def __init__(self):
        from faster_whisper import WhisperModel

        self.model = WhisperModel("medium")

    def transcribe(self, source_path: str, save_dir: str, title: str, user_id: int) -> str:
        """
        Функция транскрибирует любой медиа источник
        :param source_path: путь до медиа источника
        :param save_dir: папка, в которую нужно сохранить итоговую транскрибацию
        :param title: название итогового файла
        :param user_id: id пользователя
        :return: путь до итогового файла с транскрибацией источника
        """
        # определяет язык по первым секундам, но лучше передавать явно
        db_helper = DbHelper()
        transcription_language = db_helper.select_rows(
            "users",
            ["transcription_language"],
            {"user_id": user_id}
        )[0][0]

        language = "ru" if transcription_language == "rus" else "en"

        transcrib = ""
        segments, _ = self.model.transcribe(source_path, language=language, log_progress=True)
        for segment in segments:
            transcrib += segment.text

        print(transcrib)

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        full_path = f"{save_dir}/{title}.txt"

        # проверяем сохранен ли такой файл
        if os.path.exists(full_path):
            print(f"Файл {full_path} уже существует!")
        else:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(transcrib)

        return full_path


if __name__ == "__main__":
    trans = Transcribator()
    trans.transcribe(
        "../data/cash/voices/гс2.ogg",
        "../data/cash/voices/transcrib",
        "видео",
        5732193791
    )
