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
- Cuenta de Google Cloud Console con

Ejemplo:
```bash
sudo apt-get install git
