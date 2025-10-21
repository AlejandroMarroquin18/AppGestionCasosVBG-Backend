# utils/permissions.py
from rest_framework.permissions import BasePermission

class RolPermission(BasePermission):
    """
    Permite acceso solo a usuarios con ciertos roles.
    Uso: asignar la lista de roles a la clase.
    """
    allowed_roles = ['developer','staff']  # Lista de roles permitidos por defecto

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user.rol in self.allowed_roles
