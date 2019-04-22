"""Circles views"""

# Django REST Framework
from rest_framework.decorators import api_view
from rest_framework.response import Response


# Models
from cride.circles.models import Circle

#serializer
from cride.circles.serializers import CircleSerializer, CreateCircleSerializer

@api_view(['GET'])
def list_circles(request):
    """List circles"""
    circles = Circle.objects.filter(is_public=True)
    serializer = CircleSerializer(circles, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def create_circle(request):
    """Crea circle"""
    serializer = CreateCircleSerializer(data=request.data) #recibe los datos y los envia al serializer
    serializer.is_valid(raise_exception=True)
    circle = serializer.save()
    
    return Response(CircleSerializer(circle).data)
