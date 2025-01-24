"""
URL configuration for appvbgbackend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from login import views
from rest_framework.routers import DefaultRouter
from quejas.views import QuejaViewSet

router = DefaultRouter()
router.register(r'quejas', QuejaViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/login/", views.login_view, name="login_view"),
    path("api/register/", views.register_view, name="register_view"),
    path("api/forgottenPassword/", views.forgottenPassword_view, name="forgottenPassword_view"),
    path("api/validateForgottenPasswordCode/", views.confirmForgottenPasswordCode_view, name="ConfirmForgottenPasswordCode_view"),
    path("api/changeForgottenPassword/", views.changeForgottenPassword_view, name="changeForgottenPassword_view"),
    path("api/auth/google/", views.googleAuth, name="googleAuth_view"),
    path('admin/', admin.site.urls),
    path('api/quejas/', include('quejas.urls')),
]