from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
import requests
from p2.settings import NGROK_URL
from django.shortcuts import get_object_or_404
from .helper import format_flask_response_data, handle_flask_image_post_request, handle_flask_text_post_request

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
url:        {host}/api/objects/generation_from_image
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
class GenerateModelFromImageView(APIView):
    def post(self, request):
        # send the request to flask on colab
        response = handle_flask_image_post_request(request)
        if response.status_code != 200:
            return Response({"error": "Failed to communicate with Flask app"}, status=status.HTTP_400_BAD_REQUEST)
        # format the flask response 
        model, material, texture = format_flask_response_data(response)
        # create new category if not exists
        category_name = request.data.get('category')
        category, _ = Category.objects.get_or_create(name=category_name)
        # prepare the object data to be saved later
        object_data = request.data.copy()
        object_data['category'] = category.id
        object_data['label'] = model.name
        object_data['file'] = model
        object_data['material'] = material
        # get the td_model data from the request body
        td_model_data = {
            'name': request.data.get('name'),
            'description': request.data.get('description'),
            'type': request.data.get('type'),
        }
        # save the td_model instance
        td_model_serializer = TDModelSerializer(data=td_model_data)
        td_model_serializer.is_valid(raise_exception=True)
        td_model = td_model_serializer.save()
        # set the td_model to the object and save it 
        object_data['td_model'] = td_model.id
        object_serializer = ObjectSerializer(data=object_data)
        object_serializer.is_valid(raise_exception=True)
        object_instance = object_serializer.save()
        # save the image of the model
        ObjectImage.objects.create(object=object_instance, image=request.data['image'])
        # save the model texture
        Texture.objects.create(object=object_instance, name=texture.name, image=texture)
        # return the response 
        return Response(object_serializer.data, status=status.HTTP_200_OK)

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

class hi(APIView):
    def get(self, request):
        # Send the request to ngrok on colab
        response = requests.get(f'{NGROK_URL}/hi')
        
        if response.status_code == 200:
            # Parse the JSON response from Flask
            flask_response = response.json()
        
        return Response(flask_response, status=status.HTTP_200_OK)