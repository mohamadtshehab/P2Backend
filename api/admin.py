from django.contrib import admin
from .models import *

admin.site.register([TDModel, Object, Texture, Category, Room])
# Register your models here.