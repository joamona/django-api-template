from django.urls import path, include
from . import views
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'buildings', views.BuildingsModelViewSet)

urlpatterns = [
    path("hello_world/", views.HelloWord.as_view(),name="hello_world"),
    path('', include(router.urls)),
]