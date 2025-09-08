# apps/users/urls.py
from django.urls import path
from apps.users.views.auth import MyTokenView

urlpatterns = [
    path('token/', MyTokenView.as_view(), name='token_obtain_pair'),
]

