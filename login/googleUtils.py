
import datetime
import requests
from django.conf import settings
from django.utils import timezone

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"

def exchange_code_for_tokens(server_auth_code: str, isAndroid:bool=False) -> dict:
    """
    Intercambia server_auth_code por access_token y refresh_token.s
    Usa el CLIENTE WEB de GCP.
    """
    
    data = {
        "code": server_auth_code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "grant_type": "authorization_code",
        # Para serverAuthCode de Google Sign-In se suele usar este redirect_uri especial:
        "redirect_uri": "postmessage",
    }
    if isAndroid:
        data = {
        "code": server_auth_code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "grant_type": "authorization_code",
        # Para serverAuthCode de Google Sign-In se suele usar este redirect_uri especial:
        }

    
    r = requests.post(GOOGLE_TOKEN_URL, data=data, timeout=15)

    #print("GOOGLE RESPONSE:", r.status_code, r.text)
    r.raise_for_status()
    return r.json()

def refresh_access_token(refresh_token: str) -> dict:
    data = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    r = requests.post(GOOGLE_TOKEN_URL, data=data, timeout=15)
    
    r.raise_for_status()
    return r.json()

def ensure_google_access_token(user) -> str:
    """
    Devuelve un access_token válido para el usuario.
    Si expiró y hay refresh_token, renueva y persiste.
    """
    cred = getattr(user, "google_oauth", None)
    
    if not cred:
        raise RuntimeError("No hay credenciales de Google vinculadas al usuario.")

    # margen de 60s
    if cred.expires_at and (cred.expires_at - timezone.now()) > datetime.timedelta(seconds=60):
        return cred.access_token

    if not cred.refresh_token:
        raise RuntimeError("Access token expirado y no hay refresh_token para renovar.")

    data = refresh_access_token(cred.refresh_token)
    access_token = data["access_token"]
    expires_in = data.get("expires_in", 3600)
    cred.access_token = access_token
    cred.expires_at = timezone.now() + datetime.timedelta(seconds=expires_in)
    cred.token_type = data.get("token_type", cred.token_type)
    cred.scope = data.get("scope", cred.scope)
    cred.save(update_fields=["access_token", "expires_at", "token_type", "scope", "updated_at"])
    return cred.access_token
