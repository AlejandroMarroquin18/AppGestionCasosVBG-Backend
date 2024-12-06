from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import UserSerializer,RestorePasswordTokenSerializer
from django.contrib.auth.models import User
from .models import Usuarios, Restore_Password_Token
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail



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
        print("no se pudo")
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
    