
from rest_framework import serializers
from .models import Owners

class OwnersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Owners
        fields = ['id', 'name', 'dni']
