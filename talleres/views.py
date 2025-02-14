# talleres/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import WorkshopSerializer
from .models import Workshop
from rest_framework import status

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