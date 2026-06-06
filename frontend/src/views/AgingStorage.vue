<template>
  <div>
    <div class="page-container" style="margin-bottom:20px">
      <div class="page-header">
        <div class="page-title">
          <el-icon><Collection /></el-icon>
          <span>陈酿库位</span>
        </div>
        <div>
          <el-button type="primary" @click="openStorageDialog(null)" style="margin-right:8px">
            <el-icon><Plus /></el-icon>新增库位
          </el-button>
          <el-button type="success" @click="openRecordDialog(null)">
            <el-icon><Edit /></el-icon>入储登记
          </el-button>
        </div>
      </div>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="库位管理" name="storage">
          <div class="stat-cards">
            <div class="stat-card">
              <div class="label">库位总数</div>
              <div class="value">{{ storages.length }}<span class="unit">个</span></div>
            </div>
            <div class="stat-card">
              <div class="label">总容量</div>
              <div class="value" style="color:#c69c6d">{{ totalCapacity }}<span class="unit">坛</span></div>
            </div>
            <div class="stat-card">
              <div class="label">已使用</div>
              <div class="value" style="color:#e6a23c">{{ totalUsed }}<span class="unit">坛</span></div>
            </div>
            <div class="stat-card">
              <div class="label">平均占用率</div>
              <div class="value" style="color:#67c23a">{{ avgOccupancy }}<span class="unit">%</span></div>
            </div>
          </div>

          <div class="filter-bar">
            <el-select v-model="filterArea" placeholder="库区" clearable style="width:200px">
              <el-option v-for="a in areas" :key="a" :label="a" :value="a" />
            </el-select>
            <el-input v-model="kwStorage" placeholder="搜索库位编号" clearable style="width:220px" :prefix-icon="Search" />
          </div>

          <el-table :data="filteredStorages" border stripe style="width:100%">
            <el-table-column prop="code" label="库位编号" width="120" />
            <el-table-column prop="area" label="库区" width="160" />
            <el-table-column prop="row" label="排号" width="80" align="center" />
            <el-table-column prop="shelf" label="架号" width="100" align="center" />
            <el-table-column label="容量" width="100" align="right">
              <template #default="{ row }">{{ row.used_count }} / {{ row.capacity }} 坛</template>
            </el-table-column>
            <el-table-column label="占用率" width="120">
              <template #default="{ row }">
                <el-progress :percentage="row.occupancy_rate" :color="row.occupancy_rate > 90 ? '#f56c6c' : row.occupancy_rate > 70 ? '#e6a23c' : '#67c23a'" />
              </template>
            </el-table-column>
            <el-table-column prop="temperature_req" label="温度要求" width="110" align="center">
              <template #default="{ row }">{{ row.temperature_req }}℃</template>
            </el-table-column>
            <el-table-column prop="humidity_req" label="湿度要求" width="110" align="center">
              <template #default="{ row }">{{ row.humidity_req }}%</template>
            </el-table-column>
            <el-table-column label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :class="'tag-' + row.status" effect="light">{{ row.status_display }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="notes" label="备注" show-overflow-tooltip />
            <el-table-column label="操作" width="220" align="center" fixed="right">
              <template #default="{ row }">
                <el-button size="small" type="primary" link @click="viewRecords(row)">在储记录</el-button>
                <el-button size="small" type="success" link @click="openEnvDialog(row)">环境记录</el-button>
                <el-button size="small" link @click="openStorageDialog(row)">编辑</el-button>
                <el-button size="small" type="danger" link @click="removeStorage(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="陈酿记录" name="record">
          <div class="filter-bar">
            <el-select v-model="filterActive" placeholder="状态" clearable style="width:160px">
              <el-option label="在储中" :value="true" />
              <el-option label="已出储" :value="false" />
            </el-select>
            <el-input v-model="kwRecord" placeholder="搜索批次号" clearable style="width:220px" :prefix-icon="Search" />
          </div>

          <el-table :data="filteredRecords" border stripe style="width:100%">
            <el-table-column prop="batch_no" label="批次号" width="130" />
            <el-table-column prop="storage_code" label="库位" width="120" />
            <el-table-column prop="start_date" label="入储日期" width="120" />
            <el-table-column prop="expected_end_date" label="预计出储" width="120" />
            <el-table-column prop="end_date" label="实际出储" width="120">
              <template #default="{ row }">{{ row.end_date || '-' }}</template>
            </el-table-column>
            <el-table-column label="容量(L)" width="160" align="right">
              <template #default="{ row }">{{ row.current_volume }} / {{ row.initial_volume }}</template>
            </el-table-column>
            <el-table-column label="损耗率" width="110" align="center">
              <template #default="{ row }">
                <span :style="{ color: row.loss_rate > 5 ? '#f56c6c' : '#67c23a', fontWeight: 600 }">{{ row.loss_rate }}%</span>
              </template>
            </el-table-column>
            <el-table-column prop="container_count" label="数量(坛)" width="100" align="center" />
            <el-table-column label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag v-if="row.is_active" class="tag-fermenting" effect="light">在储中</el-tag>
                <el-tag v-else class="tag-idle" effect="light">已出储</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="160" align="center" fixed="right">
              <template #default="{ row }">
                <el-button v-if="row.is_active" size="small" type="warning" link @click="finishRecord(row)">完成</el-button>
                <el-button size="small" type="danger" link @click="removeRecord(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </div>

    <el-dialog v-model="storageDialogVisible" :title="storageForm.id ? '编辑库位' : '新增库位'" width="520px">
      <el-form :model="storageForm" label-width="100px" :rules="storageRules" ref="storageFormRef">
        <el-form-item label="库位编号" prop="code">
          <el-input v-model="storageForm.code" placeholder="如：CL-A-01" />
        </el-form-item>
        <el-form-item label="库区" prop="area">
          <el-input v-model="storageForm.area" placeholder="如：地下酒窖A区" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="排号">
              <el-input v-model="storageForm.row" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="架号">
              <el-input v-model="storageForm.shelf" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="最大容量" prop="capacity">
          <el-input-number v-model="storageForm.capacity" :min="0" style="width:100%" />
          <span style="color:#999;font-size:12px;margin-left:8px">坛</span>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="要求温度">
              <el-input-number v-model="storageForm.temperature_req" :min="0" :step="0.5" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="要求湿度">
              <el-input-number v-model="storageForm.humidity_req" :min="0" :max="100" :step="1" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="storageForm.notes" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="storageDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitStorage">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="recordDialogVisible" title="入储登记" width="520px">
      <el-form :model="recordForm" label-width="110px" :rules="recordRules" ref="recordFormRef">
        <el-form-item label="酒质批次" prop="quality">
          <el-select v-model="recordForm.quality" style="width:100%" placeholder="选择酒质登记批次">
            <el-option v-for="q in qualities" :key="q.id" :label="q.batch_no" :value="q.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="陈酿库位" prop="storage">
          <el-select v-model="recordForm.storage" style="width:100%" placeholder="选择库位">
            <el-option v-for="s in availableStorages" :key="s.id"
              :label="s.code + ' - ' + s.area + ' (剩余' + (s.capacity - s.used_count) + '坛)'" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="入储日期" prop="start_date">
          <el-date-picker v-model="recordForm.start_date" type="date" style="width:100%" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="预计出储日期">
          <el-date-picker v-model="recordForm.expected_end_date" type="date" style="width:100%" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="初始容量" prop="initial_volume">
              <el-input-number v-model="recordForm.initial_volume" :min="0" :step="1" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="容器数量" prop="container_count">
              <el-input-number v-model="recordForm.container_count" :min="1" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="recordForm.notes" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="recordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitRecord">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="envDialogVisible" title="环境温湿度记录" width="760px">
      <div v-if="currentStorage">
        <div style="margin-bottom:12px">
          <strong style="color:#3d2817">{{ currentStorage.code }} - {{ currentStorage.area }}</strong>
          <span style="color:#8b6914;margin-left:16px">要求：{{ currentStorage.temperature_req }}℃ / {{ currentStorage.humidity_req }}%</span>
        </div>
        <div ref="envChartRef" style="height:300px;margin-bottom:16px"></div>
        <el-form inline @submit.prevent>
          <el-form-item label="温度">
            <el-input-number v-model="envForm.temperature" :step="0.1" />℃
          </el-form-item>
          <el-form-item label="湿度">
            <el-input-number v-model="envForm.humidity" :step="1" />%
          </el-form-item>
          <el-form-item label="记录人">
            <el-input v-model="envForm.operator" placeholder="选填" style="width:120px" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="submitEnvRecord">添加记录</el-button>
          </el-form-item>
        </el-form>
        <el-table :data="envRecords" border size="small" style="margin-top:12px">
          <el-table-column prop="record_time" label="记录时间" width="170">
            <template #default="{ row }">{{ row.record_time?.replace('T', ' ').slice(0, 16) }}</template>
          </el-table-column>
          <el-table-column prop="temperature" label="温度(℃)" width="100" align="right" />
          <el-table-column prop="humidity" label="湿度(%)" width="100" align="right" />
          <el-table-column prop="operator" label="记录人" width="100" />
          <el-table-column label="异常" width="80" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.is_abnormal" type="danger" size="small">异常</el-tag>
              <span v-else style="color:#999">-</span>
            </template>
          </el-table-column>
          <el-table-column prop="notes" label="说明" show-overflow-tooltip />
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, reactive, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { storageApi, agingRecordApi, qualityApi, envRecordApi } from '@/api'

const activeTab = ref('storage')
const storages = ref<any[]>([])
const records = ref<any[]>([])
const qualities = ref<any[]>([])
const filterArea = ref('')
const kwStorage = ref('')
const kwRecord = ref('')
const filterActive: any = ref(null)
const envRecords = ref<any[]>([])
const currentStorage = ref<any>(null)
const envChartRef = ref<HTMLElement>()
let envChart: any = null

const areas = computed(() => [...new Set(storages.value.map(s => s.area))])
const totalCapacity = computed(() => storages.value.reduce((s, x) => s + x.capacity, 0))
const totalUsed = computed(() => storages.value.reduce((s, x) => s + x.used_count, 0))
const avgOccupancy = computed(() => {
  if (storages.value.length === 0) return 0
  const sum = storages.value.reduce((s, x) => s + (x.occupancy_rate || 0), 0)
  return (sum / storages.value.length).toFixed(1)
})
const availableStorages = computed(() => storages.value.filter(s => s.used_count < s.capacity))

const filteredStorages = computed(() => {
  return storages.value.filter(s => {
    const matchArea = !filterArea.value || s.area === filterArea.value
    const kw = kwStorage.value.trim()
    const matchKw = !kw || s.code.includes(kw) || s.area.includes(kw)
    return matchArea && matchKw
  })
})
const filteredRecords = computed(() => {
  return records.value.filter(r => {
    const matchActive = filterActive.value === null || r.is_active === filterActive.value
    const kw = kwRecord.value.trim()
    const matchKw = !kw || r.batch_no.includes(kw) || r.storage_code.includes(kw)
    return matchActive && matchKw
  })
})

const storageDialogVisible = ref(false)
const storageFormRef = ref()
const defaultStorage = () => ({
  id: null, code: '', area: '', row: '', shelf: '', capacity: 50,
  temperature_req: 15, humidity_req: 70, status: 'aging', notes: ''
})
const storageForm = ref<any>(defaultStorage())
const storageRules = {
  code: [{ required: true, message: '请输入库位编号', trigger: 'blur' }],
  area: [{ required: true, message: '请输入库区', trigger: 'blur' }],
  capacity: [{ required: true, message: '请输入容量', trigger: 'blur' }],
}

const recordDialogVisible = ref(false)
const recordFormRef = ref()
const defaultRecord = () => ({
  quality: null, storage: null,
  start_date: new Date().toISOString().slice(0, 10),
  expected_end_date: '', initial_volume: 500,
  current_volume: 500, container_count: 10, notes: ''
})
const recordForm = ref<any>(defaultRecord())
const recordRules = {
  quality: [{ required: true, message: '请选择酒质批次', trigger: 'change' }],
  storage: [{ required: true, message: '请选择库位', trigger: 'change' }],
  start_date: [{ required: true, message: '请选择入储日期', trigger: 'change' }],
  initial_volume: [{ required: true, message: '请输入初始容量', trigger: 'blur' }],
  container_count: [{ required: true, message: '请输入容器数量', trigger: 'blur' }],
}

const envDialogVisible = ref(false)
const envForm = reactive({ temperature: 16, humidity: 68, operator: '' })

const loadData = async () => {
  const [ss, rs, qs] = await Promise.all([storageApi.list(), agingRecordApi.list(), qualityApi.list()])
  storages.value = ss.results
  records.value = rs.results
  qualities.value = qs.results
}

const openStorageDialog = (row: any) => {
  storageForm.value = row ? { ...row } : defaultStorage()
  storageDialogVisible.value = true
}
const submitStorage = async () => {
  await storageFormRef.value.validate()
  if (storageForm.value.id) {
    await storageApi.update(storageForm.value.id, storageForm.value)
    ElMessage.success('修改成功')
  } else {
    await storageApi.create(storageForm.value)
    ElMessage.success('新增成功')
  }
  storageDialogVisible.value = false
  loadData()
}
const removeStorage = async (row: any) => {
  await ElMessageBox.confirm(`确认删除库位「${row.code}」吗？`, '提示', { type: 'warning' })
  await storageApi.delete(row.id)
  ElMessage.success('删除成功')
  loadData()
}

const openRecordDialog = (row: any) => {
  recordForm.value = defaultRecord()
  recordDialogVisible.value = true
}
const submitRecord = async () => {
  await recordFormRef.value.validate()
  await agingRecordApi.create(recordForm.value)
  ElMessage.success('入储登记成功')
  recordDialogVisible.value = false
  loadData()
}
const finishRecord = async (row: any) => {
  await ElMessageBox.confirm(`确认批次「${row.batch_no}」陈酿完成并出储吗？`, '提示', { type: 'warning' })
  await agingRecordApi.finish(row.id)
  ElMessage.success('陈酿已完成')
  loadData()
}
const removeRecord = async (row: any) => {
  await ElMessageBox.confirm(`确认删除这条陈酿记录吗？`, '提示', { type: 'warning' })
  await agingRecordApi.delete(row.id)
  ElMessage.success('删除成功')
  loadData()
}
const viewRecords = (row: any) => {
  activeTab.value = 'record'
  kwRecord.value = row.code
}

const openEnvDialog = async (row: any) => {
  currentStorage.value = row
  envDialogVisible.value = true
  const data: any = await envRecordApi.list({ storage: row.id })
  envRecords.value = data.results
  await nextTick()
  renderEnvChart()
}

const submitEnvRecord = async () => {
  if (!currentStorage.value) return
  const payload = {
    storage: currentStorage.value.id,
    record_time: new Date().toISOString().slice(0, 19),
    temperature: envForm.temperature,
    humidity: envForm.humidity,
    operator: envForm.operator,
  }
  const res: any = await envRecordApi.create(payload)
  if (res.is_abnormal) {
    ElMessage.warning('温湿度偏离要求范围')
  } else {
    ElMessage.success('记录已添加')
  }
  const data: any = await envRecordApi.list({ storage: currentStorage.value.id })
  envRecords.value = data.results
  renderEnvChart()
}

const renderEnvChart = () => {
  if (!envChartRef.value) return
  if (!envChart) {
    envChart = echarts.init(envChartRef.value)
  }
  const list = [...envRecords.value].reverse()
  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['温度(℃)', '湿度(%)'], top: 0 },
    grid: { left: 50, right: 60, top: 30, bottom: 30 },
    xAxis: {
      type: 'category',
      data: list.map(d => d.record_time?.slice(5, 16).replace('T', ' ')),
      axisLabel: { color: '#666', rotate: 30 }
    },
    yAxis: [
      { type: 'value', name: '温度', axisLabel: { color: '#666' } },
      { type: 'value', name: '湿度', axisLabel: { color: '#666' } }
    ],
    series: [
      {
        name: '温度(℃)', type: 'line', smooth: true,
        data: list.map(d => d.temperature), itemStyle: { color: '#e67e22' }
      },
      {
        name: '湿度(%)', type: 'line', smooth: true, yAxisIndex: 1,
        data: list.map(d => d.humidity), itemStyle: { color: '#3498db' }
      }
    ]
  }
  envChart.setOption(option)
}

onMounted(loadData)
</script>
