from django.db import models
from django.utils.translation import gettext_lazy as _
from datetime import datetime

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

class Load(models.Model):
    type=models.CharField(max_length=30)
    trailerType=models.CharField(max_length=2,choices=TrailerType.choices,default=TrailerType.ANY)
    weight=models.IntegerField()
    volume=models.IntegerField(null=True)

    def __str__(self):
        return self.type + " " + self.trailerType + " " + str(self.weight) + " " + str(self.volume)


class AccessPoint(models.Model):
    country=models.CharField(max_length=50)
    city=models.CharField(max_length=50)
    address=models.CharField(max_length=50)
    before=models.DateTimeField(default=datetime.now())
    after=models.DateTimeField(default=datetime.now())

    def __str__(self):
        return self.country + " " + self.city + " " + self.address

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