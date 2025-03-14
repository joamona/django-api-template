
from django.db import connection

from rest_framework import serializers

from core.myLib.geoModelSerializer import GeoModelSerializer
from .models import Buildings
from djangoapi.settings import EPSG_FOR_GEOMETRIES, ST_SNAP_PRECISION

class BuildingsSerializer(GeoModelSerializer):
    check_geometry_is_valid = True #if true ºit will check if the geometry is valid: not self-intersecting and closed
    check_st_relation = True #if true it will chck the relation of the geometry with the other geometries
    matrix9IM = 'T********' #matrix 9IM for the relation of the geometries: 'T********' = interiors intersects
    geoms_as_wkt = True #if true the serializer expects the geometries in WKT format. If false, in geojson format
    check_st_relation = True #if the new geometry must be checked against 
            #the other geometries in the table according to the matrix9IM. If any geometry
            #has the relation with the new geometry, the new geometry is not saved
            #an a validation error is raised, with the ids of the geometries that have the relation

    class Meta:
        model = Buildings
        fields = GeoModelSerializer.Meta.fields + ['description', 'area']

    def validate_geom(self, value):
        """Validates if a geometry is valid.
            Do not do anythin special. Simple is an example of how to override the father method
        """
        print('validate_geom, child')
        return super().validate_geom(value)
        