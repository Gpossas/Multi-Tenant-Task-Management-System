from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, TenantSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from .permissions import IsUserOrReadOnly

User = get_user_model()


class CreateUser( APIView ):

    def post( self, request ):
        deserialized_user = UserSerializer( data=request.data )
        if deserialized_user.is_valid():
            deserialized_user.save()
            return Response( deserialized_user.data, status=status.HTTP_201_CREATED )
        return Response( deserialized_user.errors, status=status.HTTP_400_BAD_REQUEST )


class UserDetail( APIView ):
    # IsAuthenticatedOrReadOnly and IsUserOrReadOnly block the same thing,
    # but if IsAuthenticatedOrReadOnly is removed, an unauthenticated user will make a request
    # to the database before being blocked. 
    # To save computational resources, it's preferable to block unauthorized users sooner.
    permission_classes = ( IsAuthenticatedOrReadOnly, IsUserOrReadOnly )

    def get( self, request, username ):
        """Get user data"""

        user = get_object_or_404( User, username=username )
        requested_user_teams = user.team.all()

        my_teams = request.user.team.all()

        if my_teams.filter( pk__in=requested_user_teams.values( 'pk' ).exists() ):
            serialized = UserSerializer( user )
            return Response( serialized.data, status=status.HTTP_200_OK )
        return Response( status=status.HTTP_403_FORBIDDEN )
    
    def post( self, request, username ):
        """Redefine user password"""

        user = get_object_or_404( User, username=username )
        self.check_object_permissions( request, user )

        deserialized_user = UserSerializer( user, data=request.data, partial=True )
        print( deserialized_user.initial_data )
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
    

class CreateTenant( APIView ):
    permission_classes = [IsAuthenticated]
    
    def post( self, request ):
        deserialized_tenant = TenantSerializer( data=request.data )
        if deserialized_tenant.is_valid():
            deserialized_tenant.save( owner=request.user )
            return Response( deserialized_tenant.data, status=status.HTTP_201_CREATED )
        return Response( deserialized_tenant.errors, status=status.HTTP_400_BAD_REQUEST )