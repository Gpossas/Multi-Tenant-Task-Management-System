from django.urls import path
from .views import CreateUser, TeamList, UserDetail, TeamDetail

urlpatterns = [
    path( 'create_user', CreateUser.as_view(), name='create_user' ),
    path( 'user_detail/<str:username>', UserDetail.as_view(), name='user_detail' ),

    path( 'workspace', TeamList.as_view(), name='workspace' ),
    
    path( 'team_detail/<str:team_name>', TeamDetail.as_view(), name='team_detail' ),
]