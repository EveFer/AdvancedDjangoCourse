"""Users views"""

#Django REST Framework
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

#Serializers 
from cride.users.serializers import (
    AccountValidatorSerializer,
    UserLoginSerializer, 
    UserModelSerializer,
    UserSignupSerializer
)

class UserLoginAPIView(APIView):
    """Users Login API view, Class-base view"""

    def post(self, request, *args, **kwargs):
        """Handle HTTP POST request"""
        serializer = UserLoginSerializer(data=request.data) 
        serializer.is_valid(raise_exception=True)
        user, token = serializer.save()
        data = {
            'user': UserModelSerializer(user).data,
            'token': token
        }
        return Response(data, status=status.HTTP_201_CREATED)

class UserSignupAPIView(APIView):
    """Users Create API View"""

    def post(self, request, *args, **kwargs):
        """Handle http post request for create user"""
        serializer = UserSignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = UserModelSerializer(user).data
        return Response(data, status=status.HTTP_201_CREATED)

class AccountVerificationAPIView(APIView):
    """Account verificacion API View"""

    def post(self, request, *args, **kwargs):
        """Handle http post request for create user"""
        serializer = AccountValidatorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = {'message':'Congratulations, now share some rides!'}
        return Response(data, status=status.HTTP_200_OK)
