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
    
    def create(self, validated_data):
        td_model_data = validated_data.pop('td_model')
        td_model, created = TDModel.objects.get_or_create(**td_model_data)
        room = Room.objects.create(td_model=td_model, **validated_data)
        return room
        
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
    
    def create(self, validated_data):
        td_model_data = validated_data.pop('td_model')
        td_model, created = TDModel.objects.get_or_create(**td_model_data)
        object = Object.objects.create(td_model=td_model, **validated_data)
        return object