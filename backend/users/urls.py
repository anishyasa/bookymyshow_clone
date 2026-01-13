from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import SignUpView

urlpatterns = [
    # API: /users/signup/
    path('signup/', SignUpView.as_view(), name='signup'),
    
    # API: /users/login/ -> Returns {"access": "...", "refresh": "..."}
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # API: /users/token/refresh/ -> Returns new access token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]