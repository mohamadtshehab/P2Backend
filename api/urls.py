from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('objects/<int:pk>', views.ObjectView.as_view(), name='object_detail'),
    path('objects', views.ObjectListView.as_view(), name='object_list'),
    path('users/<int:userId>/rooms', views.UserRoomListView.as_view(), name='user_room_list'),
    path('rooms/<int:roomId>/objects', views.RoomObjectListView.as_view(), name='room_object_list'),
    path('users/<int:userId>', views.UserView.as_view(), name='user_detail'),
    path('users', views.UserListView.as_view(), name='user_list'),
    path('objects/<int:objectId>/images', views.ObjectImageListView.as_view(), name='object_image_list'),
    path('rooms', views.RoomListView.as_view(), name='room_list'),
    path('objects/<int:objectId>/textures', views.ObjectTextureListView.as_view(), name='object_texture_list'),
    path('textures', view=views.TextureListView.as_view(), name='texture_list'),
    path('rooms/<int:roomId>', view=views.RoomView.as_view(), name='room_view'),
    path('rooms/<int:roomId>/predict', view=views.ImageUploadView.as_view(), name='predict')
]