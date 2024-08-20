from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class TDModel(models.Model):
    TYPE_CHOICES = [('room', 'Room'),
                    ('object', 'Object'),]
    
    name = models.CharField('3D Model Name', max_length=150)
    description = models.TextField('3D Model Description', null=True, blank=True)
    scaling = models.JSONField(default=dict(x=0.0, y=0.0, z=0.0))
    rotation = models.JSONField(default=dict(x=0.0, y=0.0, z=0.0))
    translation = models.JSONField(default=dict(x=0.0, y=0.0, z=0.0))
    color = models.JSONField(default=dict(r=0.0, g=0.0, b=0.0, a=1.0))
    type = models.CharField(choices=TYPE_CHOICES, max_length=150)
    
    def __str__(self):
        return self.name
class Category(models.Model):
    name = models.CharField('Category Name', unique=True, max_length=150)
    
    def __str__(self):
        return self.name
class Room(models.Model):
    td_model = models.OneToOneField(TDModel, on_delete=models.CASCADE, primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
class Object(models.Model):
    
    td_model = models.OneToOneField(TDModel, on_delete=models.CASCADE, primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    file = models.FilePathField()
    material = models.FilePathField()
    
    
class ObjectImage(models.Model):
    object = models.ForeignKey(Object, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='objects/images/')

class Texture(models.Model):
    name = models.CharField('Texture Name', max_length=150)
    image = models.ImageField(upload_to='textures/')
    object = models.ForeignKey(Object, on_delete=models.CASCADE)
    def __str__(self):
        return self.name
    
    

    