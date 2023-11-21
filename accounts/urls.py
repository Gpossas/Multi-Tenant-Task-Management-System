from django.urls import path
from .views import CreateAccount

urlpatterns = [
    path( '', CreateAccount.as_view(), name='create_account' ),
]