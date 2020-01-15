"""Rides URLs"""

#Django
from django.urls import path, include

#django REST Framework
from rest_framework.routers import DefaultRouter

#Views
from .views import rides as ride_view



router = DefaultRouter()
router.register(r'circles/(?P<slug_name>[-a-zA-Z0-9_]+)/rides',
    ride_view.RideViewSet,
    basename='ride'
)


urlpatterns = [
    
    path('', include(router.urls))
]
