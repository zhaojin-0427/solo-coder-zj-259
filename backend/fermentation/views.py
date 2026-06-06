from django.db.models import Count, Avg, Sum, Q
from django.db.models.functions import TruncMonth
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import timedelta

from .models import (
    CellarPool, FermentationBatch, FermentationRecord,
    WineQuality, AgingStorage, AgingRecord, AgingEnvRecord
)
from .serializers import (
    CellarPoolSerializer, FermentationBatchSerializer, FermentationRecordSerializer,
    WineQualitySerializer, AgingStorageSerializer, AgingRecordSerializer, AgingEnvRecordSerializer
)


class CellarPoolViewSet(viewsets.ModelViewSet):
    queryset = CellarPool.objects.all()
    serializer_class = CellarPoolSerializer
    filterset_fields = ['status']
    search_fields = ['code', 'name', 'location']


class FermentationBatchViewSet(viewsets.ModelViewSet):
    queryset = FermentationBatch.objects.select_related('cellar_pool').annotate(
        record_count=Count('records')
    )
    serializer_class = FermentationBatchSerializer
    filterset_fields = ['status', 'cellar_pool']
    search_fields = ['batch_no']

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.cellar_pool.status = 'fermenting'
        instance.cellar_pool.save()

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        batch = self.get_object()
        batch.status = 'completed'
        from django.utils import timezone
        batch.end_date = timezone.now()
        batch.save()
        batch.cellar_pool.status = 'idle'
        batch.cellar_pool.save()
        return Response(FermentationBatchSerializer(batch).data)

    @action(detail=True, methods=['get'])
    def curve(self, request, pk=None):
        batch = self.get_object()
        records = batch.records.order_by('record_time')
        entry_time = batch.entry_date

        data = []
        for r in records:
            hours = (r.record_time - entry_time).total_seconds() / 3600
            days = round(hours / 24, 1)
            data.append({
                'day': days,
                'time': r.record_time.strftime('%Y-%m-%d %H:%M'),
                'cellar_temp': r.cellar_temp,
                'acidity': r.acidity,
                'alcohol': r.alcohol,
                'is_abnormal': r.is_abnormal,
                'abnormal_note': r.abnormal_note,
            })

        abnormal_count = records.filter(is_abnormal=True).count()
        return Response({
            'batch_no': batch.batch_no,
            'entry_date': entry_time.strftime('%Y-%m-%d %H:%M'),
            'expected_days': batch.expected_days,
            'entry_temp': batch.entry_temperature,
            'data': data,
            'abnormal_count': abnormal_count,
        })


class FermentationRecordViewSet(viewsets.ModelViewSet):
    queryset = FermentationRecord.objects.select_related('batch').all()
    serializer_class = FermentationRecordSerializer
    filterset_fields = ['batch', 'is_abnormal']

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        batch_id = data.get('batch')
        try:
            batch = FermentationBatch.objects.get(id=batch_id)
        except FermentationBatch.DoesNotExist:
            return Response({'error': '批次不存在'}, status=status.HTTP_400_BAD_REQUEST)

        cellar_temp = float(data.get('cellar_temp', 0))
        acidity = float(data.get('acidity', 0))
        alcohol = float(data.get('alcohol', 0))
        entry_temp = batch.entry_temperature

        is_abnormal = False
        notes = []

        if cellar_temp > 38 or cellar_temp < 15:
            is_abnormal = True
            notes.append(f'窖温{cellar_temp}℃异常(正常15-38℃)')
        elif cellar_temp - entry_temp > 8:
            is_abnormal = True
            notes.append(f'窖温升幅过大({round(cellar_temp - entry_temp, 1)}℃)')

        if acidity > 4.5:
            is_abnormal = True
            notes.append(f'酸度过高({acidity})')
        elif acidity < 0.5:
            is_abnormal = True
            notes.append(f'酸度过低({acidity})')

        if alcohol > 70:
            is_abnormal = True
            notes.append(f'酒度异常偏高({alcohol})')

        data['is_abnormal'] = is_abnormal
        data['abnormal_note'] = '; '.join(notes)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WineQualityViewSet(viewsets.ModelViewSet):
    queryset = WineQuality.objects.select_related('batch').all()
    serializer_class = WineQualitySerializer
    filterset_fields = ['grade']
    search_fields = ['batch__batch_no']


class AgingStorageViewSet(viewsets.ModelViewSet):
    queryset = AgingStorage.objects.all()
    serializer_class = AgingStorageSerializer
    filterset_fields = ['status', 'area']
    search_fields = ['code']


class AgingRecordViewSet(viewsets.ModelViewSet):
    queryset = AgingRecord.objects.select_related('quality', 'storage').all()
    serializer_class = AgingRecordSerializer
    filterset_fields = ['storage', 'is_active']
    search_fields = ['quality__batch__batch_no']

    def perform_create(self, serializer):
        instance = serializer.save()
        storage = instance.storage
        storage.used_count += instance.container_count
        storage.save()

    @action(detail=True, methods=['post'])
    def finish(self, request, pk=None):
        record = self.get_object()
        record.is_active = False
        from django.utils import timezone
        record.end_date = timezone.now().date()
        record.save()
        storage = record.storage
        storage.used_count -= record.container_count
        if storage.used_count < 0:
            storage.used_count = 0
        storage.save()
        return Response(AgingRecordSerializer(record).data)


class AgingEnvRecordViewSet(viewsets.ModelViewSet):
    queryset = AgingEnvRecord.objects.select_related('storage').all()
    serializer_class = AgingEnvRecordSerializer
    filterset_fields = ['storage', 'is_abnormal']

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        storage_id = data.get('storage')
        try:
            storage = AgingStorage.objects.get(id=storage_id)
        except AgingStorage.DoesNotExist:
            return Response({'error': '库位不存在'}, status=status.HTTP_400_BAD_REQUEST)

        temperature = float(data.get('temperature', 0))
        humidity = float(data.get('humidity', 0))
        is_abnormal = False
        notes = []

        if storage.temperature_req:
            if abs(temperature - storage.temperature_req) > 3:
                is_abnormal = True
                notes.append(f'温度偏离要求(要求{storage.temperature_req}℃)')
        else:
            if temperature > 28 or temperature < 8:
                is_abnormal = True
                notes.append(f'温度异常({temperature}℃)')

        if storage.humidity_req:
            if abs(humidity - storage.humidity_req) > 10:
                is_abnormal = True
                notes.append(f'湿度偏离要求(要求{storage.humidity_req}%)')
        else:
            if humidity > 85 or humidity < 40:
                is_abnormal = True
                notes.append(f'湿度异常({humidity}%)')

        data['is_abnormal'] = is_abnormal
        data['notes'] = '; '.join(notes)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class StatsViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['get'])
    def overview(self, request):
        total_pools = CellarPool.objects.count()
        fermenting_pools = CellarPool.objects.filter(status='fermenting').count()
        idle_pools = CellarPool.objects.filter(status='idle').count()

        total_batches = FermentationBatch.objects.count()
        completed_batches = FermentationBatch.objects.filter(status='completed').count()
        fermenting_batches = FermentationBatch.objects.filter(status='fermenting').count()

        qualities = WineQuality.objects.all()
        total_quality = qualities.count()
        total_output = qualities.aggregate(Sum('total_output'))['total_output__sum'] or 0
        premium_count = qualities.filter(grade='premium').count()
        premium_rate = round(premium_count / total_quality * 100, 2) if total_quality > 0 else 0

        total_storages = AgingStorage.objects.count()
        active_aging = AgingRecord.objects.filter(is_active=True).count()

        return Response({
            'cellar_pools': {
                'total': total_pools,
                'fermenting': fermenting_pools,
                'idle': idle_pools,
            },
            'batches': {
                'total': total_batches,
                'completed': completed_batches,
                'fermenting': fermenting_batches,
            },
            'wine_quality': {
                'total': total_quality,
                'total_output': round(total_output, 2),
                'premium_count': premium_count,
                'premium_rate': premium_rate,
            },
            'aging': {
                'total_storages': total_storages,
                'active_aging': active_aging,
            },
        })

    @action(detail=False, methods=['get'])
    def yield_rate(self, request):
        qualities = WineQuality.objects.select_related('batch').all().order_by('produce_date')
        data = []
        for q in qualities:
            if q.batch.grain_total > 0:
                rate = round(q.total_output / q.batch.grain_total * 100, 2)
            else:
                rate = 0
            data.append({
                'batch_no': q.batch.batch_no,
                'date': q.produce_date.strftime('%Y-%m-%d'),
                'grain': q.batch.grain_total,
                'output': q.total_output,
                'yield_rate': rate,
                'grade': q.get_grade_display(),
            })

        avg_rate = round(sum(d['yield_rate'] for d in data) / len(data), 2) if data else 0
        return Response({
            'average_yield_rate': avg_rate,
            'list': data,
        })

    @action(detail=False, methods=['get'])
    def grade_distribution(self, request):
        qualities = WineQuality.objects.all()
        total = qualities.count()
        grades = ['premium', 'grade1', 'grade2', 'substandard']
        grade_labels = ['优级', '一级', '二级', '不合格']
        data = []
        for g, label in zip(grades, grade_labels):
            count = qualities.filter(grade=g).count()
            data.append({
                'grade': g,
                'label': label,
                'count': count,
                'percentage': round(count / total * 100, 2) if total > 0 else 0,
            })
        return Response(data)

    @action(detail=False, methods=['get'])
    def fermentation_cycle(self, request):
        completed = FermentationBatch.objects.filter(
            status='completed', end_date__isnull=False
        )
        cycles = []
        yeast_stats = {}
        for b in completed:
            days = (b.end_date - b.entry_date).days
            cycles.append({
                'batch_no': b.batch_no,
                'yeast_type': b.yeast_type,
                'expected_days': b.expected_days,
                'actual_days': days,
                'diff': days - b.expected_days,
            })
            if b.yeast_type not in yeast_stats:
                yeast_stats[b.yeast_type] = []
            yeast_stats[b.yeast_type].append(days)

        yeast_avg = []
        for yeast, days_list in yeast_stats.items():
            yeast_avg.append({
                'yeast_type': yeast,
                'count': len(days_list),
                'avg_days': round(sum(days_list) / len(days_list), 1),
            })

        avg_cycle = round(sum(c['actual_days'] for c in cycles) / len(cycles), 1) if cycles else 0
        return Response({
            'average_cycle_days': avg_cycle,
            'cycles': cycles,
            'by_yeast': yeast_avg,
        })

    @action(detail=False, methods=['get'])
    def aging_loss(self, request):
        records = AgingRecord.objects.filter(initial_volume__gt=0)
        data = []
        for r in records:
            loss_rate = round((r.initial_volume - r.current_volume) / r.initial_volume * 100, 2)
            aging_days = None
            if r.end_date:
                aging_days = (r.end_date - r.start_date).days
            data.append({
                'batch_no': r.quality.batch.batch_no,
                'storage': r.storage.code,
                'start_date': r.start_date.strftime('%Y-%m-%d'),
                'end_date': r.end_date.strftime('%Y-%m-%d') if r.end_date else None,
                'aging_days': aging_days,
                'initial_volume': r.initial_volume,
                'current_volume': r.current_volume,
                'loss_rate': loss_rate,
                'is_active': r.is_active,
            })

        total_initial = sum(d['initial_volume'] for d in data)
        total_current = sum(d['current_volume'] for d in data)
        overall_loss = round((total_initial - total_current) / total_initial * 100, 2) if total_initial > 0 else 0

        return Response({
            'overall_loss_rate': overall_loss,
            'list': data,
        })

    @action(detail=False, methods=['get'])
    def monthly_output(self, request):
        qualities = WineQuality.objects.annotate(
            month=TruncMonth('produce_date')
        ).values('month').annotate(
            output=Sum('total_output'),
            batch_count=Count('id')
        ).order_by('month')

        data = []
        for q in qualities:
            data.append({
                'month': q['month'].strftime('%Y-%m') if q['month'] else None,
                'output': round(q['output'], 2),
                'batch_count': q['batch_count'],
            })
        return Response(data)
