# talleres/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import WorkshopSerializer
from .models import Workshop
from rest_framework import status
from django.shortcuts import get_object_or_404

@api_view(['GET', 'POST'])
def workshop_list(request):
    if request.method == 'GET':
        workshops = Workshop.objects.all()
        serializer = WorkshopSerializer(workshops, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = WorkshopSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'DELETE', 'PATCH'])  # Added PATCH
def workshop_detail(request, pk):
    workshop = get_object_or_404(Workshop, pk=pk)
    if request.method == 'GET':
        serializer = WorkshopSerializer(workshop)
        return Response(serializer.data)
    elif request.method == 'DELETE':
        workshop.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    elif request.method == 'PATCH':
        serializer = WorkshopSerializer(workshop, data=request.data, partial=True)  # partial=True allows for partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
