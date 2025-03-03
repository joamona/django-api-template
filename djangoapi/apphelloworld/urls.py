from django.urls import path
from apphelloworld import views
urlpatterns = [
    path("hello_world/", views.HelloWord.as_view(),name="hello_world"),
]