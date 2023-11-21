from django.test import TestCase, Client
from rest_framework import status
from django.urls import reverse

client = Client()

# Create your tests here.
class CreateAccountTest( TestCase ):
    def setUp( self ):
        self.json = {
            "user": {
                "username": "mirio",
                "password": "1000000"
            },
            
            "team": {
                "name": "Big Three"
            }
        }

    def test_create_valid_team_and_account( self ):
        pass