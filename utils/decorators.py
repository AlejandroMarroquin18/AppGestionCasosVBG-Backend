from functools import wraps
from rest_framework.response import Response
from rest_framework import status

def rol_required(*roles_permitidos):
    """
    Decorador para verificar que el usuario tenga uno de los roles permitidos.
    Uso: @rol_required('admin', 'moderador')
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            '''if not user.is_authenticated:
                return Response({"detail": "No autenticado"}, status=status.HTTP_401_UNAUTHORIZED)'''
            print("Usuario rol:", user.rol)
            if user.rol not in roles_permitidos:
                return Response({"detail": "No tienes permisos para acceder a este recurso"}, 
                                status=status.HTTP_403_FORBIDDEN)

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
