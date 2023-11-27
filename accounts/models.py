import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class User( AbstractUser ):
    id = models.UUIDField( primary_key=True, default=uuid.uuid4, editable=False )

    class Meta:
        db_table = 'users'

    def __str__( self ):
        return self.username
    

class Team( models.Model ):
    id = models.UUIDField( primary_key=True, default=uuid.uuid4, editable=False )
    name = models.CharField( max_length=30 )
    members = models.ManyToManyField( User, related_name='teams' )
    created = models.DateTimeField( auto_now_add=True )

    class Meta:
        db_table = 'teams'

    def __str__( self ):
        return self.name