"""Memberships Model"""

# django
from django.db import models

# utilities
from cride.utils.models import CRideModel

class Membership(CRideModel):
    """Membership model
    
    A membership is the table that holds the relationship between
    a user and a circle
    """

    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    profile = models.ForeignKey('users.Profile', on_delete=models.CASCADE)
    circle = models.ForeignKey('circles.Circle', on_delete=models.CASCADE)

    is_admin = models.BooleanField(
        'circle admin',
        default = False,
        help_text="Circle admins can update the circle's data and manage its members"
    )

    # Invitations
    used_invitatios= models.PositiveSmallIntegerField(default=0)#cuantas invitaciones ha usuado
    remaining_invitation = models.PositiveSmallIntegerField(default=0) #cuantas invitaciones le quedan
    invited_by = models.ForeignKey(
        'users.User',
        null=True, # puede que nadie te haya invitado
        on_delete = models.SET_NULL, # si se borra quien ha invitado no borre nada
        related_name='ivited_by' #cuando se tiene un mismo campo referenciado a una tabla se debe colocar este atributo y colocar como lo vamos a indentificar
    )

    # Stats
    rides_taken = models.PositiveIntegerField(default=0)
    rides_offered = models.PositiveIntegerField(default=0)

    # Status
    #para verificar si el el usuario aun es miembro del circulo para no tener que borrar al usuario del membership
    is_active = models.BooleanField(
        'active status',
        default = True,
        help_text = 'Onlu activate users are allowed to interact in the circle.'
    )

    def __str__(self):
        """Return username and circle"""
        return '@{} at #{}'. format(
            self.user.username,
            self.circle.slug_name
        )

