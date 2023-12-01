from rest_framework import serializers
from accounts.models import Team
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer( serializers.ModelSerializer ):
    class Meta:
        model = User
        fields = ( 'id', 'username', 'password', 'first_name', 'last_name', 'email' )
    
        # Make sure that the password field is never sent back to the client.
        extra_kwargs = {
            'password': { 'write_only': True },
        }
    
    def to_representation( self, instance ):
        representation = super().to_representation( instance )
        return { key: value for key, value in representation.items() if value }
    
    def create( self, validated_data ):
        return User.objects.create_user( **validated_data )
    
    def update( self, instance, validated_data ):
        updated = super().update( instance, validated_data )
    
        # We save again the user if the password was specified to make sure it's properly hashed.
        if 'password' in validated_data:
            updated.set_password( validated_data['password'] )
            updated.save()
        return updated  
        

class TeamSerializer( serializers.ModelSerializer ):
    members = UserSerializer( many=True, read_only=True )

    class Meta:
        model = Team
        fields = ( 'id', 'name', 'members', 'created' )

    def create( self, validated_data ):
        team = Team.objects.create_team( validated_data['name'], self.context['captain'] )
        team.slug = team.name.replace( ' ', '-' ).lower()
        team.save()

        if self.context.get( 'members' ):
            members = validated_data['members']
            for member in members:
                team.members.add( User.objects.get( username = member ) )
        
        return team
    
    def update( self, instance, validated_data ):
        new_members = validated_data['new_members']

        for new_member in new_members:
            instance.members.add( User.objects.get( username=new_member ) )