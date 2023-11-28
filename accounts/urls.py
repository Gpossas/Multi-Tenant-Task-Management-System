from django.urls import path
from .views import CreateUser, TeamList, UserDetail, TeamDetail
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),

    path( 'create_user', CreateUser.as_view(), name='create_user' ),
    path( 'user_detail/<str:username>', UserDetail.as_view(), name='user_detail' ),

    path( 'workspace', TeamList.as_view(), name='workspace' ),
    
    path( 'team_detail/<str:team_name>', TeamDetail.as_view(), name='team_detail' ),
]