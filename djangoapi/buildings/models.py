from django.db import models
from django.contrib.gis.db import models as gis_models
# Create your models here.
class Buildings(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=100, blank=True)
    area = models.FloatField(blank=True)
    geom = gis_models.PolygonField(srid=25830)
#    def __str__(self):
#        return str(self.id)
