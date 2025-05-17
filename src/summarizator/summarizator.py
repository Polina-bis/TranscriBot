from abc import ABC, abstractmethod
from os.path import abspath
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import nltk
nltk.download('punkt_tab')


degree_coefficients = {'long': 2, 'medium': 3, 'short': 4}


class Summarizer(ABC):
    @abstractmethod
    def summarize(self, from_path: str, to_path: str, degree: str):
        pass

    def _tuple_into_string(self, input_tuple: tuple) -> str:
        string = ''

        for el in input_tuple:
            string += str(el)

        return string


class SumySummarizer(Summarizer):

    def summarize(self, from_path: str, to_path: str, degree: str):
        context = ''
        full_summary = ''

        with open(from_path, 'r', encoding='utf-8') as file:
            while True:
                fractional_chunk = file.read(500)

                if not fractional_chunk:
                    break
                else:
                    fractional_chunk += context

                context = fractional_chunk.split('.').pop()
                holistic_chunk = fractional_chunk[:-len(context)] if len(context) else fractional_chunk

                parser = PlaintextParser.from_string(holistic_chunk, Tokenizer("russian"))
                summarizer = LsaSummarizer()
                sentence_amount = len(holistic_chunk.split('.'))//degree_coefficients.get(degree)

                if sentence_amount == 0:
                    sentence_amount = 1

                summary = summarizer(parser.document, sentence_amount)
                full_summary += self._tuple_into_string(summary)

        with open(to_path, 'w', encoding='utf-8') as file:
            file.write(full_summary)


if __name__ == '__main__':
    from_path = abspath('../data/cash/youtube/transcrib/test.txt')
    to_path = abspath('../data/cash/youtube/summaries/test.txt')

    summarizer = SumySummarizer()
    summarizer.summarize(from_path, to_path, 'short')
