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
from google.auth.transport import requests as g_requests
from google.oauth2 import id_token
import os
from django.http import JsonResponse
import json
from django.middleware.csrf import get_token
from django.contrib.auth import login, logout
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views.decorators.csrf import csrf_exempt
from login.googleUtils import exchange_code_for_tokens, ensure_google_access_token, refresh_access_token
from login.models import GoogleOAuth
from django.utils import timezone
import datetime
from datetime import timedelta
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes
from .helpers import identificar_usuario_por_token_string




@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def login_view(request):
    
    user=get_object_or_404(Usuarios,email=request.data['email'])
    valid= user.check_password(request.data['password'])
    if not valid:
        print("contraseña invalida")
        return Response({"error": "Invalid Password"}, status=status.HTTP_401_UNAUTHORIZED)
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(instance=user)
    #login(request, user)  # Iniciar sesión en Django
    
    return Response({"token":token.key,"user": serializer.data},status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def register_view(request):
    data = request.data.copy()
    data['username'] = data.get('email', '').split('@')[0]
    serializer = UserSerializer(data=data)
    

    # Verificar si viene el password
    if not request.data.get('password'):
        return Response({'error': 'La contraseña es obligatoria.'}, status=status.HTTP_400_BAD_REQUEST)

    if serializer.is_valid():
        # Guardar el usuario (rol será asignado dentro del serializer)
        serializer.save()
        
        user = Usuarios.objects.get(email=serializer.data['email'])
        user.set_password(request.data['password'])
        user.save()

        token = Token.objects.create(user=user)
        return Response({'token': token.key, "user": serializer.data}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
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
@authentication_classes([])
@permission_classes([AllowAny])
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
@authentication_classes([])
@permission_classes([AllowAny])
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
@authentication_classes([])
@permission_classes([AllowAny])
def googleAuth(request):
    """
    Autenticación Google para WEB:
    - Recibe `code` (authorization code de OAuth o serverAuthCode).
    - Intercambia por access_token y refresh_token.
    - Guarda en GoogleOAuth vinculado al usuario.
    - Devuelve token interno para la API (no devuelve tokens de Google).
    """
    
    auth_code = request.data.get('code')
    if not auth_code:
        return Response({"error": "No se recibió el código de autorización."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # 1. Intercambiar el código por tokens en Google
        token_data = exchange_code_for_tokens(auth_code)
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        expires_in = token_data.get("expires_in", 3600)
        token_type = token_data.get("token_type", "Bearer")
        scope = token_data.get("scope")

        if not access_token:
            return Response({"error": "No se pudo obtener el access_token."}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Obtener información del usuario desde Google
        google_user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        google_response = requests.get(google_user_info_url, headers=headers)
        if google_response.status_code != 200:
            return Response({"error": "Error al verificar el usuario en Google."}, status=status.HTTP_400_BAD_REQUEST)

        user_data = google_response.json()
        email = user_data.get('email')
        name = user_data.get('name', '')
        username = email.split('@')[0]


        if not email:
            return Response({"error": "No se pudo obtener el correo del usuario."}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Crear o recuperar usuario en la base de datos
        user, created = Usuarios.objects.get_or_create(email=email, defaults={
            "nombre": name, 
            "rol": "visitor",
            "username": username
            })

        # 4. Guardar credenciales en GoogleOAuth
        expires_at = timezone.now() + timedelta(seconds=expires_in)
        old_refresh_token = getattr(getattr(user, "google_oauth", None), "refresh_token", None)

        userCreds, createdCreds = GoogleOAuth.objects.update_or_create(
            user=user,
            defaults={
                "access_token": access_token,
                "refresh_token": refresh_token or old_refresh_token,  # mantener el anterior si no llega
                "token_type": token_type,
                "scope": scope,
                "expires_at": expires_at,
                "raw": token_data
            }
        )

        
        token, _ = Token.objects.get_or_create(user=user)
        response = Response({
            "token": token.key,
            "user": {"email": user.email, "nombre": user.nombre},
            "is_new_user": created
        }, status=status.HTTP_200_OK)
        

        #login(request, user)  # Iniciar sesión en Django En produccion
        

        '''# Crear token interno de la API (DRF Token)
        
        response.set_cookie(
            key="auth_token",
            value=token.key,
            httponly=True,
            secure=False,  # solo HTTPS en producción
            samesite="Lax",
            max_age=60 * 60 * 24 * 7  # 7 días
        )'''
        csrf_token = get_token(request)
        #response.set_cookie("csrftoken", csrf_token, secure=False, samesite="Lax")
        response.set_cookie(
            key="csrftoken",
            value=csrf_token,
            httponly=False,   # React necesita leerlo
            secure=False,     # poner True en producción
            samesite="Lax",
            path="/",
            max_age=60 * 60 * 24 * 7  # 7 días
        )
        

        return response

    except requests.RequestException as e:
        return Response({"error": "Error comunicándose con Google.", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print("ERROR en google_callback:", str(e))
        import traceback
        traceback.print_exc()
        return Response({"error": "Error en la autenticación.", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)






@api_view(["POST"])##dev
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout_view(request):
    print("✅ Cookies recibidas:", request.COOKIES)  # 🔥 Ver cookies
    print("✅ Headers recibidos:", request.headers)  # 🔥 Ver headers
    print("✅ Usuario autenticado:", request.user)  # 🔥 Ver usuario
    print("Usuario autenticado:", request)  # 🔥 Debería mostrar el usuario
    #quitar en produccion y dejar solo logout(request)
    try:
        user=request.user
        
        if user:
            token = Token.objects.get(user=user)
            token.delete()
            #logout(request)  # Cierra la sesión en Django
            return Response({"message": "Sesión cerrada correctamente"}, status=200)
        else:
            return Response({"error": "Token inválido o usuario no encontrado"}, status=400)
            
    except Token.DoesNotExist:
        auth_details = {
            "error": "Token no encontrado en BD pero header presente",
        }
        print("ERROR: Header de token presente pero token no existe en BD")
        return Response(auth_details, status=400)




@api_view(["GET"])
def test_csrf(request):
    csrf_token = get_token(request)
    print("CSRF Token generado:", csrf_token)
    response = Response({"csrf_token": csrf_token})
    response.set_cookie("csrftoken", csrf_token, secure=False, samesite="Lax")
    return response



GOOGLE_ANDROID_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")  # del Cloud Console

@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def android_auth(request):
    
    """
    Recibe: id_token (Google) y opcionalmente server_auth_code (Google Sign-In).
    Verifica identidad, crea/recupera user, emite token DRF y, si hay server_auth_code,
    canjea y guarda access/refresh token de Google Calendar.
    """
    id_token_google = request.data.get('id_token')
    server_auth_code = request.data.get('server_auth_code')  # <--- NUEVO

    if not id_token_google:
        return Response({"error": "No se recibió el id_token."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        idinfo = id_token.verify_oauth2_token(
            id_token_google,
            g_requests.Request(),
            GOOGLE_ANDROID_CLIENT_ID  # tu client id Android
        )
        email = idinfo.get('email')
        name = idinfo.get('name')

        if not email:
            return Response({"error": "No se pudo obtener el email del token."}, status=status.HTTP_400_BAD_REQUEST)

        user, created = Usuarios.objects.get_or_create(
            email=email,
            defaults={"nombre": name, "rol": "visitor", "username": email.split('@')[0]}
        )

        # Si el cliente envía server_auth_code, canjeamos por tokens de Google
        if server_auth_code:
            data = exchange_code_for_tokens(server_auth_code,True)
            access_token = data["access_token"]
            expires_in = data.get("expires_in", 3600)
            refresh_token = data.get("refresh_token")  # puede venir solo la primera vez
            token_type = data.get("token_type", "Bearer")
            scope = data.get("scope")

            # crea o actualiza credenciales
            obj, _ = GoogleOAuth.objects.get_or_create(user=user)
            obj.access_token = access_token
            obj.token_type = token_type
            obj.scope = scope
            obj.expires_at = timezone.now() + datetime.timedelta(seconds=expires_in)
            # Si Google no envía refresh_token (ya otorgado antes), conserva el actual
            if refresh_token:
                obj.refresh_token = refresh_token
            obj.raw = data
            obj.save()

        # Token interno del backend (DRF)
        token, _ = Token.objects.get_or_create(user=user)
        #login(request, user)  # Iniciar sesión en Django

        return Response({
            "token": token.key,
            "user": {"email": user.email, "nombre": user.nombre, "rol":user.rol},
            "is_new_user": created,
            "google_calendar_linked": bool(getattr(user, "google_oauth", None))
        },status=status.HTTP_200_OK)

    except ValueError:
        return Response({"error": "El id_token no es válido o expiró."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": "Error en autenticación con Google.", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
''' produccion
@api_view(['GET'])
@permission_classes([IsAuthenticated])##produccion
def check_session(request):
    print("=== CHECK SESSION DEBUG ===")
    print("Request.user:", request.user)
    print("Request.user.is_authenticated:", request.user.is_authenticated)
    print("Cookies recibidas:", dict(request.COOKIES))
    print("Session key recibida:", request.session.session_key)
    print("Session data:", dict(request.session))
    print("User ID en sesión:", request.session.get('_auth_user_id'))
    
    if not request.user.is_authenticated:
        return Response({
            "error": "Usuario no autenticado", 
            "debug": {
                "cookies": dict(request.COOKIES),
                "session_key": request.session.session_key
            }
        }, status=401)
    
    user = request.user
    
    return Response({
        "is_authenticated": True,
        "user": {
            "email": user.email,
            "nombre": user.nombre,
        }
    })'''



@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def check_session(request):
    try:
        '''authorization_header = request.headers.get('Authorization')

         
        if not authorization_header.startswith('Bearer '):
            return Response({
                'error': 'Header Authorization requerido con formato: Bearer <token>'
            }, status=400)
        
        # Extraer el token
        token_string = authorization_header.split(' ')[1]'''
        
        # Identificar usuario manualmente
        #user = identificar_usuario_por_token_string(token_string)
        user=request.user
        print("Usuario autenticado en check_session:", user)
        return Response({
            "is_authenticated": user is not None,
            "user": {
                "email": user.email,
                "nombre": user.nombre,
                "rol": user.rol,
            } if user else None
        }, status=200 if user else 401)
        
            
    except Token.DoesNotExist:
        auth_details = {
            "error": "Token no encontrado en BD pero header presente",
        }
        #print("ERROR: Header de token presente pero token no existe en BD")
    
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def authorize_google_access(request):
    ##user=request.user
    auth_code=request.data.get('server_auth_code')
    accessTokenFromRequest = request.data.get('access_token')
    try:
        # 1. Intercambiar el código por tokens en Google
        token_data = exchange_code_for_tokens(auth_code,True)
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        expires_in = token_data.get("expires_in", 3600)
        token_type = token_data.get("token_type", "Bearer")
        scope = token_data.get("scope")
        scope = token_data.get("scope")
        if isinstance(scope, str):
            scope = scope.split(" ")

        if not access_token:
            return Response({"error": "No se pudo obtener el access_token."}, status=status.HTTP_404_NOT_FOUND)

        # 2. Obtener información del usuario desde Google
        google_user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        google_response = requests.get(google_user_info_url, headers=headers)
        if google_response.status_code != 200:
            return Response({"error": "Error al verificar el usuario en Google."}, status=status.HTTP_400_BAD_REQUEST)

        user_data = google_response.json()
        email = user_data.get('email')
        name = user_data.get('name', '')

        if not email:
            return Response({"error": "No se pudo obtener el correo del usuario."}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Crear o recuperar usuario en la base de datos
        user = Usuarios.objects.get(email=email)

        #4. Guardar credenciales en GoogleOAuth
        expires_at = timezone.now() + timedelta(seconds=expires_in)
        old_refresh_token = getattr(getattr(user, "google_oauth", None), "refresh_token", None)

        userCreds, createdCreds = GoogleOAuth.objects.update_or_create(
            user=user,
            defaults={
                "access_token": access_token,
                "refresh_token": refresh_token or old_refresh_token,  # mantener el anterior si no llega
                "token_type": token_type,
                "scope": scope,
                "expires_at": expires_at,
                "raw": token_data
            }
        )

        # Token interno del backend (DRF)
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "token": token.key,
            "google_calendar_linked": bool(getattr(user, "google_oauth", None))

        }, status=status.HTTP_200_OK)

    except ValueError:
        return Response({"error": "El id_token no es válido o expiró."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": "Error en autenticación con Google.", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)


