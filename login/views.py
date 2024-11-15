from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import UserSerializer
from django.contrib.auth.models import User
from .models import Usuarios
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.shortcuts import get_object_or_404



@api_view(['POST'])
def login_view(request):
    print(request.data)
    user=get_object_or_404(Usuarios,email=request.data['email'])
    print(user)
    print(request.data['password'])
    valid= user.check_password(request.data['password'])
    #valid=user.password==request.data['password']
    print(valid)
    if not valid:
        return Response({"error": "Invalid Password"}, status=status.HTTP_401_UNAUTHORIZED)
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(instance=user)
    print(serializer.data)
    return Response({"token":token.key,"user": serializer.data},status.HTTP_200_OK)

@api_view(['POST'])
def register_view(request):
    serializer=UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = Usuarios.objects.get(email=serializer.data['email'])
        user.set_password(request.data['password'])
        user.save()
        token = Token.objects.create(user=user)
        return Response({'token':token.key, "user": serializer.data}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)












'''from django.contrib.auth import login
from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from login.authentication import EmailAuthBackend  # Importa tu backend



@csrf_exempt
@api_view(['POST'])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    # Usa tu backend personalizado para autenticar
    user = EmailAuthBackend().authenticate(request, email=email, password=password)
    
    if user is not None:
        login(request, user)
        return JsonResponse({"message": "Login exitoso"}, status=200)
    else:
        return JsonResponse({"error": "Credenciales inválidas"}, status=400)'''