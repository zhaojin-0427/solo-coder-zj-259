from django.contrib import admin
from .models import (
    CellarPool, FermentationBatch, FermentationRecord,
    WineQuality, AgingStorage, AgingRecord, AgingEnvRecord,
    DisposalTask
)

admin.site.register(CellarPool)
admin.site.register(FermentationBatch)
admin.site.register(FermentationRecord)
admin.site.register(WineQuality)
admin.site.register(AgingStorage)
admin.site.register(AgingRecord)
admin.site.register(AgingEnvRecord)
admin.site.register(DisposalTask)
