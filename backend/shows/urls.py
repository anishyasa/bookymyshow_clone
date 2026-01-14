from django.urls import path
from .views import MovieScheduleView, ShowSeatListView

urlpatterns = [
    path(
        'movies/<int:event_id>/schedule/', 
        MovieScheduleView.as_view(), 
        name='movie-weekly-schedule'
    ),
    path('show-seats/<int:show_id>/', ShowSeatListView.as_view(), name="show-seats")
]