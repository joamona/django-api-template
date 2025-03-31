from django.contrib import admin
from django.contrib.gis import admin
from .models import Buildings, Owners

admin.site.register(Buildings, admin.GISModelAdmin)
admin.site.register(Owners, admin.ModelAdmin)
