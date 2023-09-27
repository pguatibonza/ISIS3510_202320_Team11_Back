from django.db import models
from .trailer import TrailerType

class Load(models.Model):
    type=models.CharField(max_length=30)
    trailerType=models.CharField(max_length=2,choices=TrailerType.choices,default=TrailerType.ANY)
    weight=models.IntegerField()
    volume=models.IntegerField(null=True)

    def __str__(self):
        return self.type + " " + self.trailerType + " " + str(self.weight) + " " + str(self.volume)
