"""Users model"""

#django
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

#utilities
from cride.utils.models import CRideModel

class User(CRideModel, AbstractUser):
    """User model
    Extend from Django's Abstract User, change the username field
    to email and add some extra fields
    """

    email = models.EmailField(
        'email address',
        unique=True,
        error_messages={
            'unique':'A user with that email already exists'
        }
    )

    phone_regex= RegexValidator(
        regex=r'\+?1?\d{9,15}', #expresion regular que validará el numero telefonico
        message="Phone number must be entered in the format: +999999999. Up to 15 digitis allowed"
    )
    phone_number = models.CharField(validators=[phone_regex],max_length=17, blank=True)

    USERNAME_FIELD='email' #asignar al campo email para pedirlo al memento de logearse
    REQUIRED_FIELDS=['username', 'first_name', 'last_name'] #se creclaran los campos requeridos al momento de crearse un usuario

    is_client = models.BooleanField(
        'client status',
        default=True,
        help_text=(
            'Help easily distinguish users and perform queries.'
            'Clients are the main type of user.'
        )
    )

    is_verified= models.BooleanField(
        'verified',
        default=False,
        help_text='Set to true when the user have verified its email address'

    )

    def __str__(self): #retorna el username
        """Return username"""
        return self.username

    def get_short_name(self): #para la version corta del nombre se retorna el username
        """Return username"""
        return self.username