from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import requests
import json

API_URL = "https://www.googleapis.com/calendar/v3"

def get_token_from_cookies(request):
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
    print("hola")
    if not access_token:
        return Response({"error": "Access token not found in cookies"}, status=status.HTTP_401_UNAUTHORIZED)
    
    event_data = request.data
    print("hola2")
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
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)