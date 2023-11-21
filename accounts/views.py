from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, TenantSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

User = get_user_model()


class CreateUser( APIView ):

    def post( self, request ):
        deserialized_user = UserSerializer( data=request.data )
        if deserialized_user.is_valid():
            deserialized_user.save()
            return Response( deserialized_user.data, status=status.HTTP_201_CREATED )
        return Response( deserialized_user.errors, status=status.HTTP_400_BAD_REQUEST )
    

class CreateTenant( APIView ):
    permission_classes = [IsAuthenticated]
    
    def post( self, request ):
        deserialized_tenant = TenantSerializer( data=request.data )
        if deserialized_tenant.is_valid():
            deserialized_tenant.save( owner=request.user )
            return Response( deserialized_tenant.data, status=status.HTTP_201_CREATED )
        return Response( deserialized_tenant.errors, status=status.HTTP_400_BAD_REQUEST )