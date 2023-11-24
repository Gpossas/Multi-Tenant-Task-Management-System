from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, TenantSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .permissions import IsInCommonTeam, IsUser, IsInTeam
from .models import Tenant, Team

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
    permission_classes = ( IsAuthenticated, IsInCommonTeam|IsUser )

    def get( self, request, username ):
        """Get user data"""

        user = get_object_or_404( User, username=username )
        self.check_object_permissions( request, user )

        serialized = UserSerializer( user )
        return Response( serialized.data, status=status.HTTP_200_OK )
    
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
    
# ========== TENANTS VIEWS ==========

class CreateTenant( APIView ):
    permission_classes = [IsAuthenticated]
    
    def post( self, request ):
        deserialized_tenant = TenantSerializer( data=request.data )
        if deserialized_tenant.is_valid():
            deserialized_tenant.save( owner=request.user )
            return Response( deserialized_tenant.data, status=status.HTTP_201_CREATED )
        return Response( deserialized_tenant.errors, status=status.HTTP_400_BAD_REQUEST )
    

class TeamDetail( APIView ):
    permission_classes = ( IsAuthenticated, IsInTeam )
    
    #TODO: return tenant and new_member data in response
    def post( self, request, team_name ):
        """Join a user to a team. Must be someone in the team to add users"""

        tenant = get_object_or_404( Tenant, name=team_name )
        self.check_object_permissions( request, tenant )
        new_member = get_object_or_404( User, username=request.data['username'] )

        Team.objects.create( tenant=tenant, user=new_member )
        return Response( status=status.HTTP_201_CREATED )