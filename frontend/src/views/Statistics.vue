<template>
  <div>
    <div class="page-container" style="margin-bottom:20px">
      <div class="page-header">
        <div class="page-title">
          <el-icon><TrendCharts /></el-icon>
          <span>统计分析</span>
        </div>
      </div>

      <div class="stat-cards">
        <div class="stat-card">
          <div class="label">平均出酒率</div>
          <div class="value" style="color:#e67e22">{{ yieldRate.average_yield_rate || 0 }}<span class="unit">%</span></div>
        </div>
        <div class="stat-card">
          <div class="label">优级酒占比</div>
          <div class="value" style="color:#cf8500">{{ premiumPercentage }}<span class="unit">%</span></div>
        </div>
        <div class="stat-card">
          <div class="label">平均发酵周期</div>
          <div class="value" style="color:#3498db">{{ cycle.average_cycle_days || 0 }}<span class="unit">天</span></div>
        </div>
        <div class="stat-card">
          <div class="label">综合陈酿损耗率</div>
          <div class="value" :style="{ color: (agingLoss.overall_loss_rate || 0) > 5 ? '#e74c3c' : '#27ae60' }">
            {{ agingLoss.overall_loss_rate || 0 }}<span class="unit">%</span>
          </div>
        </div>
      </div>
    </div>

    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="14">
        <div class="chart-box">
          <div class="chart-title">各批次出酒率趋势</div>
          <div ref="yieldChartRef" style="height:340px"></div>
        </div>
      </el-col>
      <el-col :span="10">
        <div class="chart-box">
          <div class="chart-title">酒质等级分布</div>
          <div ref="gradeChartRef" style="height:340px"></div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="12">
        <div class="chart-box">
          <div class="chart-title">发酵周期统计（按酒曲类型）</div>
          <div ref="cycleChartRef" style="height:340px"></div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="chart-box">
          <div class="chart-title">月度出酒量</div>
          <div ref="monthlyChartRef" style="height:340px"></div>
        </div>
      </el-col>
    </el-row>

    <div class="page-container">
      <div class="page-header">
        <div class="page-title">
          <el-icon><DataLine /></el-icon>
          <span>陈酿损耗明细</span>
        </div>
      </div>
      <el-table :data="agingLoss.list || []" border stripe style="width:100%">
        <el-table-column prop="batch_no" label="批次号" width="130" />
        <el-table-column prop="storage" label="库位" width="120" />
        <el-table-column prop="start_date" label="入储日期" width="120" />
        <el-table-column prop="end_date" label="出储日期" width="120">
          <template #default="{ row }">{{ row.end_date || '在储中' }}</template>
        </el-table-column>
        <el-table-column prop="aging_days" label="陈酿天数" width="100" align="right">
          <template #default="{ row }">{{ row.aging_days ?? '-' }}</template>
        </el-table-column>
        <el-table-column prop="initial_volume" label="初始容量(L)" width="120" align="right" />
        <el-table-column prop="current_volume" label="当前容量(L)" width="120" align="right" />
        <el-table-column label="损耗率" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="row.loss_rate > 5 ? 'danger' : row.loss_rate > 3 ? 'warning' : 'success'" effect="light">
              {{ row.loss_rate }}%
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_active" class="tag-fermenting" effect="light">在储中</el-tag>
            <el-tag v-else class="tag-idle" effect="light">已完成</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, reactive } from 'vue'
import * as echarts from 'echarts'
import { statsApi } from '@/api'

const yieldRate = reactive<any>({ average_yield_rate: 0, list: [] })
const gradeDist = ref<any[]>([])
const cycle = reactive<any>({ average_cycle_days: 0, by_yeast: [], cycles: [] })
const agingLoss = reactive<any>({ overall_loss_rate: 0, list: [] })
const monthlyOutput = ref<any[]>([])

const yieldChartRef = ref<HTMLElement>()
const gradeChartRef = ref<HTMLElement>()
const cycleChartRef = ref<HTMLElement>()
const monthlyChartRef = ref<HTMLElement>()

let yieldChart: any, gradeChart: any, cycleChart: any, monthlyChart: any

const premiumPercentage = computed(() => {
  const premium = gradeDist.value.find(x => x.grade === 'premium')
  return premium?.percentage || 0
})

const loadData = async () => {
  const [y, g, c, a, m] = await Promise.all([
    statsApi.yieldRate(),
    statsApi.gradeDistribution(),
    statsApi.fermentationCycle(),
    statsApi.agingLoss(),
    statsApi.monthlyOutput(),
  ])
  Object.assign(yieldRate, y)
  gradeDist.value = g as any
  Object.assign(cycle, c)
  Object.assign(agingLoss, a)
  monthlyOutput.value = m as any
  await nextTick()
  renderCharts()
}

const renderCharts = () => {
  if (yieldChartRef.value) {
    if (!yieldChart) yieldChart = echarts.init(yieldChartRef.value)
    const data = yieldRate.list || []
    yieldChart.setOption({
      tooltip: { trigger: 'axis', formatter: (p: any) => {
        const d = data[p[0].dataIndex]
        return `${d.batch_no}<br/>出酒率: ${d.yield_rate}%<br/>等级: ${d.grade}`
      }},
      grid: { left: 50, right: 20, top: 30, bottom: 40 },
      xAxis: { type: 'category', data: data.map((d: any) => d.batch_no), axisLabel: { rotate: 30, color: '#666' } },
      yAxis: { type: 'value', name: '出酒率(%)', axisLabel: { color: '#666' } },
      series: [{
        type: 'bar',
        data: data.map((d: any) => ({
          value: d.yield_rate,
          itemStyle: {
            color: d.grade === '优级' ? '#cf8500' : d.grade === '一级' ? '#409eff' : d.grade === '二级' ? '#909399' : '#f56c6c'
          }
        })),
        label: { show: true, position: 'top', formatter: '{c}%', color: '#666' }
      }]
    })
  }

  if (gradeChartRef.value) {
    if (!gradeChart) gradeChart = echarts.init(gradeChartRef.value)
    gradeChart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
      legend: { bottom: 0 },
      series: [{
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['50%', '45%'],
        data: gradeDist.value.map(d => ({
          name: d.label,
          value: d.count,
          itemStyle: {
            color: d.grade === 'premium' ? '#cf8500' : d.grade === 'grade1' ? '#409eff' : d.grade === 'grade2' ? '#909399' : '#f56c6c'
          }
        })),
        label: { formatter: '{b}\n{d}%' }
      }]
    })
  }

  if (cycleChartRef.value) {
    if (!cycleChart) cycleChart = echarts.init(cycleChartRef.value)
    const data = cycle.by_yeast || []
    cycleChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: 50, right: 20, top: 30, bottom: 40 },
      xAxis: { type: 'category', data: data.map((d: any) => d.yeast_type), axisLabel: { color: '#666' } },
      yAxis: { type: 'value', name: '平均周期(天)', axisLabel: { color: '#666' } },
      series: [{
        type: 'bar',
        data: data.map((d: any) => d.avg_days),
        itemStyle: { color: '#3498db' },
        label: { show: true, position: 'top', formatter: '{c}天', color: '#666' },
        barWidth: '50%'
      }]
    })
  }

  if (monthlyChartRef.value) {
    if (!monthlyChart) monthlyChart = echarts.init(monthlyChartRef.value)
    const data = monthlyOutput.value || []
    monthlyChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['出酒量(kg)', '批次数'], top: 0 },
      grid: { left: 60, right: 60, top: 40, bottom: 40 },
      xAxis: { type: 'category', data: data.map((d: any) => d.month), axisLabel: { color: '#666' } },
      yAxis: [
        { type: 'value', name: '出酒量(kg)', axisLabel: { color: '#666' } },
        { type: 'value', name: '批次数', axisLabel: { color: '#666' } }
      ],
      series: [
        {
          name: '出酒量(kg)', type: 'line', smooth: true,
          data: data.map((d: any) => d.output),
          itemStyle: { color: '#c69c6d' },
          areaStyle: { color: 'rgba(198,156,109,0.2)' }
        },
        {
          name: '批次数', type: 'bar', yAxisIndex: 1,
          data: data.map((d: any) => d.batch_count),
          itemStyle: { color: '#9b59b6' }
        }
      ]
    })
  }

  window.addEventListener('resize', () => {
    yieldChart?.resize()
    gradeChart?.resize()
    cycleChart?.resize()
    monthlyChart?.resize()
  })
}

onMounted(loadData)
</script>
