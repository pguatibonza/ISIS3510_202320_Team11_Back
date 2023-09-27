from django.db import models
from datetime import datetime

class AccessPoint(models.Model):
    country=models.CharField(max_length=50)
    city=models.CharField(max_length=50)
    address=models.CharField(max_length=50)
    before=models.DateTimeField(default=datetime.now())
    after=models.DateTimeField(default=datetime.now())

    def __str__(self):
        return self.country + " " + self.city + " " + self.address

