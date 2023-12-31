import json
from rest_framework import status
from django.urls import reverse
from django.test import TestCase
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
    def test_unauthenticated_user_denied( self ):
        """Ensure all methods deny unauthenticated user access"""

        url = reverse( 'user_detail', args=['luffy'] )

        get_response = self.user.get( url )
        post_response = self.user.post( url )
        put_response = self.user.put( url )
        delete_response = self.user.delete( url )
        patch_response = self.user.patch( url )

        self.assertEqual( status.HTTP_401_UNAUTHORIZED, get_response.status_code )
        self.assertEqual( status.HTTP_401_UNAUTHORIZED, post_response.status_code )
        self.assertEqual( status.HTTP_401_UNAUTHORIZED, put_response.status_code )
        self.assertEqual( status.HTTP_401_UNAUTHORIZED, delete_response.status_code )
        self.assertEqual( status.HTTP_401_UNAUTHORIZED, patch_response.status_code )

    def test_not_a_team_member_access_forbidden( self ):
        """Ensure access denied for each method to users not in team"""
        
        self.user.force_authenticate( user=self.ace )

        url = reverse( 'user_detail', args=['luffy'] )

        get_response = self.user.get( url )
        post_response = self.user.post( url )
        put_response = self.user.put( url )
        delete_response = self.user.delete( url )

        self.assertEqual( status.HTTP_403_FORBIDDEN, get_response.status_code )
        self.assertEqual( status.HTTP_403_FORBIDDEN, post_response.status_code )
        self.assertEqual( status.HTTP_403_FORBIDDEN, put_response.status_code )
        self.assertEqual( status.HTTP_403_FORBIDDEN, delete_response.status_code )

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
    
        self.assertEqual( response.data, {
            "id": mock.ANY,
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

        response = self.user.put( url, data={ 'first_name': 'Monki' }, format='json' )
        self.assertEqual( response.data, {
            "id": mock.ANY,
            "username": "luffy",
            "first_name": "Monki",
            "last_name": "D. Luffy"
        })

    def test_update_password_with_wrong_method( self ):
        url = reverse( 'user_detail', args=['luffy'] )
        self.user.force_authenticate( user=self.luffy )

        response = self.user.put( url, data={ 'password': 'not_allowed' }, format='json' )
        self.assertEqual( status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code )
    
    def test_put_nonexistent_field( self ):
        """Non existent fields are ignored and don't return bad request"""

        url = reverse( 'user_detail', args=['luffy'] )
        self.user.force_authenticate( user=self.luffy )

        response = self.user.put( url, data={ 'none_field': 'not_allowed' } , format='json' )
        self.assertEqual( status.HTTP_202_ACCEPTED, response.status_code )
    
    # POST METHOD
    def test_valid_password_redefinition( self ):
        """Ensure correct password redefinition"""

        url = reverse( 'user_detail', args=['luffy'] )
        self.user.force_authenticate( user=self.luffy )

        previous_password = self.luffy.password

        response = self.user.post( url,data={ 'password': '12345' }, format='json' )
        self.assertEqual( status.HTTP_202_ACCEPTED, response.status_code )
        self.assertNotEqual( previous_password, User.objects.get( pk=self.luffy.pk ).password )

    def test_password_field_included( self ):
        """Ensure that the password field is passed through body"""

        url = reverse( 'user_detail', args=['luffy'] )
        self.user.force_authenticate( user=self.luffy )

        response = self.user.post( url, data={}, format='json' )
        self.assertEqual( status.HTTP_400_BAD_REQUEST, response.status_code )
    
    # DELETE METHOD
    def test_valid_user_delete( self ):
        url = reverse( 'user_detail', args=['luffy'] )
        self.user.force_authenticate( user=self.luffy )

        response = self.user.put( url )
        self.assertEqual( status.HTTP_202_ACCEPTED, response.status_code )
        self.assertEqual( response.data, {
            "id": mock.ANY,
            "username": "luffy",
            "first_name": "Monkey",
            "last_name": "D. Luffy"
        })
    

class TeamListTest( TestCase ):
    def setUp( self ):
        self.user = APIClient()

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

        get_response = self.user.get( url )
        post_response = self.user.post( url )

        self.assertEqual( status.HTTP_401_UNAUTHORIZED, get_response.status_code )
        self.assertEqual( status.HTTP_401_UNAUTHORIZED, post_response.status_code )
    
    def test_valid_user_teams( self ):
        url = reverse( 'workspace' )

        self.user.force_authenticate( user=self.luffy )
        response = self.user.get( url )
        self.assertEqual( response.data, 
            [
                {
                    'id': 1, 
                    'name': 'Straw Hat Pirates', 
                    'members': [
                        {
                            'id': mock.ANY, 
                            'username': 'luffy', 
                            'first_name': 'Monkey', 
                            'last_name': 'D. Luffy'
                        }, 
                        {
                            'id': mock.ANY, 
                            'username': 'zoro', 
                            'first_name': 'Roronoa', 
                            'last_name': 'Zoro'
                        }, 
                        {
                            'id': mock.ANY, 
                            'username': 'sanji'
                        }
                    ], 
                    'created': mock.ANY
                }
            ]
        )
    
    # POST METHOD
    def test_team_name_required( self ):
        url = reverse( 'workspace' )
        self.user.force_authenticate( user=self.ace )

        response = self.user.post( url, data={}, format='json' )
        self.assertEqual( status.HTTP_400_BAD_REQUEST, response.status_code )


class TeamDetailTest( TestCase ):
    def setUp( self ):
        self.url = reverse( 'team_detail',  args=( '1', 'straw-hat-pirates' ) )
        self.user = APIClient()
        self.luffy = User.objects.create_user( username='luffy', first_name='Monkey', last_name='D. Luffy', password='123' )
        self.zoro = User.objects.create_user( username='zoro', first_name='Roronoa', last_name='Zoro', password='123' )
        self.sanji = User.objects.create_user( username='sanji', password='123' )
        self.team = Team.objects.create_team( team_name='Straw Hat Pirates', captain=self.luffy )
        self.team.members.add( self.zoro )
        self.team.members.add( self.sanji )

        self.blackbeard = User.objects.create_user( username='blackbeard', first_name='Marshall', last_name='D. Teach', password='123' )
        
    def test_access_denied_unauthenticated_user( self ):
        get_response = self.user.get( self.url )
        post_response = self.user.post( self.url )
        patch_response = self.user.patch( self.url )
        delete_response = self.user.delete( self.url )
        self.assertEqual( status.HTTP_401_UNAUTHORIZED, get_response.status_code )
        self.assertEqual( status.HTTP_401_UNAUTHORIZED, post_response.status_code )
        self.assertEqual( status.HTTP_401_UNAUTHORIZED, patch_response.status_code )
        self.assertEqual( status.HTTP_401_UNAUTHORIZED, delete_response.status_code )
    
    def test_access_denied_user_not_in_team( self ):
        """Ensure access denied for a user that is not from the team to get team data"""

        self.user.force_authenticate( user=self.blackbeard )
        
        get_response = self.user.get( self.url )
        post_response = self.user.post( self.url )
        delete_response = self.user.delete( self.url )
        patch_response = self.user.patch( self.url )
        self.assertEqual( status.HTTP_403_FORBIDDEN, get_response.status_code )
        self.assertEqual( status.HTTP_403_FORBIDDEN, post_response.status_code )
        self.assertEqual( status.HTTP_403_FORBIDDEN, delete_response.status_code )
        self.assertEqual( status.HTTP_403_FORBIDDEN, patch_response.status_code )
    
    def test_nonexistent_team( self ):
        self.user.force_authenticate( user=self.luffy )
        url = reverse( 'team_detail',  args=( '99', 'straw-hat-pirates' ) )
        get_response = self.user.get( url )
        post_response = self.user.post( url )
        delete_response = self.user.delete( url )
        patch_response = self.user.patch( url )
        self.assertEqual( status.HTTP_404_NOT_FOUND, get_response.status_code )
        self.assertEqual( status.HTTP_404_NOT_FOUND, post_response.status_code )
        self.assertEqual( status.HTTP_404_NOT_FOUND, delete_response.status_code )
        self.assertEqual( status.HTTP_404_NOT_FOUND, patch_response.status_code )
    
    # POST METHOD
    def test_access_denied_add_member( self ):
        # authenticated, but not a member of team
        self.user.force_authenticate( user=self.blackbeard )
        response = self.user.post( self.url )
        self.assertEqual( status.HTTP_403_FORBIDDEN, response.status_code )

        # member of team, but without permission
        self.user.force_authenticate( user=self.sanji )
        response = self.user.post( self.url )
        self.assertEqual( status.HTTP_403_FORBIDDEN, response.status_code )
    
    def test_access_denied_wrong_json( self ):
        self.user.force_authenticate( user=self.luffy )
        response = self.user.post( self.url, data={} )
        self.assertEqual( status.HTTP_400_BAD_REQUEST, response.status_code )
    
    # DELETE METHOD
    def test_access_denied_not_captain_delete_team( self ):
        self.user.force_authenticate( user=self.zoro )
        response = self.user.delete( self.url )
        self.assertEqual( status.HTTP_403_FORBIDDEN, response.status_code )
    
    # PATH METHOD
    def test_valid_member_remove( self ):
        # captain remove member
        self.user.force_authenticate( user=self.luffy )
        response = self.user.patch( self.url, data={ 'username': 'zoro' } )
        self.assertEqual( status.HTTP_202_ACCEPTED, response.status_code )
        self.assertNotIn( self.zoro, self.team.members.all() )

        # member leave team
        self.user.force_authenticate( user=self.sanji )
        response = self.user.patch( self.url, data={ 'username': 'sanji' } )
        self.assertEqual( status.HTTP_202_ACCEPTED, response.status_code )
        self.assertNotIn( self.sanji, self.team.members.all() )
    
    def test_denied_permission_remove_member( self ):
        self.user.force_authenticate( user=self.zoro )
        response = self.user.patch( self.url, data={ 'username': 'sanji' } )
        self.assertEqual( status.HTTP_403_FORBIDDEN, response.status_code )
        self.assertIn( self.sanji, self.team.members.all() )