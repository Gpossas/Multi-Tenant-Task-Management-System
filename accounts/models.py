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

class User( AbstractUser ):
    id = models.UUIDField( primary_key=True, default=uuid.uuid4, editable=False )

    class Meta:
        db_table = 'users'

    def __str__( self ):
        return self.username
    

class TenantManager( models.Manager ):
    """Creates a Tenant along with the Team"""

    @transaction.atomic
    def create_tenant( self, tenant_name: str, user: User ):
        tenant = Tenant.objects.create( name=tenant_name, owner=user )
        tenant.save()

        team = Team.objects.create( tenant=tenant, user=user )
        team.save()

        return tenant


class Tenant( models.Model ):
    id = models.UUIDField( primary_key=True, default=uuid.uuid4, editable=False )
    name = models.CharField( max_length=25, unique=True )
    owner = models.ForeignKey( User, related_name='tenants', on_delete=models.SET_NULL, null=True )

    objects = TenantManager()

    class Meta:
        db_table = 'tenants'

    def __str__( self ):
        return self.name


class Team( models.Model ):
    created = models.DateTimeField( auto_now_add=True )
    tenant = models.ForeignKey( Tenant, related_name='teams', on_delete=models.CASCADE )
    user = models.ForeignKey( User, related_name='teams', on_delete=models.SET_NULL, null=True )

    class Meta:
        db_table = 'teams'

    def __str__( self ):
        return self.tenant.name