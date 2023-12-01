import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db import transaction

class TeamManager( models.Manager ):

    @transaction.atomic
    def create_team( self, team_name, captain ):
        team = Team.objects.create( name=team_name )
        TeamMembership.objects.create( team=team, member=captain, role=TeamMembership.Roles.CAPTAIN )
        return team       


class User( AbstractUser ):
    id = models.UUIDField( primary_key=True, default=uuid.uuid4, editable=False )

    class Meta:
        db_table = 'users'

    def __str__( self ):
        return self.username
    

class Team( models.Model ):
    name = models.CharField( max_length=30 )
    slug = models.SlugField()
    members = models.ManyToManyField( User, related_name='teams', through='TeamMembership' )
    created = models.DateTimeField( auto_now_add=True )

    objects = TeamManager()

    class Meta:
        db_table = 'teams'

    def __str__( self ):
        return self.name
    

class TeamMembership( models.Model ):
    class Roles( models.TextChoices ):
        CAPTAIN = 'C', 'Captain'
        FIRST_MATE = 'FM', 'First mate'
        MEMBER = 'M', 'Member'
        
    team = models.ForeignKey( Team, on_delete=models.CASCADE )
    member = models.ForeignKey( User, on_delete=models.CASCADE )
    role = models.CharField(
        max_length=2,
        choices=Roles.choices,
        default=Roles.MEMBER
    )

    class Meta:
        db_table = 'teams_membership' 