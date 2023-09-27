from django.db import models 
from .load import Load
from .trailer import Trailer
from .user import User
from .accespoint import AccessPoint

from django.utils.translation import gettext_lazy as _

class Trip(models.Model):
    class Status(models.TextChoices):
        DELIVERED='DE',_('Delivered')
        INPROGESS='IP',_('In Progress')
        TOASSIGN='TA',_('To Assign')
        CANCELLED='CA',_('Cancelled')

    loadOwner=models.ForeignKey(User,on_delete=models.CASCADE,default=None)
    trailer=models.ForeignKey(Trailer,on_delete=models.CASCADE,default=None)
    load=models.ForeignKey(Load,on_delete=models.CASCADE,default=None)
    pickup=models.ForeignKey(AccessPoint,on_delete=models.CASCADE,related_name='pickup',default=None)
    dropoff=models.ForeignKey(AccessPoint,on_delete=models.CASCADE,related_name='dropoff',default=None)
    status=models.CharField(max_length=2,choices=Status.choices,default=Status.TOASSIGN)