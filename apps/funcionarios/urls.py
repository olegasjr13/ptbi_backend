from django.urls import path, include
from apps.funcionarios.views.funcionario_views import FuncionarioViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'funcionarios', FuncionarioViewSet, basename='funcionario')

urlpatterns = [
    path('', include(router.urls)),
]

