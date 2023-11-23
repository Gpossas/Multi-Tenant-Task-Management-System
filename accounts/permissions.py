from rest_framework import permissions

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


class IsInCommonTeamOrIsUser( permissions.BasePermission ):
    def has_object_permission( self, request, view, obj ):
        if obj == request.user:
            return True
        
        my_teams = request.user.teams.all()
        requested_user_teams = obj.teams.all()

        return my_teams.filter( pk__in=requested_user_teams.values_list( 'pk', flat=True ) ).exists()