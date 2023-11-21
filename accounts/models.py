import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models, transaction

# TODO: Model to be added
# class Role:
#     roles = [
#         ( 'Administrator', 'administrator' ),
#         ( 'Frontend', 'frontend' ),
#         ( 'Backend', 'backend' ),
#         ( 'Designer', 'designer' ),
#         ( 'Trainee', 'trainee' ),
#     ]

#     @classmethod
#     def add_role( cls, role ):
#         return cls.roles.append( role )


class Tenant( models.Model ):
    id = models.UUIDField( primary_key=True, default=uuid.uuid4, editable=False )
    name = models.CharField( max_length=25, unique=True )

    class Meta:
        db_table = 'tenants'

    def __str__( self ):
        return self.name


class User( AbstractUser ):
    id = models.UUIDField( primary_key=True, default=uuid.uuid4, editable=False )

    class Meta:
        db_table = 'users'

    def __str__( self ):
        return self.username


class Team( models.Model ):
    created = models.DateTimeField( auto_now_add=True )
    tenant = models.ForeignKey( Tenant, related_name='team', on_delete=models.CASCADE )
    user = models.ForeignKey( User, related_name='team', on_delete=models.CASCADE )

    class Meta:
        db_table = 'teams'

    def __str__( self ):
        return self.tenant.name