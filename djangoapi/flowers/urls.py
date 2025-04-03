from django.urls import path, include
from . import views

urlpatterns = [
    path("hello_world/", views.HelloWord.as_view(),name="hello_world"),
]