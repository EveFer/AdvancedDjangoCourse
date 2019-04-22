"""Circle serializers"""

#Django Rest framwork
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

#models
from cride.circles.models import Circle

class CircleSerializer(serializers.Serializer): #listar circles
    """Circle serializer"""
    name = serializers.CharField()
    slug_name = serializers.SlugField()
    rides_taken = serializers.IntegerField()
    rides_offered = serializers.IntegerField()
    members_limit = serializers.IntegerField()

class CreateCircleSerializer(serializers.Serializer): #crear circles
    """Create circle serializer"""

    name = serializers.CharField(max_length=140)
    slug_name = serializers.SlugField(
        max_length=40,
        validators=[
            UniqueValidator(queryset=Circle.objects.all())
        ]    
    )
    about = serializers.CharField(
        max_length=255,
        required=False
    )

    def create(self, data):
        """Create circle"""
        return Circle.objects.create(**data)