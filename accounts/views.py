from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, TeamSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .permissions import IsInCommonTeam, IsUser, IsInTeam, IsReadOnly
from .models import Team

User = get_user_model()

# ========== USER VIEWS ==========

class CreateUser( APIView ):

    def post( self, request ):
        deserialized_user = UserSerializer( data=request.data )
        if deserialized_user.is_valid():
            deserialized_user.save()
            return Response( deserialized_user.data, status=status.HTTP_201_CREATED )
        return Response( deserialized_user.errors, status=status.HTTP_400_BAD_REQUEST )


class UserDetail( APIView ):
    # IsInCommonTeamOrIsUser will block unauthenticated users as IsAuthenticated.
    # To save computational resources by not hitting the database, it's preferable to block unauthenticated users earlier.
    permission_classes = ( IsAuthenticated, IsUser|( IsReadOnly&IsInCommonTeam ) )

    def get( self, request, username ):
        """Get user data"""

        user = get_object_or_404( User, username=username )
        self.check_object_permissions( request, user )

        serialized = UserSerializer( user )
        return Response( serialized.data, status=status.HTTP_200_OK )
    
    def put( self, request, username ):
        """Edit user information"""

        if 'password' in request.data:
            return Response( { 'error': 'password update should be under POST method' }, status=status.HTTP_405_METHOD_NOT_ALLOWED )
        
        user = get_object_or_404( User, username=username )
        self.check_object_permissions( request, user )

        user_serialized = UserSerializer( user, data=request.data, partial=True )
        if user_serialized.is_valid():
            user_serialized.save()
            return Response( user_serialized.data, status=status.HTTP_202_ACCEPTED )
        return Response( user_serialized.errors, status=status.HTTP_400_BAD_REQUEST )

    
    def post( self, request, username ):
        """Redefine user password"""

        user = get_object_or_404( User, username=username )
        self.check_object_permissions( request, user )

        deserialized_user = UserSerializer( user, data=request.data, partial=True )
        if deserialized_user.is_valid():
            deserialized_user.save()
            return Response( deserialized_user.data, status=status.HTTP_202_ACCEPTED )
        return Response( deserialized_user.errors, status=status.HTTP_400_BAD_REQUEST )

    def delete( self, request, username ):
        """Delete user"""

        user = get_object_or_404( User, username=username )
        self.check_object_permissions( request, user )

        serialized = UserSerializer( user )
        user.delete()
        return Response( serialized.data, status=status.HTTP_202_ACCEPTED )
    

class TeamList( APIView ):
    permission_classes = ( IsAuthenticated, )

    def get( self, request ):
        """Shows all the teams the user is on"""

        user_teams = request.user.teams.all()
        teams_serilized = TeamSerializer( user_teams, many=True )
        return Response( teams_serilized.data, status=status.HTTP_200_OK )


    def post( self, request ):
        """
        Create a team.
        Optional: populate team with members
        """

        members_to_add = [ get_object_or_404( User, username=member ) for member in request.data.get( 'members' ) ]  
        team_serialized = TeamSerializer( data=request.data, context={ 'captain': request.user, 'members': members_to_add } )

        if team_serialized.is_valid():
            team_serialized.save( members=members_to_add )
            return Response( team_serialized.data, status=status.HTTP_201_CREATED )
        return Response( team_serialized.errors, status=status.HTTP_400_BAD_REQUEST )


class TeamDetail( APIView ):
    permission_classes = ( IsAuthenticated, IsInTeam )
    
    def get( self, request, team_name ):
        """Get information about a team and its members"""

        team = get_object_or_404( Team, name=team_name )
        self.check_object_permissions( request, team )

        team_serialized = TeamSerializer( team )
        return Response( team_serialized.data, status=status.HTTP_200_OK )
    

    def post( self, request, team_name ):
        """Join a user to a team. Must be someone in the team to add users"""

        team = get_object_or_404( Team, name=team_name )
        self.check_object_permissions( request, team )
        new_member = get_object_or_404( User, username=request.data['username'] )

        team.members.add( new_member )
        serialized = TeamSerializer( team )
        return Response( serialized.data, status=status.HTTP_201_CREATED )
    

    def delete( self, request, team_name ):
        """Delete a team"""
        # TODO: user should be the captain to delete a team

        team = get_object_or_404( Team, name=team_name )
        self.check_object_permissions( request, team )
        team.delete()
        team_serialized = TeamSerializer( team )
        return Response( team_serialized.data, status=status.HTTP_202_ACCEPTED )