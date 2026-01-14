# urls.py
from django.urls import path
from .views import BookTicketView

urlpatterns = [
    path('book/', BookTicketView.as_view(), name='book-ticket'),
]