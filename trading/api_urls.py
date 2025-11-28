from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'camarilla', views.CamarillaLevelViewSet, basename='camarilla')
router.register(r'whole-number', views.WholeNumberStockViewSet, basename='whole-number')
router.register(r'logs', views.ScriptRunLogViewSet, basename='logs')

urlpatterns = [
    path('', include(router.urls)),
]