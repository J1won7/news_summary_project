from django.shortcuts import render
from .models import News


def news_objects(request, category=100):
    news_objects = News.objects.filter(category=category).order_by('-time')[:20]
    return render(request, 'news/news_list.html', {'news_objects': news_objects})
