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
    owner = UserSerializer( read_only=True )

    class Meta:
        model = Tenant
        fields = ( 'id', 'name', 'owner' )

    def create( self, validated_data ):
        tenant_name: str = validated_data['name']
        owner: User = validated_data['owner']

        tenant = Tenant.objects.create_tenant(
            tenant_name = tenant_name, 
            user = owner
        )

        return tenant
    
    # TODO: update name of tenant maintaining data integrity
    def update( self, instance, validated_data ):
        new_name = Tenant.objects.filter( name=validated_data['name'] ) 
        if new_name:
            raise Tenant.FieldError( 'Name already in use' )
        instance.name = validated_data['name']
        return instance
        

class TeamSerializer( serializers.ModelSerializer ):
    tenant = TenantSerializer()
    user = UserSerializer()

    class Meta:
        model = Team
        fields = ( 'id', 'tenant', 'user', 'created' )