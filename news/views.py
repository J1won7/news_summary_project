from django.shortcuts import render
from .models import News


def news_objects(request):
    news_objects = News.objects.order_by('-time')[:20]
    return render(request, 'news/news_list.html', {'news_objects': news_objects})
