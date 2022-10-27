from django.urls import path
from users.views import UserView


urlpatterns = [
    path('users/', UserView.as_view()),
]
