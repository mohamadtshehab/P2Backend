from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('objects/<int:pk>', views.ObjectView.as_view(), name='object_detail'),
    path('objects', views.ObjectListView.as_view(), name='object_list'),
]