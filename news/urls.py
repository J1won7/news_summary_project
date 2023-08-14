from django.urls import path
from .views import newsAPI
from . import views

urlpatterns = [
    path('', newsAPI),
    path('<int:category>', newsAPI)
]

