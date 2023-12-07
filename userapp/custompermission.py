from rest_framework.permissions import BasePermission,IsAuthenticated
from rest_framework.decorators import permission_classes



class OnlyUserPermission(BasePermission):
    def has_permission(self, request, view):
        current_user = request.user
        if current_user.is_shopowner:
            return False
        return True
    


class OnlyOwnerPermission(BasePermission):
    def has_permission(self, request, view):
        current_user = request.user
        if current_user.is_shopowner:
            return True
        return False