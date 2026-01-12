from django.contrib import admin
from django.contrib.gis import admin
from .models import Buildings, Owners, BuildingsOwners

admin.site.register(Owners, admin.ModelAdmin)
admin.site.register(Buildings, admin.GISModelAdmin)
admin.site.register(BuildingsOwners, admin.ModelAdmin)
