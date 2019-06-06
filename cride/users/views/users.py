"""Users views"""

#Django REST Framework
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

# Permisions
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)
from cride.users.permissions import IsAccountOwner

#Serializers 
from cride.users.serializers.profiles import ProfileModelSerializer
from cride.circles.serializers import CircleModelSerializer
from cride.users.serializers import (
    AccountValidatorSerializer,
    UserLoginSerializer, 
    UserModelSerializer,
    UserSignupSerializer
)



#models
from cride.users.models import User
from cride.circles.models import Circle

class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """User view set
    
    Handle sign up, login and account verification
    """

    #se obtiene el detalle de un usurio
    queryset = User.objects.filter(is_active=True, is_client=True)
    serializer_class = UserModelSerializer
    lookup_field='username'


    def get_permissions(self): #esta funcion se sobreescribe, con el fin de otorgar los permisos de que solo el usuario puede ver su detalle nadie mas
        """Assing permissions based on action"""
        if self.action in ['signup', 'login', 'verify']: # si el action se encuentran en una de estas lo podra realizar cualquiera
            permissions = [AllowAny]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            permissions = [IsAuthenticated, IsAccountOwner]
        else:
            permissions = [IsAuthenticated]
        return [permission() for permission in permissions]


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

    @action(detail=True, methods=['put', 'patch'])
    def profile(self, request, *args, **kwargs): #este es para poder modificar le profile
        """Update profile data"""
        user = self.get_object()
        profile = user.profile
        partial = request.method == 'PATCH'
        serializer = ProfileModelSerializer(
            profile,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = UserModelSerializer(user).data # por que se utiliza el usermodelserializer, porque se hara se este serializer tenga un campo de profile
        return Response(data)

    #esta funcion logrará mostrar los circulos de los cuales es miembro en los detalles de un usuario
    def retrieve(self, request, *args, **kwargs):
        """Add extra data to the response"""
        response = super(UserViewSet, self).retrieve(request, *args, **kwargs) #se obtiene el repsonse
        circles = Circle.objects.filter( #se obtinen los ciculos a los cuales es miembro el usuario
            members = request.user,
            membership__is_active=True
        )
        data = { #se modifica el data
            'user': response.data,
            'circles':CircleModelSerializer(circles, many=True).data
        }
        response.data = data 
        return response
