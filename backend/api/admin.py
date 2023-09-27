from django.contrib import admin
from .models.trailer import Trailer
from .models.user import User
from .models.load import Load
from .models.accespoint import AccessPoint
from .models.trip import Trip


admin.site.register(Trailer)
admin.site.register(User)
admin.site.register(Load)
admin.site.register(AccessPoint)
admin.site.register(Trip)

