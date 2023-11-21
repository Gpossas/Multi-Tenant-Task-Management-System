from rest_framework import serializers
from accounts.models import Team, Tenant
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer( serializers.ModelSerializer ):
    class Meta:
        model = User
        fields = ( 'id', 'username', 'password' )
    
        # Make sure that the password field is never sent back to the client.
        extra_kwargs = {
            'password': { 'write_only': True },
        }
    
    def create( self, validated_data ):
        return User.objects.create_user( **validated_data )
    
    def update( self, instance, validated_data ):
        updated = super().update( instance, validated_data )
    
        # We save again the user if the password was specified to make sure it's properly hashed.
        if 'password' in validated_data:
            updated.set_password( validated_data['password'] )
            updated.save()
        return updated



class TenantSerializer( serializers.ModelSerializer ):
    class Meta:
        model = Tenant
        fields = ( 'id', 'name' )


class TeamSerializer( serializers.ModelSerializer ):
    tenant = TenantSerializer()
    user = UserSerializer()

    class Meta:
        model = Team
        field = ( 'id', 'tenant', 'user' )


# class AccountSerializer( serializers.Serializer ):
#     team = TeamSerializer()
#     user = UserSerializer()
    
#     def create( self, validated_data ):
#         team_data = validated_data['team']
#         user_data = validated_data['user']

#         # Call our CompanyManager method to create the Team and the User
#         team, user = Team.objects.create_account(
#             team_name=team_data.get( 'name' ),
#             username=user_data.get( 'username' ),
#             password=user_data.get( 'password' ),
#         )

#         return { 'team': team, 'user': user }
    
#     def update( self, instance, validated_data ):
#         raise NotImplementedError( 'Cannot call update() on an account' )