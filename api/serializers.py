from rest_framework import serializers
from .models import *

        
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email']

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
            validated_data.pop('password')
        return super().update(instance, validated_data)
    

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