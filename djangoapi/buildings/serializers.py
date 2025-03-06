
from django.db import connection

from rest_framework import serializers

from core.myLib.geoModelSerializer import GeoModelSerializer
from .models import Buildings
from djangoapi.settings import EPSG_FOR_GEOMETRIES, ST_SNAP_PRECISION

class BuildingsSerializer(GeoModelSerializer):
    check_st_relation = True
    geoms_as_wkt = False
    class Meta:
        model = Buildings
        fields = ['id', 'description', 'area', 'geom', 'geom_geojson', 'geom_wkt']

    def validate_geom(self, value):
        """Validates if a geometry in geojson is valid."""
        print('validate_geom, child')
        return super().validate_geom(value)
        