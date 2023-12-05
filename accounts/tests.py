from rest_framework import status
from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import Team

User = get_user_model()

class UserDetailTestCase( TestCase ):
    def setUp( self ):
        self.client = Client()
        self.user = User.objects.create( username='luffy', first_name='Monkey', last_name='D. Luffy', password='123' )
        self.user2 = User.objects.create( username='zoro', first_name='Roronoa', last_name='Zoro', password='123' )
        self.user3 = User.objects.create( username= 'ace', password='123' )
        self.team = Team.objects.create_team( team_name='Straw Hat Pirates', captain=self.user )
        self.team.members.add( self.user2 )


    def test_unauthenticated_user_forbidden( self ):
        """Ensure all methods deny unauthenticated user access"""

        url = reverse( 'user_detail', args=['luffy'] )

        get_response = self.client.get( url )
        post_response = self.client.post( url )
        put_response = self.client.put( url )
        delete_response = self.client.delete( url )
        patch_response = self.client.patch( url )

        self.assertEqual( status.HTTP_403_FORBIDDEN, get_response.status_code )
        self.assertEqual( status.HTTP_403_FORBIDDEN, post_response.status_code )
        self.assertEqual( status.HTTP_403_FORBIDDEN, put_response.status_code )
        self.assertEqual( status.HTTP_403_FORBIDDEN, delete_response.status_code )
        self.assertEqual( status.HTTP_403_FORBIDDEN, patch_response.status_code )

    def test_not_a_team_member_access_forbidden( self ):
        """Ensure access denied for each method to users not in team"""
        
        not_member = Client()
        not_member.force_login( self.user3 )

        url = reverse( 'user_detail', args=['luffy'] )

        get_response = self.client.get( url )
        post_response = self.client.post( url )
        put_response = self.client.put( url )
        delete_response = self.client.delete( url )
        patch_response = self.client.patch( url )

        self.assertEqual( status.HTTP_403_FORBIDDEN, get_response.status_code )
        self.assertEqual( status.HTTP_403_FORBIDDEN, post_response.status_code )
        self.assertEqual( status.HTTP_403_FORBIDDEN, put_response.status_code )
        self.assertEqual( status.HTTP_403_FORBIDDEN, delete_response.status_code )
        self.assertEqual( status.HTTP_403_FORBIDDEN, patch_response.status_code )

    def test_nonexistent_user( self ):
        """Ensure status 404 if user doesn't exist"""

        url = reverse( 'user_detail', args=['not_a_user'] )
        self.client.force_login( self.user )

        response = self.client.get( url )
        self.assertEqual( status.HTTP_404_NOT_FOUND, response.status_code )

    # GET METHOD 
    def test_valid_get_user_detail( self ):
        """Test valid access to owner account detail"""

        owner = Client()
        owner.force_login( self.user )
        url = reverse( 'user_detail', args=[self.user.username] )
        get_response = owner.get( url )
        self.assertEqual( status.HTTP_200_OK, get_response.status_code )

    def test_user_signed_as_another_user( self ):
        """Ensure access denied to any user that is not the owner of account"""

        url = reverse( 'user_detail', args=['zoro'] )
        self.client.force_login( self.user )

        get_response = self.client.get( url )
        post_response = self.client.post( url )
        put_response = self.client.put( url )
        delete_response = self.client.delete( url )

        #Exception: they are on the same team
        self.assertEqual( status.HTTP_200_OK, get_response.status_code )
        self.assertEqual( status.HTTP_403_FORBIDDEN, post_response.status_code )
        self.assertEqual( status.HTTP_403_FORBIDDEN, put_response.status_code )
        self.assertEqual( status.HTTP_403_FORBIDDEN, delete_response.status_code )

    # PUT METHOD
    def test_valid_data_edit( self ):
        pass
    def test_edit_another_user_data( self ):
        pass # forbidden
    def test_update_password_with_wrong_method( self ):
        pass # forbidden