from django.shortcuts import render
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# Create your views here.


@csrf_exempt  # Exime de la verificación de CSRF (para pruebas, no en producción)
def login_view(request):
    if request.method == "POST":
        try:
            # Parsear el JSON recibido
            data = json.loads(request.body)
            requestemail = data.get("email")
            requestpassword = data.get("password")
            
            # Autenticar al usuario
            user = authenticate(request, username=requestemail, password=requestpassword)
            
            if user is not None:
                # El usuario es válido
                return JsonResponse({"status": "success", "message": "Usuario autenticado correctamente"})
            else:
                # Usuario o contraseña incorrectos
                return JsonResponse({"status": "error", "message": "Credenciales incorrectas"}, status=401)
        
        except json.JSONDecodeError:
            # Error en el JSON recibido
            return JsonResponse({"status": "error", "message": "JSON inválido"}, status=400)

    return JsonResponse({"status": "error", "message": "Método no permitido"}, status=405)


@csrf_exempt  # Solo usar para desarrollo; considera seguridad para producción
def registro_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")
            password = data.get("password")

            # Verificar que todos los campos estén presentes
            if  not email or not password:
                return JsonResponse({"error": "Faltan campos requeridos"}, status=400)

            

            user = User.objects.create(
                username=username,
                email=email,
                password=make_password(password)  # Hashea la contraseña
            )

            return JsonResponse({"message": "Usuario creado exitosamente"}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido"}, status=400)
    else:
        return JsonResponse({"error": "Método no permitido"}, status=405)