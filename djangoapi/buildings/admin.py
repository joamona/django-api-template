from django.contrib import admin
from django.contrib.gis import admin
from .models import Buildings

admin.site.register(Buildings, admin.GISModelAdmin)

