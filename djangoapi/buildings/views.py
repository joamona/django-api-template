# Create your views here.
#Django imports
from django.http import JsonResponse
from django.views import View
from django.contrib.auth import logout
from django.shortcuts import redirect

#rest_framework imports
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import permissions

from .models import Buildings
from .serializers import BuildingsSerializer

def custom_logout_view(request):
    logout(request)
    return redirect("/accounts/login/")  # O a donde desees redirigir después del logout

class HelloWord(View):
    def get(self, request):
        return JsonResponse({"ok":True,"message": "Buildings. Hello world", "data":[]})

class BuildingsModelViewSet(viewsets.ModelViewSet):
    """
    The actions provided by the ModelViewSet class are .list(), .retrieve(), .create(), .update(), .partial_update(), and .destroy().
    """
    queryset = Buildings.objects.all()
    serializer_class = BuildingsSerializer
    permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]