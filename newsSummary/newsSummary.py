import json
import re
import requests
import time
from bs4 import BeautifulSoup
from .koBertSumExt import BertSumExt


head = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/114.0.0.0 Whale/3.21.192.18 Safari/537.36"}
delay_time = 0.5


def get_content_from_naver_news_url(url):
    response = requests.get(url, headers=head)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.find('div', {"class": "media_end_head_title"}).get_text(strip=True)
    content = soup.select_one("#newsct_article").get_text('\n').split('\n')

    content = [line.strip() for line in content if line.strip()]

    data_time = soup.find('span', {"class": "media_end_head_info_datestamp_time _ARTICLE_DATE_TIME"}).attrs[
        'data-date-time']
    image = soup.find('img', id='img1')

    if image is None:
        image = ''
    else:
        image = image.attrs['data-src']

    return title, content, image, data_time


def get_summary_from_naver_news_url(url):
    response = requests.get(url, headers=head)
    data = json.loads(response.text)

    # title = data['title']
    summary = data['summary']
    result_code = data['result_code']

    return result_code, re.sub('<.*?>', ' ', summary)


def get_data_from_naver_news_url(url):
    # result_code는 요약문이 존재하는 경우 1을 존재 하지 않는 경우 0을 반환
    result_code, summary = get_summary_from_naver_news_url(
        f"https://tts.news.naver.com/article/{url[39:53]}/summary")
    if result_code == 1:
        time.sleep(delay_time)
        title, content, image, write_time = get_content_from_naver_news_url(url)
        return True, title, content, summary, image, write_time
    else:
        return False, None, None, None


def crawling_headline_news():
    bert_sum = BertSumExt()
    news_objects = []

    for category in range(100, 106):
        urls = []
        news_list_url = f"https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1={category}"
        response = requests.get(news_list_url, headers=head)
        soup = BeautifulSoup(response.text, 'html.parser')

        results = soup.select_one("#main_content > div > div._persist > div.section_headline > ul")

        for i in range(1, 11):
            try:
                result = results.select_one(f"li:nth-child({i}) > div.sh_text > a")
                if result is not None:
                    urls.append(result.attrs['href'])
            except Exception as e:
                print(f"뉴스 리스트 크롤링 중 에러 발생 : {e}")
        for url in urls:
            try:
                news_id = url[43:53]
                #media = url[39:42]

                title, content, image, write_time = get_content_from_naver_news_url(url)

                summary = bert_sum(content)

                news_objects.append({"_id": news_id, "category": category, "title": title, "summary": summary,
                                    "image": image, "time": write_time, "url": url})

            except Exception as e:
                print(f"뉴스 본문 크롤링 중 에러 발생 : {e}")

        print(f"카테고리[{category}] : 데이터 크롤링 완료")

    return news_objects


