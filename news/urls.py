from django.urls import path
from . import views

urlpatterns = [
    path('', views.news_objects, name='news_list'),
    #path('photo/<int:pk>/', views.news_detail, name='news_detail'),
    #path('photo/<int:pk>/edit/', views.news_edit, name='news_edit'),
]