from django.shortcuts import render

from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import SignUpSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class SignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = SignUpSerializer
