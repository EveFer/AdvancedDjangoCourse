"""Profile model"""

#django
from django.db import models

#utilities
from cride.utils.models import CRideModel

class Profile(CRideModel):
    """Profile model

    A profile holds a user's public data like biography, picture, ans statistics
    """

    user = models.OneToOneField('users.User', on_delete=models.CASCADE)

    picture = models.ImageField(
        'profile picture',
        upload_to='users/pictures/',
        blank=True, #No es requerido este valor y puede quedar como valor sin caracter
        null=True   #EL valor por default de una imagen no hay sino que es nulo
    )
    biography=models.TextField(max_length=500, blank=True)

    #Stats
    rides_taken=models.PositiveIntegerField(default=0)
    rides_offered=models.PositiveIntegerField(default=0)
    reputation=models.FloatField(
        default=5.0,
        help_text="User's reputacion based on the rides taken and offered"
    )

    def __str__(self):
        """Return user's str representation"""
        return str(self.user)