from rest_framework import serializers
from .models import *

        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class TextureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Texture
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class TDModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = TDModel
        fields = '__all__'
        
class RoomSerializer(serializers.ModelSerializer):
    td_model = TDModelSerializer()
    class Meta:
        model = Room
        fields = '__all__'
        
class ObjectImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjectImage
        fields = '__all__'
        
class ObjectSerializer(serializers.ModelSerializer):
    textures = TextureSerializer(many=True)
    td_model = TDModelSerializer()
    class Meta:
        model = Object
        fields = '__all__'