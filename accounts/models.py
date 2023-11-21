import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models, transaction

class TeamManager( models.Manager ):
    """Manager for the Team model. Also handles the account creation"""

    @transaction.atomic
    def create_account( self, team_name, username, password ):
        """Creates a Team along with the User(with staff permission) and returns them both"""

        team = Team( name=team_name )
        team.save()

        user = User.objects.create_user(
            username=username,
            password=password,
            team=team,
            is_staff=True,
        )

        return team, user


class Team( models.Model ):
    id = models.UUIDField( primary_key=True, default=uuid.uuid4, editable=False )
    name = models.CharField( 'name', max_length=100, unique=True )
    created = models.DateTimeField(auto_now_add=True)

    objects = TeamManager()

    class Meta:
        db_table = 'teams'

    def __str__( self ):
        return self.name
    

class Role:
    roles = [
        ( 'Administrator', 'administrator' ),
        ( 'Frontend', 'frontend' ),
        ( 'Backend', 'backend' ),
        ( 'Designer', 'designer' ),
        ( 'Trainee', 'trainee' ),
    ]

    @classmethod
    def add_role( cls, role ):
        return cls.roles.append( role )

class User( AbstractUser ):
    id = models.UUIDField( primary_key=True, default=uuid.uuid4, editable=False )
    team = models.ForeignKey( Team, related_name='users', on_delete=models.CASCADE, editable=False )

    class Meta:
        db_table = 'users'

    def __str__( self ):
        return f'{ self.username } | { self.team.name }'