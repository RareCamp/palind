from rest_framework import permissions


class IsRequestTokenDatasetID(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        print(request.user)        
        return request.user == obj.dataset.api_token