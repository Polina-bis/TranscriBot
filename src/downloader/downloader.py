from abc import ABC, abstractmethod


class Downloader(ABC):
    @abstractmethod
    def download_source(self, directory: str, source: str) -> str:
        pass
