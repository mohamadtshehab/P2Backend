from factory.django import DjangoModelFactory
from factory import Faker, Sequence, post_generation, lazy_attribute
import random
import json
from django.conf import settings
from django.db import transaction
from .models import Texture, Category, TDModel, Room, Object, ObjectImage
from django.contrib.auth.models import User
from django.db.models import Q


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = Sequence(lambda n: f"user{n}")
    email = Faker('email')
    first_name = Faker('first_name')
    last_name = Faker('last_name')
    is_staff = False
    is_superuser = False

    @post_generation
    def password(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.set_password(extracted)
        else:
            self.set_password('defaultpassword')


class TextureFactory(DjangoModelFactory):
    class Meta:
        model = Texture

    name = Faker('word')
    image = Faker('image_url')
    
    @lazy_attribute
    def object(self):
        all_objects = Object.objects.all()
        if len(all_objects) == 0:
            return ObjectFactory()
        return random.choice(all_objects)


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    name = Sequence(lambda n: f"Category {n}")


class TDModelFactory(DjangoModelFactory):
    class Meta:
        model = TDModel

    name = Sequence(lambda n: f"TDModel {n}")
    description = Faker('paragraph', nb_sentences=3)
    scaling = lazy_attribute(lambda _: json.dumps({'x': random.uniform(0, 1), 'y': random.uniform(0, 1), 'z': random.uniform(0, 1)}))
    rotation = lazy_attribute(lambda _: json.dumps({'x': random.uniform(0, 360), 'y': random.uniform(0, 360), 'z': random.uniform(0, 360)}))
    translation = lazy_attribute(lambda _: json.dumps({'x': random.uniform(-100, 100), 'y': random.uniform(-100, 100), 'z': random.uniform(-100, 100)}))
    color = lazy_attribute(lambda _: json.dumps({'r': random.uniform(0, 1), 'g': random.uniform(0, 1), 'b': random.uniform(0, 1), 'a': random.uniform(0, 1)}))
    type = lazy_attribute(lambda _: random.choice(['room', 'object']))


class RoomFactory(DjangoModelFactory):
    class Meta:
        model = Room

    @lazy_attribute
    def td_model(self):
        new_model = TDModel.objects.create(type='room')
        new_model.save()
        return new_model

    @lazy_attribute
    def user(self):
        all_users = User.objects.all()
        if len(all_users) == 0:
            return UserFactory()
        return random.choice(all_users)


class ObjectFactory(DjangoModelFactory):
    class Meta:
        model = Object

    @lazy_attribute
    def td_model(self):
        new_model = TDModel.objects.create(type='object')
        new_model.save()
        return new_model

    category = lazy_attribute(lambda _: CategoryFactory())

    @lazy_attribute
    def room(self):
        all_rooms = Room.objects.all()
        if len(all_rooms) == 0:
            return RoomFactory()
        return random.choice(all_rooms)

    file = Faker('image_url')
    material = Faker('image_url')


class ObjectImageFactory(DjangoModelFactory):
    class Meta:
        model = ObjectImage

    @lazy_attribute
    def object(self):
        all_objects = Object.objects.all()
        if len(all_objects) == 0:
            return ObjectFactory()
        return random.choice(all_objects)

    image = Faker('image_url')

class FactoryLauncher:

    def create_all_instances(num_users=5, num_textures=10, num_categories=5, num_tdmodels=5, num_rooms=5, num_objects=10, num_object_images=10):
        with transaction.atomic():
            users = [UserFactory() for _ in range(num_users)]
            print(f"Created {len(users)} users.")
            
            textures = [TextureFactory() for _ in range(num_textures)]
            print(f"Created {len(textures)} textures.")
            
            categories = [CategoryFactory() for _ in range(num_categories)]
            print(f"Created {len(categories)} categories.")
            
            tdmodels = [TDModelFactory() for _ in range(num_tdmodels)]
            print(f"Created {len(tdmodels)} TD models.")
            
            rooms = [RoomFactory() for _ in range(num_rooms)]
            print(f"Created {len(rooms)} rooms.")
            
            objects = [ObjectFactory() for _ in range(num_objects)]
            print(f"Created {len(objects)} objects.")
            
            object_images = [ObjectImageFactory() for _ in range(num_object_images)]
            print(f"Created {len(object_images)} object images.")