import re
import kss
from typing import List


class NewsCleaner:
    def __init__(self):
        super(NewsCleaner, self).__init__()

    @staticmethod
    def remove_reporter_info(article_original: List[str]) -> List[str]:
        email_pattern = re.compile(r"[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        reporter_pattern = re.compile(r"^\/?([가-힣]+)\s?(기자|팀)+\s*\.?$")

        texts = []
        reporters = []
        for sentence in article_original:
            ## If we can find email pattern in one sentence:
            email = email_pattern.findall(sentence)
            if email != []:
                continue

            ## We don't care about "OOO 기자 OOO 기자", not "OOO 기자"
            reporter = reporter_pattern.findall(sentence)
            if reporter != []:
                reporters.extend([i[0] for i in reporter])
                continue

            ## If known reporter name is in sentence...
            if any([i in sentence for i in reporters]):
                continue

            texts.append(sentence)

        return texts

    @staticmethod
    def remove_url(article_original: List[str]) -> List[str]:
        url_pattern = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*,]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
                                 re.MULTILINE)

        texts = "\n".join(article_original)
        texts = url_pattern.sub("", texts)

        return texts.split("\n")

    @staticmethod
    def remove_phone_number(article_original: List[str]) -> List[str]:
        phone_pattern = re.compile(r"""(
            (\d{2}|\(\d{2}\)|\d{3}|\(\d{3}\))?      ## 2 or 3 words include "(...)" patterns -> optional
            (|-|\.)?                                ## sep word: "." or "-"
            (\d{3}|\d{4})                           ## 3 or 4 numbers
            (\s|-|\.)                               ## sep word: "." or "-"
            (\d{4})                                 ## 4 numbers
        )""", re.VERBOSE | re.MULTILINE)

        texts = "\n".join(article_original)
        texts = phone_pattern.sub("", texts)

        return texts.split("\n")

    @staticmethod
    def remove_brack_sentence(article_original: List[str]) -> List[str]:
        bracket_1_pattern = re.compile(r"\s?<.*>", re.MULTILINE)  ## e.g.
        bracket_2_pattern = re.compile(r"\s?\(.*\)", re.MULTILINE)  ## e.g.
        bracket_3_pattern = re.compile(r"\s?\[.*\]", re.MULTILINE)  ## e.g.

        texts = "\n".join(article_original)
        texts = bracket_1_pattern.sub("", texts)
        texts = bracket_2_pattern.sub("", texts)
        texts = bracket_3_pattern.sub("", texts)

        return texts.split("\n")

    @staticmethod
    def split_sentence(article_original: List[str]) -> List[str]:
        result_list = []
        for item in article_original:
            if any(punctuation in item[:-1] for punctuation in [".", "!", "?"]):
                result_list.extend(kss.split_sentences(item))
            else:
                result_list.append(item)

        return result_list

    @staticmethod
    def apply(article_original: List[str]) -> List[str]:
        texts = NewsCleaner.remove_reporter_info(article_original)
        texts = NewsCleaner.remove_url(texts)
        texts = NewsCleaner.remove_phone_number(texts)
        texts = NewsCleaner.remove_brack_sentence(texts)

        texts = NewsCleaner.split_sentence(texts)

        return texts
