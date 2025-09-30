from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
################dev
def identificar_usuario_por_token_string(token_string):
    """
    Si tienes el token como string y necesitas obtener el usuario manualmente
    """
    try:
        # Buscar el token en la base de datos
        token_obj = Token.objects.get(key=token_string)
        
        # Obtener el usuario asociado
        user = token_obj.user

        return user
        
    except Token.DoesNotExist:
 
        return None
    
def obtener_usuario_de_request(request):
    authorization_header = request.headers.get('Authorization')

    if not authorization_header or not authorization_header.startswith('Bearer '):
        return None
        
        # Extraer el token
    token_string = authorization_header.split(' ')[1]
        
    # Identificar usuario manualmente
    user = identificar_usuario_por_token_string(token_string)
    return user

################Decoradores de autenticacion#######################################
from rest_framework.permissions import BasePermission

class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

# Usar en tu vista
@permission_classes([IsAuthenticated, IsAdminRole])
def mi_vista(request):
    # Solo usuarios con role='admin' pueden acceder
    pass

from rest_framework.permissions import BasePermission

class IsManagerGroup(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='managers').exists()

@permission_classes([IsManagerGroup])
def mi_vista(request):
    pass