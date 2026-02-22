# Third Party
from rest_framework import permissions


class HasGlomarPermission(permissions.BasePermission):
    """Require the glomar.view_glomar permission."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.has_perm("glomar.view_glomar")
        )
