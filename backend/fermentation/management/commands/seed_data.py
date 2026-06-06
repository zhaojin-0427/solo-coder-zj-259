from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, date
import random

from fermentation.models import (
    CellarPool, FermentationBatch, FermentationRecord,
    WineQuality, AgingStorage, AgingRecord, AgingEnvRecord
)


class Command(BaseCommand):
    help = '初始化示例数据'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化数据...')

        CellarPool.objects.all().delete()
        FermentationBatch.objects.all().delete()
        FermentationRecord.objects.all().delete()
        WineQuality.objects.all().delete()
        AgingStorage.objects.all().delete()
        AgingRecord.objects.all().delete()
        AgingEnvRecord.objects.all().delete()

        pools_data = [
            {'code': 'JC-001', 'name': '老窖一号', 'location': 'A区一排1号', 'volume': 5000, 'status': 'idle', 'built_year': 1985},
            {'code': 'JC-002', 'name': '老窖二号', 'location': 'A区一排2号', 'volume': 5000, 'status': 'fermenting', 'built_year': 1988},
            {'code': 'JC-003', 'name': '老窖三号', 'location': 'A区一排3号', 'volume': 5000, 'status': 'idle', 'built_year': 1990},
            {'code': 'JC-004', 'name': '新窖一号', 'location': 'B区二排1号', 'volume': 4000, 'status': 'fermenting', 'built_year': 2015},
            {'code': 'JC-005', 'name': '新窖二号', 'location': 'B区二排2号', 'volume': 4000, 'status': 'cleaning', 'built_year': 2018},
            {'code': 'JC-006', 'name': '新窖三号', 'location': 'B区二排3号', 'volume': 4000, 'status': 'idle', 'built_year': 2020},
        ]
        pools = []
        for d in pools_data:
            pool = CellarPool.objects.create(**d)
            pools.append(pool)

        yeast_types = ['高温大曲', '中温大曲', '低温大曲', '麸曲']
        now = timezone.now()

        batches_data = []
        for i in range(8):
            pool = pools[i % len(pools)]
            batch_status = 'completed' if i < 6 else 'fermenting'
            entry_date = now - timedelta(days=60 + i * 15)
            end_date = entry_date + timedelta(days=random.randint(28, 40)) if batch_status == 'completed' else None

            batch = FermentationBatch.objects.create(
                batch_no=f'FJ2026{i + 1:03d}',
                cellar_pool=pool,
                grain_ratio={'高粱': random.randint(50, 70), '小麦': random.randint(15, 30), '玉米': random.randint(5, 20)},
                grain_total=random.randint(3000, 4500),
                yeast_type=random.choice(yeast_types),
                yeast_amount=random.randint(150, 300),
                entry_temperature=round(random.uniform(18, 26), 1),
                entry_date=entry_date,
                expected_days=30,
                status=batch_status,
                end_date=end_date,
                notes='示例数据'
            )
            batches_data.append(batch)

            if batch_status == 'completed':
                pool.status = 'idle'
                pool.save()
            else:
                pool.status = 'fermenting'
                pool.save()

        for batch in batches_data:
            days_count = 20 if batch.status == 'fermenting' else (batch.end_date - batch.entry_date).days
            for day in range(1, days_count + 1):
                record_time = batch.entry_date + timedelta(days=day, hours=random.randint(8, 18))
                cellar_temp = round(batch.entry_temperature + random.uniform(2, 12), 1)
                if day > days_count * 0.7:
                    cellar_temp = round(cellar_temp - random.uniform(1, 5), 1)
                cellar_temp = max(15, min(40, cellar_temp))
                acidity = round(random.uniform(0.8, 3.8), 2)
                alcohol = round(min(day * 0.6 + random.uniform(-0.5, 0.5), 62), 1)

                is_abnormal = False
                abnormal_note = ''
                if random.random() < 0.08:
                    cellar_temp = round(random.uniform(12, 14.5), 1)
                    is_abnormal = True
                    abnormal_note = f'窖温{cellar_temp}℃异常(正常15-38℃)'

                FermentationRecord.objects.create(
                    batch=batch,
                    record_time=record_time,
                    cellar_temp=cellar_temp,
                    acidity=acidity,
                    alcohol=alcohol,
                    ambient_temp=round(random.uniform(18, 28), 1),
                    ambient_humidity=round(random.uniform(55, 75), 1),
                    operator=random.choice(['张师傅', '李师傅', '王师傅']),
                    is_abnormal=is_abnormal,
                    abnormal_note=abnormal_note,
                )

        grades = ['premium', 'premium', 'grade1', 'grade1', 'grade2', 'substandard']
        completed_batches = [b for b in batches_data if b.status == 'completed']
        for idx, batch in enumerate(completed_batches):
            grade = grades[idx % len(grades)]
            output = round(batch.grain_total * random.uniform(0.35, 0.55), 2)
            quality = WineQuality.objects.create(
                batch=batch,
                produce_date=batch.end_date.date(),
                total_output=output,
                grade=grade,
                alcohol_content=round(random.uniform(52, 65), 1),
                acidity=round(random.uniform(1.0, 3.0), 2),
                ester=round(random.uniform(2.0, 5.0), 2),
                sensory_score=round(random.uniform(75, 98), 1),
                tasting_notes='酒体醇厚，窖香浓郁，绵甜爽净' if grade in ['premium', 'grade1'] else '口感一般，香气稍弱',
            )

        storages_data = [
            {'code': 'CL-A-01', 'area': '地下酒窖A区', 'row': '1排', 'shelf': '1架', 'capacity': 50, 'temperature_req': 15, 'humidity_req': 70},
            {'code': 'CL-A-02', 'area': '地下酒窖A区', 'row': '1排', 'shelf': '2架', 'capacity': 50, 'temperature_req': 15, 'humidity_req': 70},
            {'code': 'CL-A-03', 'area': '地下酒窖A区', 'row': '2排', 'shelf': '1架', 'capacity': 40, 'temperature_req': 16, 'humidity_req': 68},
            {'code': 'CL-B-01', 'area': '陶坛库B区', 'row': '1排', 'shelf': '1架', 'capacity': 80, 'temperature_req': 18, 'humidity_req': 65},
            {'code': 'CL-B-02', 'area': '陶坛库B区', 'row': '2排', 'shelf': '1架', 'capacity': 80, 'temperature_req': 18, 'humidity_req': 65},
            {'code': 'CL-C-01', 'area': '精品酒库C区', 'row': 'VIP-1', 'shelf': '专属', 'capacity': 20, 'temperature_req': 14, 'humidity_req': 72},
        ]
        storages = []
        for d in storages_data:
            storage = AgingStorage.objects.create(**d)
            storages.append(storage)

        qualities = WineQuality.objects.all()
        for idx, q in enumerate(qualities):
            storage = storages[idx % len(storages)]
            is_active = random.random() < 0.7
            start_date = q.produce_date + timedelta(days=random.randint(1, 10))
            initial_vol = round(q.total_output * 0.9, 2)
            end_date = None
            current_vol = initial_vol
            if not is_active:
                end_date = start_date + timedelta(days=random.randint(90, 720))
                current_vol = round(initial_vol * (1 - random.uniform(0.02, 0.12)), 2)

            container_count = random.randint(5, 20)
            AgingRecord.objects.create(
                quality=q,
                storage=storage,
                start_date=start_date,
                expected_end_date=start_date + timedelta(days=365 * random.randint(1, 5)),
                end_date=end_date,
                initial_volume=initial_vol,
                current_volume=current_vol,
                container_count=container_count,
                is_active=is_active,
            )

            if is_active:
                storage.used_count += container_count
                storage.save()

        for storage in storages:
            for i in range(15):
                record_time = now - timedelta(days=i, hours=random.randint(6, 20))
                base_temp = storage.temperature_req or 16
                base_hum = storage.humidity_req or 68
                temp = round(base_temp + random.uniform(-2, 2), 1)
                hum = round(base_hum + random.uniform(-5, 5), 1)

                is_abnormal = False
                notes = ''
                if random.random() < 0.05:
                    temp = round(base_temp + random.choice([-5, 5]), 1)
                    is_abnormal = True
                    notes = f'温度偏离要求(要求{base_temp}℃)'

                AgingEnvRecord.objects.create(
                    storage=storage,
                    record_time=record_time,
                    temperature=temp,
                    humidity=hum,
                    operator=random.choice(['管理员A', '管理员B']),
                    is_abnormal=is_abnormal,
                    notes=notes,
                )

        self.stdout.write(self.style.SUCCESS('数据初始化完成！'))
        self.stdout.write(f'窖池: {CellarPool.objects.count()} 个')
        self.stdout.write(f'发酵批次: {FermentationBatch.objects.count()} 个')
        self.stdout.write(f'发酵记录: {FermentationRecord.objects.count()} 条')
        self.stdout.write(f'酒质登记: {WineQuality.objects.count()} 条')
        self.stdout.write(f'陈酿库位: {AgingStorage.objects.count()} 个')
        self.stdout.write(f'陈酿记录: {AgingRecord.objects.count()} 条')
