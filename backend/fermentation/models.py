from django.db import models


class CellarPool(models.Model):
    STATUS_CHOICES = [
        ('idle', '空闲'),
        ('fermenting', '发酵中'),
        ('cleaning', '清洁中'),
        ('maintenance', '维护中'),
    ]
    code = models.CharField('窖池编号', max_length=50, unique=True)
    name = models.CharField('窖池名称', max_length=100, blank=True)
    location = models.CharField('位置', max_length=200, blank=True)
    volume = models.FloatField('容量(kg)', default=0)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='idle')
    built_year = models.IntegerField('建造年份', null=True, blank=True)
    notes = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'cellar_pool'
        ordering = ['code']

    def __str__(self):
        return self.code


class FermentationBatch(models.Model):
    STATUS_CHOICES = [
        ('fermenting', '发酵中'),
        ('completed', '已出酒'),
        ('aborted', '已终止'),
    ]
    RISK_LEVEL_CHOICES = [
        ('none', '无风险'),
        ('low', '低风险'),
        ('medium', '中风险'),
        ('high', '高风险'),
    ]
    DISPOSAL_STATUS_CHOICES = [
        ('none', '无需处置'),
        ('pending', '待处置'),
        ('processing', '处置中'),
        ('completed', '已处置待复核'),
        ('reviewed', '复核通过'),
        ('returned', '复核退回'),
    ]
    batch_no = models.CharField('批次号', max_length=50, unique=True)
    cellar_pool = models.ForeignKey(CellarPool, on_delete=models.PROTECT, related_name='batches', verbose_name='窖池')
    grain_ratio = models.JSONField('粮食配比', default=dict, help_text='如: {"高粱": 60, "小麦": 30, "玉米": 10}')
    grain_total = models.FloatField('粮食总重量(kg)', default=0)
    yeast_type = models.CharField('酒曲类型', max_length=100)
    yeast_amount = models.FloatField('酒曲用量(kg)', default=0)
    entry_temperature = models.FloatField('入窖温度(℃)')
    entry_date = models.DateTimeField('入窖时间')
    expected_days = models.IntegerField('预计发酵天数', default=30)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='fermenting')
    end_date = models.DateTimeField('出窖时间', null=True, blank=True)
    risk_level = models.CharField('风险等级', max_length=20, choices=RISK_LEVEL_CHOICES, default='none')
    disposal_status = models.CharField('处置状态', max_length=20, choices=DISPOSAL_STATUS_CHOICES, default='none')
    responsible_person = models.CharField('责任人', max_length=50, blank=True)
    disposal_note = models.TextField('处置说明', blank=True)
    review_time = models.DateTimeField('复核时间', null=True, blank=True)
    notes = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'fermentation_batch'
        ordering = ['-entry_date']

    def __str__(self):
        return self.batch_no


class FermentationRecord(models.Model):
    batch = models.ForeignKey(FermentationBatch, on_delete=models.CASCADE, related_name='records', verbose_name='批次')
    record_time = models.DateTimeField('检测时间')
    cellar_temp = models.FloatField('窖温(℃)')
    acidity = models.FloatField('酸度')
    alcohol = models.FloatField('酒度(度)')
    ambient_temp = models.FloatField('环境温度(℃)', null=True, blank=True)
    ambient_humidity = models.FloatField('环境湿度(%)', null=True, blank=True)
    operator = models.CharField('检测人', max_length=50, blank=True)
    is_abnormal = models.BooleanField('是否异常', default=False)
    abnormal_note = models.CharField('异常说明', max_length=200, blank=True)
    notes = models.TextField('备注', blank=True)

    class Meta:
        db_table = 'fermentation_record'
        ordering = ['-record_time']

    def __str__(self):
        return f'{self.batch.batch_no} - {self.record_time}'


class WineQuality(models.Model):
    GRADE_CHOICES = [
        ('premium', '优级'),
        ('grade1', '一级'),
        ('grade2', '二级'),
        ('substandard', '不合格'),
    ]
    batch = models.OneToOneField(FermentationBatch, on_delete=models.CASCADE, related_name='quality', verbose_name='批次')
    produce_date = models.DateField('出酒日期')
    total_output = models.FloatField('出酒总量(kg)')
    grade = models.CharField('酒质等级', max_length=20, choices=GRADE_CHOICES)
    alcohol_content = models.FloatField('酒精度(度)')
    acidity = models.FloatField('总酸(g/L)')
    ester = models.FloatField('总酯(g/L)')
    sensory_score = models.FloatField('感官评分', default=0)
    storage_location = models.CharField('陈酿位置', max_length=200, blank=True)
    tasting_notes = models.TextField('品鉴记录', blank=True)
    notes = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'wine_quality'
        ordering = ['-produce_date']

    def __str__(self):
        return f'{self.batch.batch_no} - {self.get_grade_display()}'


class AgingStorage(models.Model):
    STATUS_CHOICES = [
        ('aging', '陈酿中'),
        ('bottled', '已装瓶'),
        ('sold', '已出库'),
    ]
    code = models.CharField('库位编号', max_length=50, unique=True)
    area = models.CharField('库区', max_length=100)
    row = models.CharField('排号', max_length=20, blank=True)
    shelf = models.CharField('架号', max_length=20, blank=True)
    capacity = models.IntegerField('最大容量(坛)', default=0)
    used_count = models.IntegerField('已用数量', default=0)
    temperature_req = models.FloatField('要求温度(℃)', null=True, blank=True)
    humidity_req = models.FloatField('要求湿度(%)', null=True, blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='aging')
    notes = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'aging_storage'
        ordering = ['code']

    def __str__(self):
        return self.code


class AgingRecord(models.Model):
    quality = models.ForeignKey(WineQuality, on_delete=models.CASCADE, related_name='aging_records', verbose_name='酒质批次')
    storage = models.ForeignKey(AgingStorage, on_delete=models.PROTECT, related_name='records', verbose_name='库位')
    start_date = models.DateField('入储日期')
    expected_end_date = models.DateField('预计陈酿结束日期', null=True, blank=True)
    end_date = models.DateField('出储日期', null=True, blank=True)
    initial_volume = models.FloatField('初始容量(L)', default=0)
    current_volume = models.FloatField('当前容量(L)', default=0)
    container_count = models.IntegerField('容器数量(坛)', default=1)
    notes = models.TextField('备注', blank=True)
    is_active = models.BooleanField('是否在储', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'aging_record'
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.quality.batch.batch_no} - {self.storage.code}'


class AgingEnvRecord(models.Model):
    storage = models.ForeignKey(AgingStorage, on_delete=models.CASCADE, related_name='env_records', verbose_name='库位')
    record_time = models.DateTimeField('记录时间')
    temperature = models.FloatField('温度(℃)')
    humidity = models.FloatField('湿度(%)')
    operator = models.CharField('记录人', max_length=50, blank=True)
    is_abnormal = models.BooleanField('是否异常', default=False)
    notes = models.TextField('备注', blank=True)

    class Meta:
        db_table = 'aging_env_record'
        ordering = ['-record_time']

    def __str__(self):
        return f'{self.storage.code} - {self.record_time}'


class DisposalTask(models.Model):
    SOURCE_CHOICES = [
        ('fermentation', '发酵检测异常'),
        ('aging_env', '陈酿温湿度异常'),
        ('manual', '人工创建'),
    ]
    STATUS_CHOICES = [
        ('pending', '待处置'),
        ('processing', '处置中'),
        ('completed', '已处置待复核'),
        ('reviewed', '复核通过'),
        ('returned', '复核退回'),
    ]
    batch = models.ForeignKey(FermentationBatch, on_delete=models.CASCADE, related_name='disposal_tasks', verbose_name='发酵批次', null=True, blank=True)
    storage = models.ForeignKey(AgingStorage, on_delete=models.CASCADE, related_name='disposal_tasks', verbose_name='陈酿库位', null=True, blank=True)
    task_no = models.CharField('任务编号', max_length=50, unique=True)
    source = models.CharField('风险来源', max_length=20, choices=SOURCE_CHOICES, default='manual')
    risk_level = models.CharField('风险等级', max_length=20, choices=FermentationBatch.RISK_LEVEL_CHOICES, default='medium')
    title = models.CharField('任务标题', max_length=200)
    description = models.TextField('风险描述', blank=True)
    abnormal_record_id = models.IntegerField('关联异常记录ID', null=True, blank=True)
    responsible_person = models.CharField('责任人(酿酒师)', max_length=50, blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    disposal_measures = models.TextField('处置措施', blank=True)
    disposal_person = models.CharField('处置人', max_length=50, blank=True)
    disposal_time = models.DateTimeField('处置时间', null=True, blank=True)
    review_opinion = models.TextField('复核意见', blank=True)
    reviewer = models.CharField('复核人', max_length=50, blank=True)
    review_time = models.DateTimeField('复核时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'disposal_task'
        ordering = ['-created_at']

    def __str__(self):
        return self.task_no
