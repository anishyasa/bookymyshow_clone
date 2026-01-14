from django.urls import path
from .views import MovieScheduleView

urlpatterns = [
    path(
        'movies/<int:event_id>/schedule/', 
        MovieScheduleView.as_view(), 
        name='movie-weekly-schedule'
    ),
]