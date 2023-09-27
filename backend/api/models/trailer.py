from django.db import models
from .user import User
from django.utils.translation import gettext_lazy as _

class TrailerType(models.TextChoices):
        FLATBED = 'FB', _('Flatbed')
        DRYVAN = 'DV', _('Dry Van')
        REEFER = 'RF', _('Reefer')
        LOWBOY = 'LB', _('Lowboy')
        STEPDECK = 'SD', _('Stepdeck')
        OTHER = 'OT', _('Other')
        ANY= 'AN',_('Any')


class  Trailer(models.Model):

    class TrailerStatus(models.TextChoices):
        AVAILABLE = 'AV', _('Available')
        INTRANSIT = 'IT', _('In Transit')
        UNAVAILABLE = 'UN', _('Unavailable') 
    
    plates=models.CharField(max_length=6,null=False)
    capacity=models.IntegerField()
    volume=models.IntegerField(null=True)
    pickup=models.CharField(max_length=30)
    dropoff=models.CharField(max_length=30)
    status=models.CharField(max_length=2,choices=TrailerStatus.choices,default=TrailerStatus.AVAILABLE)
    type=models.CharField(max_length=2,choices=TrailerType.choices,default=TrailerType.ANY)

    driver=models.OneToOneField(User,on_delete=models.CASCADE,related_name="TrailerAssigned",null=True)

    owner=models.ForeignKey(User,on_delete=models.CASCADE,related_name="TrailerOwner",default=None)

    def __str__(self):
        return self.plates + " " + self.type + " " + self.status