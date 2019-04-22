"""User Serializers"""

#django
from django.contrib.auth import password_validation, authenticate
from django.core.validators import RegexValidator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings

#django REST Framework
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.authtoken.models import Token

#models
from cride.users.models import User, Profile

#Utilities
from datetime import timedelta
import jwt


class UserModelSerializer(serializers.ModelSerializer):
    """User model serializer"""
    class Meta:
        """Meta class"""
        
        model=User
        fields=('username', 'first_name', 'last_name', 'email', 'phone_number')


class UserLoginSerializer(serializers.Serializer):
    """User Login serializer.

    Handle the login request data.
    """

    email= serializers.EmailField()
    password = serializers.CharField(min_length=8)

    def validate(self, data):
        """Check credentiales"""
        user = authenticate(username=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError('Invalid credentials')
        if not user.is_verified:
            raise serializers.ValidationError('Account is not activate yet D:')
        self.context['user'] = user
        return data

    def create(self, data):
        """Generate or retrieve new token"""
        token, created = Token.objects.get_or_create(user=self.context['user'])
        return self.context['user'], token.key

class UserSignupSerializer(serializers.Serializer):
    """User Create Serializer
    
    Handle Sign up data validation and user/profile creation
    """

    email= serializers.EmailField(
        validators = [UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        min_length=4,
        max_length=20,
        validators = [UniqueValidator(queryset=User.objects.all())]
    )

    phone_regex= RegexValidator(
        regex=r'\+?1?\d{9,15}', #expresion regular que validará el numero telefonico
        message="Phone number must be entered in the format: +999999999. Up to 15 digitis allowed"
    )
    phone_number = serializers.CharField(validators=[phone_regex])

    password = serializers.CharField(min_length=8)
    password_confirmation = serializers.CharField(min_length=8)

    first_name = serializers.CharField(min_length=4, max_length=30)
    last_name = serializers.CharField(min_length=4, max_length=30)

    def validate(self, data):
        """Varify password match"""
        passwd = data['password']
        passwd_conf = data['password_confirmation']
        if passwd != passwd_conf:
            raise serializers.ValidationError("Passwords don´t match.")
        password_validation.validate_password(passwd) #django puede validar el password y lanzar los errores
        return data

    def create(self, data):
        data.pop('password_confirmation')
        user = User.objects.create_user(**data, is_verified=False)
        Profile.objects.create(user=user)
        self.send_confirmation_email(user)
        return user
    
    def send_confirmation_email(self, user):
        """Send account verification link to give user."""
        verification_token = self.gen_verification_token(user)
        subject = 'Welcome @{}! Verify tour account to start using Comparte Ride'.format(user.username)
        from_email = 'Comparte Ride <noreply@comparteride.com>'
        content = render_to_string(
            'emails/users/account_verification.html', #template
            {'token': verification_token, 'user':user} #Enviar como contexto
        )
        msg = EmailMultiAlternatives(subject, content, from_email, [user.email])
        msg.attach_alternative(content, "text/html")
        msg.send()

    def gen_verification_token(self, user):
        """Create JWT token that the user can use to verify its account"""
        exp_date = timezone.now()+timedelta(days=3)
        payload = {
            'user':user.username,
            'exp':int(exp_date.timestamp()),
            'type': 'email_confirmation'
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        return token.decode()

class AccountValidatorSerializer(serializers.Serializer):
    """Account Verificación Serializer"""
    token =serializers.CharField()

    def validate_token(self, data):
        """Verify token is valid"""
        try:
            payload = jwt.decode(data, settings.SECRET_KEY, algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError('Verification link has expired')
        except jwt.PyJWTError:
            raise serializers.ValidationError('Invalid token')
        if payload['type'] != 'email_confirmation':
            raise serializers.ValidationError('Invalid token')
        
        self.context['payload'] = payload
        return data

    def save(self): #solo se sobre escribe el metodo save cuando se quiere realizar alguna otra cosa al momento de guardar
        """Update user's verified status"""
        payload = self.context['payload']
        user = User.objects.get(username=payload['user'])
        user.isverified = True
        user.save()