from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, TeamSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .permissions import IsInCommonTeam, IsUser, IsInTeam, IsReadOnly, IsCaptain, IsFirstMate
from .models import Team, TeamMembership
from rest_framework_simplejwt.authentication import JWTAuthentication

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
    authentication_classes = ( JWTAuthentication, )
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

        if 'password' not in request.data:
            return Response( { 'error': 'password field required' }, status=status.HTTP_400_BAD_REQUEST )

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
    

# ========== TEAM VIEWS ==========


class TeamList( APIView ):
    authentication_classes = ( JWTAuthentication, )
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

        members_to_add = [ get_object_or_404( User, username=member ) for member in request.data.get( 'members', [] ) ]  
        team_serialized = TeamSerializer( data=request.data, context={ 'captain': request.user, 'members': members_to_add } )

        if team_serialized.is_valid():
            team_serialized.save( members=members_to_add )
            return Response( team_serialized.data, status=status.HTTP_201_CREATED )
        return Response( team_serialized.errors, status=status.HTTP_400_BAD_REQUEST )


class TeamDetail( APIView ):
    authentication_classes = ( JWTAuthentication, )
    
    def get_permissions( self ):
        if self.request.method == 'POST':
            self.permission_classes = ( IsAuthenticated, IsInTeam, IsCaptain|IsFirstMate )
        elif self.request.method == 'PATCH':
            self.permission_classes = ( IsAuthenticated, IsInTeam )
        elif self.request.method == 'DELETE':
            self.permission_classes = ( IsAuthenticated, IsInTeam, IsCaptain )
        else:
            self.permission_classes = ( IsAuthenticated, IsInTeam )
        return super( TeamDetail, self ).get_permissions()
    
    
    def get( self, request, pk, slug ):
        """Get information about a team and its members"""

        team = get_object_or_404( Team, pk=pk )
        self.check_object_permissions( request, team )

        team_serialized = TeamSerializer( team )
        return Response( team_serialized.data, status=status.HTTP_200_OK )
    

    def post( self, request, pk, slug ):
        """Add a member to the team ( must be captain or first mate )"""

        team = get_object_or_404( Team, pk=pk )
        self.check_object_permissions( request, team )
        new_member = get_object_or_404( User, username=request.data['username'] )

        team.members.add( new_member )
        serialized = TeamSerializer( team )
        return Response( serialized.data, status=status.HTTP_201_CREATED )
    

    def patch( self, request, pk, slug ):
        """Remove a member or leave a team"""

        member_to_remove = get_object_or_404( User, username=request.data.get( 'username' ) )
        team = get_object_or_404( Team, pk=pk )
        if (
            request.user == member_to_remove or
            TeamMembership.objects.filter( team=team.id, member=request.user.id, role__in=('C', 'FM') ).exists()
        ):
            serialized_member_to_remove = UserSerializer( member_to_remove )
            team.members.remove( member_to_remove )
            return Response( serialized_member_to_remove.data, status=status.HTTP_202_ACCEPTED )
        return Response( 
            { 'error': 'must be captain or first mate to remove a member or be the member itself' },
            status=status.HTTP_403_FORBIDDEN 
        )
    

    def delete( self, request, pk, slug ):
        """Delete a team"""

        team = get_object_or_404( Team, pk=pk )
        self.check_object_permissions( request, team )
        team_serialized_data = TeamSerializer( team ).data
        team.delete()
        return Response( team_serialized_data, status=status.HTTP_202_ACCEPTED )