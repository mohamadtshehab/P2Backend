from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .serializers import *
from .models import *
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
class ObjectView(APIView):
    def get(self, request, pk):
        object = Object.objects.get(td_model=pk)
        serializer = ObjectSerializer(object)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def delete(self, request, pk):
        object = Object.objects.get(td_model=pk)
        object.delete()
        return Response(status=status.HTTP_200_OK)

class ObjectListView(APIView):
    def post(self, request):
        serializer = ObjectSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserRoomList(APIView):
    def get(self, request, userId):
        rooms = Room.objects.filter(user=userId)
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RoomObjectList(APIView):
    def get(self, request, roomId):
        objects = Object.objects.select_related('td_model').filter(room=roomId)
        serializer = ObjectSerializer(objects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)