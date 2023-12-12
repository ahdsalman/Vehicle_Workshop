from rest_framework.permissions import BasePermission,IsAuthenticated
from rest_framework.decorators import permission_classes
from shopdetails.models import Workshopdetails



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
    



class OnlyShopPermission(BasePermission):
    def has_permission(self, request, view):
        current_user = request.user.id
        try:

            approved_shop = Workshopdetails.objects.get(shop_owner=current_user)
            if approved_shop.is_approved:
                return True
        except Workshopdetails.DoesNotExist:
            pass
        return False