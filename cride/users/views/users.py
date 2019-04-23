"""Users views"""

#Django REST Framework
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

#Serializers 
from cride.users.serializers import (
    AccountValidatorSerializer,
    UserLoginSerializer, 
    UserModelSerializer,
    UserSignupSerializer
)

class UserViewSet(viewsets.GenericViewSet):
    """User view set
    
    Handle sign up, login and account verification
    """

    @action(detail=False, methods=['post']) #para personalizar viewssets
    def login(self, request): #el nombre de la funcion sera el que se pondra en la url (localhost:8000/users/login/)
        """user sign in"""
        serializer = UserLoginSerializer(data=request.data) 
        serializer.is_valid(raise_exception=True)
        user, token = serializer.save()
        data = {
            'user': UserModelSerializer(user).data,
            'token': token
        }
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def signup(self, request):
        """User Sign up"""
        serializer = UserSignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = UserModelSerializer(user).data
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def verify(self, request):
        """Account verification"""
        serializer = AccountValidatorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = {'message':'Congratulations, now share some rides!'}
        return Response(data, status=status.HTTP_200_OK)
