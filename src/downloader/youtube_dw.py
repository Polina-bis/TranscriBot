import os
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from src.downloader.downloader import Downloader


class YouTubeDownloader(Downloader):
    def __extract_video_id(self, youtube_url):
        parsed_url = urlparse(youtube_url)
    
        if parsed_url.netloc == 'youtu.be':
            return parsed_url.path[1:]
    
        if parsed_url.netloc in ('www.youtube.com', 'youtube.com'):
            if parsed_url.path == '/watch':
                return parse_qs(parsed_url.query)['v'][0]
            elif parsed_url.path.startswith('/embed/'):
                return parsed_url.path.split('/')[2]
            elif parsed_url.path.startswith('/v/'):
                return parsed_url.path.split('/')[2]
    
        raise ValueError(f"Could not extract video ID from URL: {youtube_url}")
    
    def download_source(self, directory: str, source: str) -> str:
        video_id = self.__extract_video_id(source)
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["en", "ru"])
        subtitles = ' '.join([entry['text'] for entry in transcript])

        if not os.path.exists(directory):
            os.makedirs(directory)

        full_path = f"{directory}/{video_id}.txt"

        # проверяем сохранен ли такой файл
        if os.path.exists(full_path):
            print(f"Файл {full_path} уже существует!")
        else:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(subtitles)

        return full_path


if __name__ == "__main__":
    downl = YouTubeDownloader()
    print(downl.download_source("../data/cash/youtube/transcrib", "https://youtu.be/c5Nh4g8zwyo?si=tvmkOKXOKMlgE3LR"))