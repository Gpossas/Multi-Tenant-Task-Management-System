from django.urls import path
from .views import CreateUser, CreateTenant

urlpatterns = [
    path( '', CreateUser.as_view(), name='create_user' ),
    path( 'create_tenant', CreateTenant.as_view(), name='create_tenant' ),
]