from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import News
from .serializers import NewsSerializer

@api_view(['GET'])
def newsAPI(request, category=100):
    news_objects = News.objects.filter(category=category)
    serializer = NewsSerializer(news_objects, many=True)
    return Response(serializer.data)


'''
def news_objects(request):
    news_objects = News.objects.all().order_by('-time')[:20]
    return render(request, 'news/news_list.html', {'news_objects': news_objects})
'''