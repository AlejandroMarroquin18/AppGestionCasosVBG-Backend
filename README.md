# AppGestionCasosVBG-Backend
Backend para manejar la app de gestión de casos de VBG para Univalle.

#ejecutar servidor

.\venv\Scripts\activate

python manage.py runserver 0.0.0.0:8000

python manage.py runserver_plus --cert-file cert.crt --key-file key.key 0.0.0.0:8000
python manage.py runserver_plus --cert-file cert.crt --key-file key.key



# Backend de la plataforma de AppVBG

Backend de la plataforma para el Área de atención de violencias y discriminaciones basadas en genero

Esta aplicación es la encargada de manejar todas las peticiones realizadas mediante las aplicaciones 
web y móvil, además de manipular la base de datos de la plataforma 

---

## 🚀 Requisitos previos

Herramientas y requisitos previos:

- Python 3.13.0 o superior
- Base de datos relacional SQL (Ej. PostgreSQL)
- Todas las librerías y versiones que se encuentran en el archivo requirements.txt
- Cuenta de correo electronico con una contraseña de aplicación habilitada para el envío de correos
- Cuenta de Google Cloud Console con una credencial de cliente Web, una de cliente de Android y la API de Google 
    Calendar habilitada con los siguientes scopes solicitados
    https://www.googleapis.com/auth/calendar
    https://www.googleapis.com/auth/calendar.events
-


##Setup del servidor
Antes de poder inicializar el servidor, es necesario establecer las variables de entorno y credenciales utilizadas para el proyecto
1. Archivo .env
El archivo .env debe verse así

2. Establecimiento de las ips del backend
En el archivo settings.py, ubicado en 
./appvbgbackend/settings.py
se debe establecer la ip en la que se va a alojar esta aplicación en las variables:
- BACKEND_URL
- ALLOWED_HOSTS

3. Establecimiento de las ips de la aplicación web
En el archivo settings.py, ubicado en 
./appvbgbackend/settings.py
se deben establecer la ips desde las cuales la aplicación podrá recibir peticiones en las variables:
- GOOGLE_REDIRECT_URI
- CORS_ALLOWED_ORIGINS
- CSRF_TRUSTED_ORIGINS

##Paso a paso de inicialización del servidor:
1. Creacion del entorno virtual 
```bash
python -m venv venv
   ```
2. Instalación de librerías necesarias
```bash
pip install -r requirements.txt
   ```
3. Creacion de las migraciones en caso de haber realizado un cambio en los models.py
```bash
python manage.py makemigrations
```
4. Aplicación de las migraciones
```bash
python manage.py migrate
```
5. inicializar el servidor
```bash
python manage.py runserver 0.0.0.0:8000
```




Ejemplo:
```bash
sudo apt-get install git
