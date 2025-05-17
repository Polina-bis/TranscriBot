from urllib.parse import urlparse, parse_qs
import re
from aiogram import types

class YoutubeLinkFilter:
    def __init__(self):
        # Регулярные выражения для основных форматов ссылок YouTube
        self.youtube_domains = [
            'youtube.com',
            'www.youtube.com',
            'm.youtube.com',
            'youtu.be',
            'www.youtu.be'
        ]

        self.video_id_pattern = re.compile(
            r'^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*'
        )

    def __call__(self, message: types.Message) -> bool:
        text = message.text or message.caption
        if not text:
            return False

        return self.is_youtube_url(text)

    def is_youtube_url(self, url: str) -> bool:
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ('http', 'https'):
                return False

            # Проверка домена
            if parsed.netloc.lower() not in self.youtube_domains:
                return False

            # Проверка наличия video ID
            if parsed.netloc.lower() == 'youtu.be':
                video_id = parsed.path[1:]  # Убираем первый слеш
            else:
                query = parse_qs(parsed.query)
                video_id = query.get('v', [''])[0]
                if not video_id:
                    match = self.video_id_pattern.match(url)
                    video_id = match.group(2) if match else None

            return bool(video_id)

        except:
            return False