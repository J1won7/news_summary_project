from django.urls import path
from . import views

urlpatterns = [
    path('', views.news_objects, name='news_list'),
    path('<int:category>', views.news_objects, name='news_list_by_category'),
]