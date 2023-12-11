from rest_framework import permissions
from .models import TeamMembership

class IsOwnerOrReadOnly( permissions.BasePermission ):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.owner == request.user
    

class IsUserOrReadOnly( permissions.BasePermission ):
    def has_object_permission(self, request, view, instance_user):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return instance_user == request.user


class IsReadOnly( permissions.BasePermission ):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsUser( permissions.BasePermission ):
    message = 'Must be the owner of the account to perform action'
    def has_object_permission( self, request, view, obj ):
        return bool( obj == request.user )


class IsInCommonTeam( permissions.BasePermission ):
    message = 'Must be in a common team to perform action'
    def has_object_permission( self, request, view, obj ): 
        my_teams = request.user.teams.all()
        requested_user_teams = obj.teams.all()

        return bool( my_teams.filter( pk__in=requested_user_teams.values_list( 'pk', flat=True ) ).exists() )
    

class IsInTeam( permissions.BasePermission ):
    message = 'Must be in team to perform action'
    def has_object_permission( self, request, view, team ): 
        return bool( request.user.teams.filter( name=team ).exists() )
    

class IsCaptain( permissions.BasePermission ):
    message = 'Must be captain to perform action'
    def has_object_permission( self, request, view, team ): 
        return bool( TeamMembership.objects.filter( team=team.id, member=request.user.id, role='C' ).exists() )


class IsFirstMate( permissions.BasePermission ):
    message = 'Must be First mate to perform action'
    def has_object_permission( self, request, view, team ): 
        return bool( TeamMembership.objects.filter( team=team.id, member=request.user.id, role='FM' ).exists() )

class IsInTeamAndIsUserOrIsCaptainOrIsFirstMate( permissions.BasePermission ):
    message = 'must be captain or first mate to remove a member or be the member itself'
    def has_object_permission( self, request, view, user ): 
        team_pk = view.kwargs.get( 'pk' )
        if not request.user.teams.filter( pk=team_pk ).exists():
            self.message = 'must be in team to perform action'
            return False
        return bool( 
            request.user == user 
            or TeamMembership.objects.filter( team=team_pk, member=request.user.id, role__in=('C', 'FM') ).exists()
        )