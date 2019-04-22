"""Circle model"""

#django
from django.db import models

#utilities
from cride.utils.models import CRideModel


class Circle(CRideModel):
    """Circle model

    A circle is a private group where rides are offered and taken
    by its members. To join a circle a user must receive an unique
    invitation code from an existing circle member.    
    """

    name = models.CharField('circle name', max_length=140)
    slug_name = models.SlugField(unique=True, max_length=40) #el equivalente al username del grupo, seutilizara en las urls

    about = models.CharField('circle description', max_length=255)
    picture  =models.ImageField(upload_to='circles/pictures', blank=True, null=True)

    members = models.ManyToManyField(
        'users.User',  #
        through='circles.Membership', #se especifica con que otro modelo se realizara la relacion para agregar mas fields
        through_fields=('circle', 'user') 
        #si tiene mas de una llave foranea que apuentan a un mismo campo se debe especificar por cual los une
    )


    #Stas
    rides_offered = models.PositiveIntegerField(default=0)
    rides_taken = models.PositiveIntegerField(default=0)
    
    verified = models.BooleanField(
        'verifed circle',
        default=False,
        help_text='Verified circle are also known as official cmmunities'
    )

    is_public = models.BooleanField(
        default=True, 
        help_text= 'Oublic circles are listed in the main page so everyone know about their existence'
    )

    is_limited= models.BooleanField(
        'Limited',
        default=False,
        help_text='Limited circle can grow up to a fixed number of members'
    )

    members_limit = models.PositiveIntegerField(
        default=0,
        help_text='If circle is limited, this will be the limit on the number of members'
    )

    def __str__(self):
        """Return circle name"""
        return self.name

    #se extiende de la clase meta para modificar el orden en la que se presentaran los circle
    class Meta(CRideModel.Meta): 
        """Meta class."""

        ordering = ['-rides_taken', '-rides_offered'] #el signo menos es para ordenar de manera desendente
    