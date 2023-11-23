from django.urls import path
from .views import CreateUser, CreateTenant, UserDetail

urlpatterns = [
    path( 'create_user', CreateUser.as_view(), name='create_user' ),
    path( 'user_detail/<str:username>', UserDetail.as_view(), name='user_detail' ),

    path( 'create_tenant', CreateTenant.as_view(), name='create_tenant' ),
]