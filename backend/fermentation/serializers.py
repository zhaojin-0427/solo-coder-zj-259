from rest_framework import serializers
from .models import (
    CellarPool, FermentationBatch, FermentationRecord,
    WineQuality, AgingStorage, AgingRecord, AgingEnvRecord,
    DisposalTask
)


class CellarPoolSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    active_batch = serializers.SerializerMethodField()

    class Meta:
        model = CellarPool
        fields = '__all__'

    def get_active_batch(self, obj):
        batch = obj.batches.filter(status='fermenting').first()
        if batch:
            return {'id': batch.id, 'batch_no': batch.batch_no}
        return None


class FermentationBatchSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    risk_level_display = serializers.CharField(source='get_risk_level_display', read_only=True)
    disposal_status_display = serializers.CharField(source='get_disposal_status_display', read_only=True)
    cellar_pool_code = serializers.CharField(source='cellar_pool.code', read_only=True)
    record_count = serializers.IntegerField(read_only=True)
    latest_record = serializers.SerializerMethodField()
    latest_disposal_task = serializers.SerializerMethodField()

    class Meta:
        model = FermentationBatch
        fields = '__all__'

    def get_latest_record(self, obj):
        record = obj.records.order_by('-record_time').first()
        if record:
            return FermentationRecordSerializer(record).data
        return None

    def get_latest_disposal_task(self, obj):
        task = obj.disposal_tasks.order_by('-created_at').first()
        if task:
            return DisposalTaskSerializer(task).data
        return None


class FermentationRecordSerializer(serializers.ModelSerializer):
    batch_no = serializers.CharField(source='batch.batch_no', read_only=True)

    class Meta:
        model = FermentationRecord
        fields = '__all__'


class WineQualitySerializer(serializers.ModelSerializer):
    grade_display = serializers.CharField(source='get_grade_display', read_only=True)
    batch_no = serializers.CharField(source='batch.batch_no', read_only=True)
    yield_rate = serializers.SerializerMethodField()

    class Meta:
        model = WineQuality
        fields = '__all__'

    def get_yield_rate(self, obj):
        if obj.batch.grain_total > 0:
            return round(obj.total_output / obj.batch.grain_total * 100, 2)
        return 0


class AgingStorageSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    occupancy_rate = serializers.SerializerMethodField()

    class Meta:
        model = AgingStorage
        fields = '__all__'

    def get_occupancy_rate(self, obj):
        if obj.capacity > 0:
            return round(obj.used_count / obj.capacity * 100, 2)
        return 0


class AgingRecordSerializer(serializers.ModelSerializer):
    batch_no = serializers.CharField(source='quality.batch.batch_no', read_only=True)
    storage_code = serializers.CharField(source='storage.code', read_only=True)
    loss_rate = serializers.SerializerMethodField()

    class Meta:
        model = AgingRecord
        fields = '__all__'

    def get_loss_rate(self, obj):
        if obj.initial_volume > 0:
            return round((obj.initial_volume - obj.current_volume) / obj.initial_volume * 100, 2)
        return 0


class AgingEnvRecordSerializer(serializers.ModelSerializer):
    storage_code = serializers.CharField(source='storage.code', read_only=True)

    class Meta:
        model = AgingEnvRecord
        fields = '__all__'


class DisposalTaskSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    source_display = serializers.CharField(source='get_source_display', read_only=True)
    risk_level_display = serializers.CharField(source='get_risk_level_display', read_only=True)
    batch_no = serializers.CharField(source='batch.batch_no', read_only=True, default=None)
    storage_code = serializers.CharField(source='storage.code', read_only=True, default=None)

    class Meta:
        model = DisposalTask
        fields = '__all__'
