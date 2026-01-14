from django.urls import path, include
from .views import MovieHomepageView

app_name = 'movies'

urlpatterns = [
    path('homepage/', MovieHomepageView.as_view(), name='homepage'),
]