#Django imports
from django.http import JsonResponse
from django.views import View
from django.contrib.auth import logout
from django.shortcuts import redirect

#rest_framework imports
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import permissions


def custom_logout_view(request):
    logout(request)
    return redirect("/accounts/login/")  # O a donde desees redirigir después del logout

class HelloWord(View):
    def get(self, request):
        return JsonResponse({"ok":True,"message": "Core. Hello world", "data":[]})

