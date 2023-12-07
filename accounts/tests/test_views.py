import json
from rest_framework import status
from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from accounts.models import Team
import unittest.mock as mock
from rest_framework.test import APIClient

User = get_user_model()

class UserDetailTestCase( TestCase ):
    def setUp( self ):
        self.user = APIClient()

        self.password = '123'
        self.luffy = User.objects.create_user( username='luffy', first_name='Monkey', last_name='D. Luffy', password=self.password )
        self.zoro = User.objects.create_user( username='zoro', first_name='Roronoa', last_name='Zoro', password=self.password )
        self.sanji = User.objects.create_user( username='sanji', password=self.password )
        self.ace = User.objects.create_user( username= 'ace', password=self.password )

        self.team = Team.objects.create_team( team_name='Straw Hat Pirates', captain=self.luffy )
        self.team.members.add( self.zoro )
        self.team.members.add( self.sanji )

    # ALL METHODS
    def test_unauthenticated_user_forbidden( self ):
        """Ensure all methods deny unauthenticated user access"""

        url = reverse( 'user_detail', args=['luffy'] )

        get_response = self.user.get( url )
        post_response = self.user.post( url )
        put_response = self.user.put( url )
        delete_response = self.user.delete( url )
        patch_response = self.user.patch( url )

        self.assertEqual( status.HTTP_403_FORBIDDEN, get_response.status_code )
        self.assertEqual( status.HTTP_403_FORBIDDEN, post_response.status_code )
        self.assertEqual( status.HTTP_403_FORBIDDEN, put_response.status_code )
        self.assertEqual( status.HTTP_403_FORBIDDEN, delete_response.status_code )
        self.assertEqual( status.HTTP_403_FORBIDDEN, patch_response.status_code )

    def test_not_a_team_member_access_forbidden( self ):
        """Ensure access denied for each method to users not in team"""
        
        not_member = APIClient()
        not_member.force_authenticate( user=self.ace )

        url = reverse( 'user_detail', args=['luffy'] )

        get_response = self.user.get( url )
        post_response = self.user.post( url )
        put_response = self.user.put( url )
        delete_response = self.user.delete( url )
        patch_response = self.user.patch( url )

        self.assertEqual( status.HTTP_403_FORBIDDEN, get_response.status_code )
        self.assertEqual( status.HTTP_403_FORBIDDEN, post_response.status_code )
        self.assertEqual( status.HTTP_403_FORBIDDEN, put_response.status_code )
        self.assertEqual( status.HTTP_403_FORBIDDEN, delete_response.status_code )
        self.assertEqual( status.HTTP_403_FORBIDDEN, patch_response.status_code )

    def test_nonexistent_user( self ):
        """Ensure status 404 if user doesn't exist"""

        url = reverse( 'user_detail', args=['not_a_user'] )
        self.user.force_authenticate( user=self.luffy )

        response = self.user.get( url )
        self.assertEqual( status.HTTP_404_NOT_FOUND, response.status_code )
    
    def test_user_signed_as_another_user( self ):
        """
        Ensure access denied to any user that is not the owner of account.
        Get response is allowed if they are in the same team.
        """

        url = reverse( 'user_detail', args=['zoro'] )
        self.user.force_authenticate( user=self.luffy )

        get_response = self.user.get( url )
        post_response = self.user.post( url )
        put_response = self.user.put( url )
        delete_response = self.user.delete( url )

        self.assertEqual( status.HTTP_200_OK, get_response.status_code )
        self.assertEqual( status.HTTP_403_FORBIDDEN, post_response.status_code )
        self.assertEqual( status.HTTP_403_FORBIDDEN, put_response.status_code )
        self.assertEqual( status.HTTP_403_FORBIDDEN, delete_response.status_code )

    # GET METHOD 
    def test_valid_get_user_detail( self ):
        """Test valid access to owner account detail"""

        owner = APIClient()
        owner.force_authenticate( user=self.luffy )
        url = reverse( 'user_detail', args=[self.luffy.username] )
        
        response = owner.get( url )
        self.assertEqual( status.HTTP_200_OK, response.status_code )

        response_data = response.json()
        response_data.pop( 'id' )
        self.assertEqual( response_data, {
            "username": "luffy",
            "first_name": "Monkey",
            "last_name": "D. Luffy"
        })
        self.assertNotIn( 'password', response.data )

    # PUT METHOD
    def test_valid_data_edit( self ):
        """Ensure owner data edit"""

        url = reverse( 'user_detail', args=['luffy'] )
        self.user.force_authenticate( user=self.luffy )

        response = self.user.put( url, data=json.dumps( { 'first_name': 'Monki' } ), content_type='application/json' )
        response_data = response.json()
        response_data.pop( 'id',  None )
        self.assertEqual( response_data, {
            "username": "luffy",
            "first_name": "Monki",
            "last_name": "D. Luffy"
        })

    def test_update_password_with_wrong_method( self ):
        url = reverse( 'user_detail', args=['luffy'] )
        self.user.force_authenticate( user=self.luffy )

        response = self.user.put( url, data=json.dumps( { 'password': 'not_allowed' } ), content_type='application/json' )
        self.assertEqual( status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code )
    
    def test_put_nonexistent_field( self ):
        """Non existent fields are ignored and don't return bad request"""

        url = reverse( 'user_detail', args=['luffy'] )
        self.user.force_authenticate( user=self.luffy )

        response = self.user.put( url, data=json.dumps( { 'none_field': 'not_allowed' } ), content_type='application/json' )
        self.assertEqual( status.HTTP_202_ACCEPTED, response.status_code )
    
    # POST METHOD
    def test_valid_password_redefinition( self ):
        """Ensure correct password redefinition"""

        url = reverse( 'user_detail', args=['luffy'] )
        self.user.force_authenticate( user=self.luffy )

        previous_password = self.luffy.password

        response = self.user.post( url, data=json.dumps( { 'password': '12345' } ), content_type='application/json' )
        self.assertEqual( status.HTTP_202_ACCEPTED, response.status_code )
        self.assertNotEqual( previous_password, User.objects.get( pk=self.luffy.pk ).password )

    def test_password_field_included( self ):
        """Ensure that the password field is passed through body"""

        url = reverse( 'user_detail', args=['luffy'] )
        self.user.force_authenticate( user=self.luffy )

        response = self.user.post( url, data={}, content_type='application/json' )
        self.assertEqual( status.HTTP_400_BAD_REQUEST, response.status_code )
    
    # DELETE METHOD
    def test_valid_user_delete( self ):
        url = reverse( 'user_detail', args=['luffy'] )
        self.user.force_authenticate( user=self.luffy )

        response = self.user.put( url )
        response_data = response.data
        response_data.pop( 'id',  None )
        self.assertEqual( status.HTTP_202_ACCEPTED, response.status_code )
        self.assertEqual( response_data, {
            "username": "luffy",
            "first_name": "Monkey",
            "last_name": "D. Luffy"
        })
    

class TeamListTest( TestCase ):
    def setUp( self ):
        self.client = Client()

        self.luffy = User.objects.create_user( username='luffy', first_name='Monkey', last_name='D. Luffy', password='123' )
        self.zoro = User.objects.create_user( username='zoro', first_name='Roronoa', last_name='Zoro', password='123' )
        self.sanji = User.objects.create_user( username='sanji', password='123' )
        self.team = Team.objects.create_team( team_name='Straw Hat Pirates', captain=self.luffy )
        self.team.members.add( self.zoro )
        self.team.members.add( self.sanji )

        self.whitebeard = User.objects.create_user( username='pops', first_name='Edward', last_name='Newgate', password='123' )
        self.ace = User.objects.create_user( username= 'ace', password='123' )
        self.marco = User.objects.create_user( username= 'marco', password='123' )
        self.team2 = Team.objects.create_team( team_name='Whitebeard Pirates', captain=self.whitebeard )
        self.team2.members.add( self.ace )
        self.team2.members.add( self.marco )
        
    def test_deny_user_unauthenticated( self ):
        url = reverse( 'workspace' )

        get_response = self.client.get( url )
        post_response = self.client.post( url )

        self.assertEqual( status.HTTP_401_UNAUTHORIZED, get_response.status_code )
        self.assertEqual( status.HTTP_401_UNAUTHORIZED, post_response.status_code )
    
    def test_valid_user_teams( self ):
        url = reverse( 'workspace' )

        response = self.client.get( url )

        self.assertEqual( response.data , 
            {
                "id": 1,
                "name": "Straw Hat Pirates",
                "members": [
                    {
                        "id": mock.ANY,
                        "username": "luffy",
                        "first_name": "Monkey",
                        "last_name": "D. Luffy"
                    },
                    {
                        "id": mock.ANY,
                        "username": "sanji"
                    },
                    {
                        "id": mock.ANY,
                        "username": "nami",
                        "first_name": "Senhorita",
                        "last_name": "Nami"
                    },
                    {
                        "id": mock.ANY,
                        "username": "zoro",
                        "first_name": "Roronoa",
                        "last_name": "Zoro"
                    }
                ],
                "created": mock.ANY
            }
        )