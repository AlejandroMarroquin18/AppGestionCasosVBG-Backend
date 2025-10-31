from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import requests
from login.googleUtils import ensure_google_access_token
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes
from login.helpers import obtener_usuario_de_request
from agenda.models import Event
from agenda.serializers import EventSerializer

API_URL = "https://www.googleapis.com/calendar/v3"

'''def get_token_from_cookies(request):
    """Helper function to extract the token from cookies"""
    access_token = request.COOKIES.get('access_token')
    if not access_token:
        return None
    return access_token

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_events(request,year):
    """
    Fetch events from Google Calendar for a specific year.
    Expects 'year' as a query parameter.
    """
    #year = request.GET.get('year')
    if not year:
        return Response({"error": "Year parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    access_token = get_token_from_cookies(request)
    if not access_token:
        return Response({"error": "Access token not found in cookies"}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Define date range for the year
    time_min = f"{year}-01-01T00:00:00Z"
    time_max = f"{year}-12-31T23:59:59Z"
    
    all_events = []
    next_page_token = None
    
    try:
        while True:
            params = {
                "maxResults": "250",
                "orderBy": "startTime",
                "singleEvents": "true",
                "timeMin": time_min,
                "timeMax": time_max
            }
            
            if next_page_token:
                params["pageToken"] = next_page_token
                
            response = requests.get(
                f"{API_URL}/calendars/primary/events",
                params=params,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if not response.ok:
                return Response(response.json(), status=response.status_code)
            
            data = response.json()
            
            if data.get('items'):
                all_events.extend(data['items'])
                
            next_page_token = data.get('nextPageToken')
            if not next_page_token:
                break
        
        return Response(all_events)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_event(request):
    """
    Create a new event in Google Calendar.
    Expects event data in the request body.
    """

    access_token = get_token_from_cookies(request)
    
    if not access_token:
        return Response({"error": "Access token not found in cookies"}, status=status.HTTP_401_UNAUTHORIZED)
    
    event_data = request.data
    
    try:
        response = requests.post(
            f"{API_URL}/calendars/primary/events?conferenceDataVersion=1",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            json=event_data
        )
        
        data = response.json()
        
        if response.ok:
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            error_message = data.get('error', {}).get('message', 'Unknown error creating event')
            return Response({"error": error_message}, status=response.status_code)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_event(request,eventId):
    """
    Update an existing event in Google Calendar.
    Expects event_id as URL parameter and updated data in request body.
    """
    access_token = get_token_from_cookies(request)

    updatedData= request.data

    



    if not access_token:
        return Response({"error": "Access token not found in cookies"}, status=status.HTTP_401_UNAUTHORIZED)
    
    #updated_data = request.data

    
    try:

        seq = requests.get(
            f"{API_URL}/calendars/primary/events/{eventId}",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        response = requests.put(
            f"{API_URL}/calendars/primary/events/{eventId}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            json=updatedData
        )
        
        if response.ok:
            return Response(response.json(), status=status.HTTP_200_OK)
        else:
            return Response(response.json(), status=response.status_code)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_event(request,eventId):
    """
    Delete an event from Google Calendar.
    Expects event_id as URL parameter.
    """

    
    

    access_token = get_token_from_cookies(request)
    if not access_token:
        return Response({"error": "Access token not found in cookies"}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        response = requests.delete(
            f"{API_URL}/calendars/primary/events/{eventId}",
            headers={
                "Authorization": f"Bearer {access_token}",
                
            }
        )
        
        if response.ok:
            return Response({"message": "Event deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Failed to delete event"}, status=response.status_code)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_event_by_id(request,eventId):
    """
    Fetch a specific event by its ID.
    Expects event_id as URL parameter.
    """

    
    
    access_token = get_token_from_cookies(request)
    if not access_token:
        return Response({"error": "Access token not found in cookies"}, status=status.HTTP_401_UNAUTHORIZED)
    
    if not eventId:
        return Response({"error": "Event ID is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        response = requests.get(
            f"{API_URL}/calendars/primary/events/{eventId}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if not response.ok:
            return Response({"error": response.reason}, status=response.status_code)
        
        return Response(response.json(), status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)'''



API_URL = "https://www.googleapis.com/calendar/v3"

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def fetch_events(request, year):

   
    if not year:
        return Response({"error": "Year parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user=request.user
        
        access_token = ensure_google_access_token(user)
    except Exception as e:
        return Response({"error dentro del endpoint": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

    time_min = f"{year}-01-01T00:00:00Z"
    time_max = f"{year}-12-31T23:59:59Z"

    all_events, next_page_token = [], None
    try:
        while True:
            params = {
                "maxResults": "250",
                "orderBy": "startTime",
                "singleEvents": "true",
                "timeMin": time_min,
                "timeMax": time_max
            }
            if next_page_token:
                params["pageToken"] = next_page_token

            resp = requests.get(
                f"{API_URL}/calendars/primary/events",
                params=params,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if not resp.ok:
                return Response(resp.json(), status=resp.status_code)

            data = resp.json()
            all_events.extend(data.get("items", []))
            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break

        return Response(all_events)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_event(request):
    try:
        user=request.user
        access_token = ensure_google_access_token(user)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

    google_event_data = request.data
    event_data = request.data.copy()

    backendEvent = event_data.pop("backendEvent", {})
    print(backendEvent)
    #del event_data["backendEvent"]

    try:
        resp = requests.post(
            f"{API_URL}/calendars/primary/events?conferenceDataVersion=1",
            headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
            json=google_event_data
        )
        data = resp.json()
        
        if not resp.ok:
            return Response({"error": data.get('error', {}).get('message', 'Unknown error')}, status=resp.status_code)

        backendEvent["google_event_id"] = data.get("id")
        backendEvent["meet_link"] = data.get("hangoutLink", "")

        
        serializer = EventSerializer(data=backendEvent)
        
        if serializer.is_valid():
            print("Serializer válido")
            serializer.save()
        print(serializer.errors)
        
        
        '''event = Event.objects.create(
            title=data.get("summary", ""),
            description=data.get("description", ""),
            status=data.get("status", "Creado"),
            location=data.get("location", ""),
            attendes=",".join([att["email"] for att in data.get("attendees", [])]) if "attendees" in data else None,
            color=data.get("colorId", None),
            organizer=data.get("organizer", {}).get("email", user.email),
            startdatehour=data["start"].get("dateTime"),
            enddatehour=data["end"].get("dateTime"),
            timezone=data["start"].get("timeZone", "America/Bogota"),
            type=event_data.get("type", ""),
            case_id_id=event_data.get("case_id"),
            create_meet="hangoutLink" in data,
            meet_link=data.get("hangoutLink"),
            google_event_id=data.get("id")
        )'''
        return Response(data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_event(request, eventId):
    try:
        user=request.user
        access_token = ensure_google_access_token(user)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

    updatedData = request.data
    try:
        resp = requests.put(
            f"{API_URL}/calendars/primary/events/{eventId}",
            headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
            json=updatedData
        )
        data = resp.json()

        if not resp.ok:
            return Response(resp.json(), status=resp.status_code)
    
        try:
            event = Event.objects.get(google_event_id=eventId)
            event.title = data.get("summary", event.title)
            event.description = data.get("description", event.description)
            event.location = data.get("location", event.location)
            event.attendes = [att["email"] for att in data.get("attendees", [])] if "attendees" in data else event.attendes
            event.color = data.get("colorId", event.color)
            event.startdatehour = data["start"].get("dateTime", event.startdatehour)
            event.enddatehour = data["end"].get("dateTime", event.enddatehour)
            event.timezone = data["start"].get("timeZone", event.timezone)
            event.meet_link = data.get("hangoutLink", event.meet_link)
            event.save()
        except Event.DoesNotExist:
            pass  # si no existe en DB, solo se mantiene en Google
        
        return Response(data, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(e)
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_event(request, eventId):
    try:
        user=request.user
        access_token = ensure_google_access_token(user)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        resp = requests.delete(
            f"{API_URL}/calendars/primary/events/{eventId}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if not resp.ok:
            return Response({"error": "Failed to delete event"}, status=resp.status_code)
        
            
        
        Event.objects.filter(google_event_id=eventId).delete()

        return Response({"message": "Event deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def fetch_event_by_id(request, eventId):
    if not eventId:
        return Response({"error": "Event ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user=request.user
        access_token = ensure_google_access_token(user)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        resp = requests.get(
            f"{API_URL}/calendars/primary/events/{eventId}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if not resp.ok:
            return Response(resp.json(), status=resp.status_code)
        return Response(resp.json(), status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
