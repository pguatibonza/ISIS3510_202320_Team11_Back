from django.db import models
from django.utils.translation import gettext_lazy as _

class User(models.Model):

    class UserType(models.TextChoices):
        LOADOWNER = 'LO', _('LoadOwner')
        DRIVER = 'DR',_('Driver')
        TRAILEROWNER = 'TO',_('TrailerOwner')
    
    name=models.CharField(max_length=50)
    lastName=models.CharField(max_length=50)
    email=models.EmailField(max_length=254)
    password=models.CharField(max_length=50)
    phone=models.CharField(max_length=10)
    userType=models.CharField(max_length=2,choices=UserType.choices,default=UserType.LOADOWNER)
    def __str__(self):
        return self.name + " " + self.lastName + " " + self.email + " " + self.phone + " " + self.userType