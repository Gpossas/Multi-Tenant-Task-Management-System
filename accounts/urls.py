from django.urls import path
from .views import CreateUser

urlpatterns = [
    path( '', CreateUser.as_view(), name='create_user' ),
]