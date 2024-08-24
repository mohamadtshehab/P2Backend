from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
import requests
import base64
from p2.settings import MULTIVIEW_NGROK_URL, MESH_NGROK_URL
from django.shortcuts import get_object_or_404
from .helper import format_flask_response_data, handle_flask_text_post_request
from django.core.files.uploadedfile import SimpleUploadedFile

class ObjectView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        object = get_object_or_404(Object, td_model=pk)
        serializer = ObjectSerializer(object)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def delete(self, request, pk):
        object = Object.objects.get(td_model=pk)
        object.delete()
        return Response(status=status.HTTP_200_OK)

class ObjectListView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = ObjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RoomListView(APIView):
    permission_classes = [IsAuthenticated]
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
    permission_classes = [IsAuthenticated]
    def get(self, request, userId):
        if request:
            rooms = Room.objects.select_related('td_model').filter(user=userId)
        rooms = Room.objects.filter(user=userId)
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RoomObjectListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, roomId):
        objects = Object.objects.select_related('td_model', 'category').filter(room=roomId)
        serializer = ObjectSerializer(objects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, userId):
        user = get_object_or_404(User, id=userId)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserListView(APIView):
    def get(self, request):
        self.permission_classes = [IsAuthenticated]
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
    permission_classes = [IsAuthenticated]
    def get(self, request, objectId):
        images = ObjectImage.objects.filter(object=objectId)
        serializer = ObjectImageSerializer(images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ObjectTextureListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, reqeuest, objectId):
        textures = Texture.objects.filter(object=objectId)
        serializer = TextureSerializer(textures, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class TextureListView(APIView):
    permission_classes = [IsAuthenticated]
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
class ObjectGenerationView(APIView):
    def post(self, request):
        
        # Send a multi-view-image-generation request to flask and receive its response
        request_image = request.FILES['image']
        url = f'{MULTIVIEW_NGROK_URL}/generate_multi_views'
        image = {'image': ('image.png', request_image)}
        try:
            response = requests.post(url, files=image)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error communicating with Flask service: {str(e)}")
        
        response_data = response.json()
        
        # Store the multi-view image
        encoded_image = response_data['image']
        image_name = response_data['image_name']
        decoded_image = base64.b64decode(encoded_image)
        
        # Send a 3D-object-generation request and receive its response
        url = f'{MESH_NGROK_URL}/generate_mesh'
        image = {'image': (image_name, decoded_image)}
        try:
            response = requests.post(url, files=image)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error communicating with Flask service: {str(e)}")
        response_data = response.json()
        
        # -----Store the 3D object------
        # get data from response
        encoded_model = response_data['model']
        encoded_material = response_data['material']
        encoded_texture = response_data['texture']
        # get files' names
        model_name = response_data['model_name']
        material_name = model_name.split('.')[0] + '.mtl'
        texture_name = model_name.split('.')[0] + '.png'
        
        # Save files into storage
        decoded_model = base64.b64decode(encoded_model)
        model = SimpleUploadedFile(model_name, decoded_model)
            
        decoded_material = base64.b64decode(encoded_material)
        material = SimpleUploadedFile(material_name, decoded_material)
        
        decoded_texture = base64.b64decode(encoded_texture)
        texture = SimpleUploadedFile(texture_name, decoded_texture)
        
        # Store td_model into database
        td_model_name = request.data.get('name')
        td_model_description = request.data.get('description')
        td_model_type = request.data.get('type')
        
        td_model_data = {
            'name': td_model_name,
            'description': td_model_description,
            'type': td_model_type
        }
        
        td_model_serializer = TDModelSerializer(data=td_model_data)
        td_model_serializer.is_valid(raise_exception=True)
        td_model = td_model_serializer.save()
        
        # Create category
        category_name = request.data.get('category')
        category, _ = Category.objects.get_or_create(name=category_name)
        
        # Get the id of the room containing the object
        room_id = request.data.get('room')
        
        # Store the object in database
        object_data = {
            'label': model_name,
            'td_model': td_model.id,
            'category': category.id,
            'room': room_id,
            'file': model,
            'material': material
        }
        object_serializer = ObjectSerializer(data=object_data)
        object_serializer.is_valid(raise_exception=True)
        object_instance = object_serializer.save()
        
        # Store texture and object image in database
        Texture.objects.create(name=texture_name, image=texture, object=object_instance)
        ObjectImage.objects.create(image=request_image, object=object_instance)
        
        return Response(data=object_serializer.data, status=status.HTTP_200_OK)

'''
Method:     POST
url:        {host}/api/objects/generation_from_text
body:{
    'prompt': required,
}
'''
class GenerateImageFromTextView(APIView):
    def post(self, request):
        # send the request to flask on colab
        response = handle_flask_text_post_request(request)
        if response.status_code != 200:
            return Response({"error": "Failed to communicate with Flask app"}, status=status.HTTP_400_BAD_REQUEST)
        # format the flask response 
        image = format_flask_response_data(response)
        
        return Response(image, status=status.HTTP_200_OK)