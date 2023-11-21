from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import  AccountSerializer
from rest_framework.response import Response
from rest_framework import status

User = get_user_model()

class CreateAccount( APIView ):
    """ Create account and team"""

    def post( self, request ):
        account = AccountSerializer( data=request.data )
        if account.is_valid():
            account.save()
            return Response( account.data, status=status.HTTP_201_CREATED )
        return Response( account.errors, status=status.HTTP_400_BAD_REQUEST )