import os
import sys
import django

from apscheduler.schedulers.background import BackgroundScheduler
from .newsSummary import crawling_headline_news


#디렉토리 인식 및 Django 환경변수 끌어오기
FILE_DIR = os.path.abspath(os.path.join(os.path.realpath(__file__), os. pardir))
BASE_DIR = os.path.abspath(os.path.join(os.path.realpath(FILE_DIR), os.pardir))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myweb.settings")
django.setup()

sched = BackgroundScheduler()

from news.models import News


def crawl_and_save_data():
    news_objects = crawling_headline_news()

    for news_obj in news_objects:
        News.objects.create(
            _id=news_obj["_id"],
            category=news_obj["category"],
            title=news_obj["title"],
            image=news_obj["image"],
            summary=news_obj["summary"],
            time=news_obj["time"],
            url=news_obj["url"]
        )


def start_crawling():
    sched.add_job(crawl_and_save_data, "interval", minutes=5)
    sched.start()
