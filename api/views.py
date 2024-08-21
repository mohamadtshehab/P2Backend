from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FileUploadParser
import requests
import base64
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from p2.settings import NGROK_URL
from django.shortcuts import get_object_or_404
from django.core.files.uploadedfile import SimpleUploadedFile
import pdb

class ObjectView(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        object = get_object_or_404(Object, td_model=pk)
        serializer = ObjectSerializer(object)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def delete(self, request, pk):
        object = Object.objects.get(td_model=pk)
        object.delete()
        return Response(status=status.HTTP_200_OK)

class ObjectListView(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = ObjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RoomListView(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request):
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserRoomListView(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request, userId):
        if request:
            rooms = Room.objects.select_related('td_model').filter(user=userId)
        rooms = Room.objects.filter(user=userId)
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RoomObjectListView(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request, roomId):
        objects = Object.objects.select_related('td_model', 'category').filter(room=roomId)
        serializer = ObjectSerializer(objects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserView(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request, userId):
        user = get_object_or_404(User, id=userId)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserListView(APIView):
    def get(self, request):
        # self.permission_classes = [IsAuthenticated]
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ObjectImageListView(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request, objectId):
        images = ObjectImage.objects.filter(object=objectId)
        serializer = ObjectImageSerializer(images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ObjectTextureListView(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, reqeuest, objectId):
        textures = Texture.objects.filter(object=objectId)
        serializer = TextureSerializer(textures, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class TextureListView(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request):
        textures = Texture.objects.all()
        serializer = TextureSerializer(textures, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def post(self, request):
        serializer = TextureSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
class RoomView(APIView):
    def delete(self, request, roomId):
        room = get_object_or_404(Room, td_model=roomId)
        room.delete()
        return Response(status=status.HTTP_200_OK)
    
'''
Method:     POST
url:        {host}/api/objects/generation
body:{
    'image': required,
    'name'
    'description',
    'scaling',
    'rotation',
    'translation',
    'color',
    'type': required,
    'category: required',
    'room_id: required'
}

'''
class ImageUploadView(APIView):
    def post(self, request):

        response = self.handle_flask_post_request(request)
        if response.status_code != 200:
            return Response({"error": "Failed to communicate with Flask app"}, status=status.HTTP_400_BAD_REQUEST)
        
        model, material, texture = self.format_flask_response_data(response)
        

        category_name = request.data.get('category')
        category, _ = Category.objects.get_or_create(name=category_name)
        

        object_data = request.data.copy()
        object_data['category'] = category.id
        object_data['label'] = model.name
        object_data['file'] = model
        object_data['material'] = material
        
        td_model_data = {
            'name': request.data.get('name'),
            'description': request.data.get('description'),
            'type': request.data.get('type'),
        }
        
        td_model_serializer = TDModelSerializer(data=td_model_data)
        td_model_serializer.is_valid(raise_exception=True)
        td_model = td_model_serializer.save()
        
        object_data['td_model'] = td_model.id

        object_serializer = ObjectSerializer(data=object_data)
        object_serializer.is_valid(raise_exception=True)
        object_instance = object_serializer.save()

        ObjectImage.objects.create(object=object_instance, image=request.data['image'])
        
        Texture.objects.create(object=object_instance, name=texture.name, image=texture)
        
        return Response(object_serializer.data, status=status.HTTP_200_OK)

    def handle_flask_post_request(self, request):
        image = request.data.get('image')
        flask_post_data = {'image': ('image.jpg', image)}
        try:
            response = requests.post(f'{NGROK_URL}/generate', files=flask_post_data)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error communicating with Flask service: {str(e)}")
        return response
    
    def format_flask_response_data(self, response):
        flask_response_data = response.json()
        
        model_name = flask_response_data.get('model_name')
        material_name = model_name.split('.obj')[0] + '.mtl'
        texture_name = model_name.split('.obj')[0] + '.png'
        
        encoded_model = flask_response_data.get('model')
        decoded_model = base64.b64decode(encoded_model)
        model = SimpleUploadedFile(model_name, decoded_model)
        
        encoded_material = flask_response_data.get('material')
        decoded_material = base64.b64decode(encoded_material)
        material = SimpleUploadedFile(material_name, decoded_material)
        
        encoded_texture = flask_response_data.get('texture')
        decoded_texture = base64.b64decode(encoded_texture)
        texture = SimpleUploadedFile(texture_name, decoded_texture)

        return model, material, texture

    
    
    
class hi(APIView):
    def get(self, request):
        # Send the request to ngrok on colab
        response = requests.get(f'{NGROK_URL}/hi')
        
        if response.status_code == 200:
            # Parse the JSON response from Flask
            flask_response = response.json()
        
        return Response(flask_response, status=status.HTTP_200_OK)