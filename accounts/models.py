import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db import transaction

class User( AbstractUser ):
    id = models.UUIDField( primary_key=True, default=uuid.uuid4, editable=False )

    class Meta:
        db_table = 'users'

    def __str__( self ):
        return self.username
    

class TeamManager( models.Manager ):

    @transaction.atomic
    def create_team( self, team_name, captain ):
        team = Team.objects.create( name=team_name )
        team.save()
        team.members.add( captain )
        return team


class Team( models.Model ):
    id = models.UUIDField( primary_key=True, default=uuid.uuid4, editable=False )
    name = models.CharField( max_length=30 )
    members = models.ManyToManyField( User, related_name='teams' )
    created = models.DateTimeField( auto_now_add=True )

    objects = TeamManager()

    class Meta:
        db_table = 'teams'

    def __str__( self ):
        return self.name