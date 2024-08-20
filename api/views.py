from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .serializers import *
from .models import *
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import *
import requests
from rest_framework.parsers import FileUploadParser
import base64
from p2.settings import NGROK_URL
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
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
url:        {host}/api/room/room_id/predict
body:{
    'image': required,
    'name'
    'description',
    'scaling',
    'rotation',
    'translation',
    'color',
    'type': required,
    'category: required'
}

'''
class ImageUploadView(APIView):
    parser_class = (FileUploadParser,)
    
    def post(self, request, *args, **kwargs):
        # try:
        room_id = kwargs.get('room_id')
        
        # Convert the image file to bytes
        image = request.data.get('image')

        # Prepare the data to send to Flask
        files = {'file': ('image.jpg', image)}

        # Send the request to ngrok on colab
        response = requests.post(f'{NGROK_URL}/predict', files=files)

        print('1')
        print(response)
        print(response.status_code)
        
        if response.status_code == 200:
            # Parse the JSON response from Flask
            flask_response = response.json()
        
            print('2')
        
            # Decode the base64-encoded model data
            model_base64 = flask_response.get('model_file')
            model_binary_data = base64.b64decode(model_base64)
        
            print('3')
        
            # Generate a filename for the model file
            model_filename = flask_response.get('model_path').split(sep='/tmp/')[-1]
            # Save the decoded model data to a file in the static files directory
            model_file_path = default_storage.save(f"objects/{model_filename}", ContentFile(model_binary_data))
        
            print('4')
            print(model_file_path)
        
            # Save the TDModel data
            # Create TDModel data
            td_model_data = {
                'name': request.data.get('name'), 
                'description': request.data.get('description'), 
                'type': request.data.get('type')
            }
            TDModel_serializer = TDModelSerializer(data=td_model_data)
            TDModel_serializer.is_valid(raise_exception=True)
            td_model = TDModel_serializer.save()

            print('5')
            # print(td_model)

            # Get or create the Category instance
            category_name = request.data.get('category')
            category, _ = Category.objects.get_or_create(name=category_name)
            
            print('6')
            print(category)

            # Get the Room instance
            room = Room.objects.get(td_model__id=room_id)
            
            print('7')
            print(room)

            # Save the Object instance
            object_data = {
                # 'td_model': td_model,
                # 'category': category,
                'room': room,
                # 'file': model_file_path,
                # 'material': model_file_path
            }

            print('8')
            # print(object_data)

            object_serializer = ObjectSerializer(data=object_data)
            print('9')
            if object_serializer.is_valid(raise_exception=True):
                print('10')
                object_instance = object_serializer.save(td_model=td_model)
                # save the image of the created object
                object_image_instance = ObjectImage.objects.create(object=object_instance, image=image)

            print('11')
            # print(object_image_instance)

            # Return the response from Flask as the response of this view
            return Response({
                'model_path': object_instance.model_file_path,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to communicate with Flask app"}, status=status.HTTP_400_BAD_REQUEST)
            # else:
            #     return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # except Exception as e:
        #     return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class hi(APIView):
    def get(self, request):
        # Send the request to ngrok on colab
        response = requests.get(f'{NGROK_URL}/hi')
        
        if response.status_code == 200:
            # Parse the JSON response from Flask
            flask_response = response.json()
        
        return Response(flask_response, status=status.HTTP_200_OK)