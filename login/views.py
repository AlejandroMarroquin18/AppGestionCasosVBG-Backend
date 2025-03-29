from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .serializers import UserSerializer
import requests as req 
import requests
from .models import Usuarios, Restore_Password_Token
from rest_framework.authtoken.models import Token
from rest_framework import status, viewsets
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from google.auth.transport import requests
from google.oauth2 import id_token
import os
from django.http import JsonResponse
import json
from django.middleware.csrf import get_token
from django.contrib.auth import login, logout
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt



@api_view(['POST'])
def login_view(request):
    
    user=get_object_or_404(Usuarios,email=request.data['email'])
    valid= user.check_password(request.data['password'])
    if not valid:
        return Response({"error": "Invalid Password"}, status=status.HTTP_401_UNAUTHORIZED)
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(instance=user)
    
    return Response({"token":token.key,"user": serializer.data},status.HTTP_200_OK)

@api_view(['POST'])
def register_view(request):
    
    serializer=UserSerializer(data=request.data)

    if not request.data.get['password']:
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    if serializer.is_valid():
        serializer.save()
        user = Usuarios.objects.get(email=serializer.data['email'])
        user.set_password(request.data['password'])
        user.save()
        token = Token.objects.create(user=user)
        return Response({'token':token.key, "user": serializer.data}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
def forgottenPassword_view(request):
    
    emailrequest=request.data.get('email')
    
    if not emailrequest:
        return Response({"message":"No se ha proporcionado ningún correo electronico"}, status=status.HTTP_400_BAD_REQUEST)
    if (not Usuarios.objects.filter(email=emailrequest).exists()):
        
        return Response({"message":"La cuenta no existe o no se encontró"},status=status.HTTP_404_NOT_FOUND)
    if(Restore_Password_Token.objects.filter(email=emailrequest).exists()):
        tokenexistente=get_object_or_404(Restore_Password_Token,email=request.data.get('email'))
        tokenexistente.delete()
        

    ##Generar un Token que se vence despues de un tiempo (10 minutos)
    codigoRegistro=Restore_Password_Token.objects.create(email=emailrequest)
    codigo=codigoRegistro.codigo
    
    #serializer=RestorePasswordTokenSerializer(codigo)
    ##Enviar este token por correo
    asunto = 'Recuperacion de contraseña'
    mensaje = f'Este es tu codigo de recuperacion de contraseña: {codigo}'
    destinatario = [emailrequest]
    remitente = 'dawntest90@gmail.com'
    
    try:
        send_mail(asunto, mensaje,remitente,destinatario)
        #Se envío el correo, blablabla
        
        return Response({'message': 'codigo enviado al correo'},status=status.HTTP_200_OK)
    except Exception as e:
        print("no se pudo enviar el correo")
        return Response({'status':'error','message': f'Error al enviar el correo electronico {e}'},status=status.HTTP_408_REQUEST_TIMEOUT)

    
@api_view(['POST'])
def confirmForgottenPasswordCode_view(request):
    ##Que se ingrese este codigo y verifique si fue generado por este correo y
    
    coderequest=request.data.get('codigo')
    ses=get_object_or_404(Restore_Password_Token,email=request.data.get('email'))
    #se lo hace saber al frontend
    if ses.codigo==coderequest:
        return Response({'status':'success','message':'token correcto'},status=status.HTTP_200_OK)
    else:
        return Response( { 'status':'error','message':'Codigo Incorrecto'},status=status.HTTP_401_UNAUTHORIZED)

    
@api_view(['POST'])
def changeForgottenPassword_view(request):
    #Recibe la solicitud de cambio de contraseña
    print(request.data)
    newPassword= request.data.get('password')
    codigorequest= request.data.get('codigo')
    
    user=get_object_or_404(Usuarios,email=request.data['email'])
    
    token=get_object_or_404(Restore_Password_Token,email=request.data.get('email'))
    
    if (codigorequest==token.codigo):
        
        #Cambia la contraseña de la BD
        user.set_password(newPassword)
        user.save()
        #Borra el token generado
        token.delete()
        return Response({'status':'success', 'message':'Password cambiada correctamente'}, status=status.HTTP_200_OK)
    else:
        return Response({'status':'error','message':'El token no concuerda con el generado'},status=status.HTTP_401_UNAUTHORIZED)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

@api_view(['POST'])
def googleAuth(request):
    auth_code = request.data.get('code')  #  Recibir "code" en lugar de "access_token"

    if not auth_code:
        return Response({"error": "No se recibió el código de autorización."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # 🔥 Intercambiar el código por tokens en Google
        google_token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "code": auth_code,  # 🔥 Ahora usamos "code", no "access_token"
            "grant_type": "authorization_code",
            "redirect_uri": "http://localhost:3000",  # Asegúrate de que coincide con Google Console
        }
        token_response = req.post(google_token_url, data=token_data)

        if token_response.status_code != 200:
            return Response({"error": "Error al obtener tokens de Google.", "details": token_response.json()}, status=status.HTTP_400_BAD_REQUEST)

        token_json = token_response.json()
        access_token = token_json.get("access_token")
        refresh_token = token_json.get("refresh_token")  # 🔥 Ahora obtenemos el refresh_token

        if not access_token:
            return Response({"error": "No se recibió el access_token."}, status=status.HTTP_400_BAD_REQUEST)

        #  Obtener información del usuario
        google_user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        google_response = req.get(google_user_info_url, headers=headers)

        if google_response.status_code != 200:
            return Response({"error": "No se pudo verificar el usuario con Google."}, status=status.HTTP_400_BAD_REQUEST)

        user_data = google_response.json()
        email = user_data.get('email')
        name = user_data.get('name')

        if not email:
            return Response({"error": "No se pudo obtener el correo electrónico."}, status=status.HTTP_400_BAD_REQUEST)

        #  Guardar usuario en la base de datos
        user, created = Usuarios.objects.get_or_create(email=email, defaults={"nombre": name, "rol":"developer"})

        #  Guardar el refresh_token solo si se recibe
        if refresh_token:
            user.refresh_token = refresh_token
            user.save()
        
        

        # 🔥 Obtener el token CSRF para seguridad
        csrf_token = get_token(request)

        print(csrf_token)
        # Generar un token de Django
        token, _ = Token.objects.get_or_create(user=user)

        response = Response({
            "token": token.key,
            "user": {"email": user.email, "nombre": user.nombre},
            "is_new_user": created
        }, status=status.HTTP_200_OK)

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,  # No accesible desde JavaScript
            secure=False,  # Solo en HTTPS (puedes cambiarlo a False en desarrollo)
            samesite="Lax",
            max_age=3600,  # 1 hora
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token if refresh_token else "",
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=60 * 60 * 24 ,  # 1 día
        )

        response.set_cookie("csrftoken", csrf_token, secure=False, samesite="Lax")
        # 🔥 Iniciar sesión en Django
        login(request, user)
        return response

    except Exception as e:
        return Response({"error": "Error en la autenticación con Google.", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
def refresh_google_token(request):
    email = request.data.get("email")
    
    if not email:
        return Response({"error": "No se proporcionó email"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = Usuarios.objects.get(email=email)
        refresh_token = user.refresh_token

        if not refresh_token:
            return Response({"error": "No se encontró refresh_token para este usuario"}, status=status.HTTP_400_BAD_REQUEST)

        # Solicitar un nuevo access_token a Google
        google_token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        token_response = req.post(google_token_url, data=token_data)

        if token_response.status_code != 200:
            return Response({"error": "No se pudo renovar el token", "details": token_response.json()}, status=status.HTTP_400_BAD_REQUEST)

        token_json = token_response.json()
        new_access_token = token_json.get("access_token")
        expires_in = token_json.get("expires_in")

        return Response({
            "access_token": new_access_token,
            "expires_in": expires_in
        }, status=status.HTTP_200_OK)

    except Usuarios.DoesNotExist:
        return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": "Error al renovar el token", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)



@api_view(["POST"])
def logout_view(request):
    print("✅ Cookies recibidas:", request.COOKIES)  # 🔥 Ver cookies
    print("✅ Headers recibidos:", request.headers)  # 🔥 Ver headers
    print("✅ Usuario autenticado:", request.user)  # 🔥 Ver usuario
    print("Usuario autenticado:", request)  # 🔥 Debería mostrar el usuario
    logout(request)
    print("Después del logout, usuario:", request.user)  # 🔥 Debería estar vacío
    # 🔥 Elimina las cookies de sesión y CSRF
    response = Response({"message": "Sesión cerrada correctamente"}, status=200)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    response.delete_cookie("csrftoken")
     # 🔥 Eliminar todas las cookies relacionadas con autenticación
    response.delete_cookie("sessionid", path="/")
    response.delete_cookie("csrftoken", path="/")
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")

    return response



@api_view(["GET"])
def test_csrf(request):
    csrf_token = get_token(request)
    print("CSRF Token generado:", csrf_token)  # 🔍 Verifica que se genere
    response = Response({"csrf_token": csrf_token})
    response.set_cookie("csrftoken", csrf_token, secure=False, samesite="Lax")
    return response