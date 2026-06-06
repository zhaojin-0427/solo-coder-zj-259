from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CellarPoolViewSet, FermentationBatchViewSet, FermentationRecordViewSet,
    WineQualityViewSet, AgingStorageViewSet, AgingRecordViewSet, AgingEnvRecordViewSet,
    DisposalTaskViewSet, StatsViewSet
)

router = DefaultRouter()
router.register(r'cellar-pools', CellarPoolViewSet)
router.register(r'batches', FermentationBatchViewSet)
router.register(r'fermentation-records', FermentationRecordViewSet)
router.register(r'wine-qualities', WineQualityViewSet)
router.register(r'aging-storages', AgingStorageViewSet)
router.register(r'aging-records', AgingRecordViewSet)
router.register(r'aging-env-records', AgingEnvRecordViewSet)
router.register(r'disposal-tasks', DisposalTaskViewSet)
router.register(r'stats', StatsViewSet, basename='stats')

urlpatterns = [
    path('', include(router.urls)),
]
