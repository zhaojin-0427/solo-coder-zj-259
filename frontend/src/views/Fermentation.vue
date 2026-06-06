<template>
  <div>
    <div class="page-container" style="margin-bottom:20px">
      <div class="page-header">
        <div class="page-title">
          <el-icon><DataAnalysis /></el-icon>
          <span>发酵监控</span>
        </div>
        <div>
          <el-button type="primary" @click="openBatchDialog(null)" style="margin-right:8px">
            <el-icon><Plus /></el-icon>入窖登记
          </el-button>
          <el-button type="success" @click="openRecordDialog(null)">
            <el-icon><Edit /></el-icon>发酵检测
          </el-button>
        </div>
      </div>

      <div class="stat-cards">
        <div class="stat-card">
          <div class="label">发酵中批次</div>
          <div class="value">{{ fermentingBatches.length }}<span class="unit">个</span></div>
        </div>
        <div class="stat-card">
          <div class="label">已完成批次</div>
          <div class="value" style="color:#67c23a">{{ completedCount }}<span class="unit">个</span></div>
        </div>
        <div class="stat-card">
          <div class="label">异常记录</div>
          <div class="value" style="color:#f56c6c">{{ abnormalCount }}<span class="unit">条</span></div>
        </div>
        <div class="stat-card">
          <div class="label">待处置任务</div>
          <div class="value" style="color:#e6a23c">{{ pendingTasks }}<span class="unit">个</span></div>
        </div>
        <div class="stat-card">
          <div class="label">高风险批次</div>
          <div class="value" style="color:#e74c3c">{{ highRiskCount }}<span class="unit">个</span></div>
        </div>
        <div class="stat-card">
          <div class="label">总检测次数</div>
          <div class="value">{{ recordCount }}<span class="unit">次</span></div>
        </div>
      </div>

      <div class="filter-bar">
        <el-select v-model="filterStatus" placeholder="批次状态" clearable style="width:160px">
          <el-option label="发酵中" value="fermenting" />
          <el-option label="已出酒" value="completed" />
          <el-option label="已终止" value="aborted" />
        </el-select>
        <el-select v-model="filterRisk" placeholder="风险等级" clearable style="width:160px">
          <el-option label="无风险" value="none" />
          <el-option label="低风险" value="low" />
          <el-option label="中风险" value="medium" />
          <el-option label="高风险" value="high" />
        </el-select>
        <el-select v-model="filterDisposal" placeholder="处置状态" clearable style="width:160px">
          <el-option label="无需处置" value="none" />
          <el-option label="待处置" value="pending" />
          <el-option label="处置中" value="processing" />
          <el-option label="待复核" value="completed" />
          <el-option label="复核通过" value="reviewed" />
          <el-option label="复核退回" value="returned" />
        </el-select>
        <el-select v-model="selectedBatch" placeholder="选择批次查看曲线" clearable style="width:240px" @change="loadCurve">
          <el-option v-for="b in batches" :key="b.id" :label="b.batch_no + ' - ' + b.cellar_pool_code" :value="b.id" />
        </el-select>
      </div>

      <el-table :data="filteredBatches" border stripe style="width:100%">
        <el-table-column prop="batch_no" label="批次号" width="130" fixed />
        <el-table-column prop="cellar_pool_code" label="窖池" width="100" />
        <el-table-column label="粮食配比" min-width="200">
          <template #default="{ row }">
            <span v-for="(v, k) in row.grain_ratio" :key="k" style="margin-right:10px">
              {{ k }}:{{ v }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="grain_total" label="粮食(kg)" width="100" align="right" />
        <el-table-column prop="yeast_type" label="酒曲类型" width="110" />
        <el-table-column prop="entry_temperature" label="入窖温度" width="100" align="right">
          <template #default="{ row }">{{ row.entry_temperature }}℃</template>
        </el-table-column>
        <el-table-column label="入窖时间" width="160">
          <template #default="{ row }">{{ formatDate(row.entry_date) }}</template>
        </el-table-column>
        <el-table-column prop="expected_days" label="预计天数" width="90" align="center" />
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :class="'tag-' + row.status" effect="light">{{ row.status_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="风险等级" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.risk_level === 'high'" type="danger" effect="dark">高风险</el-tag>
            <el-tag v-else-if="row.risk_level === 'medium'" type="warning" effect="light">中风险</el-tag>
            <el-tag v-else-if="row.risk_level === 'low'" type="info" effect="light">低风险</el-tag>
            <el-tag v-else type="success" effect="plain">无风险</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="处置状态" width="110" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.disposal_status === 'pending'" type="warning" effect="dark">待处置</el-tag>
            <el-tag v-else-if="row.disposal_status === 'processing'" type="primary" effect="light">处置中</el-tag>
            <el-tag v-else-if="row.disposal_status === 'completed'" type="info" effect="light">待复核</el-tag>
            <el-tag v-else-if="row.disposal_status === 'reviewed'" type="success" effect="light">复核通过</el-tag>
            <el-tag v-else-if="row.disposal_status === 'returned'" type="danger" effect="light">退回</el-tag>
            <span v-else style="color:#999">无需处置</span>
          </template>
        </el-table-column>
        <el-table-column label="责任人" width="100">
          <template #default="{ row }">{{ row.responsible_person || '-' }}</template>
        </el-table-column>
        <el-table-column label="最新检测" width="200">
          <template #default="{ row }">
            <div v-if="row.latest_record" style="font-size:12px;line-height:1.6">
              <div>窖温: {{ row.latest_record.cellar_temp }}℃ | 酸度: {{ row.latest_record.acidity }} | 酒度: {{ row.latest_record.alcohol }}°</div>
              <div style="color:#999">{{ formatDate(row.latest_record.record_time) }}</div>
              <el-tag v-if="row.latest_record.is_abnormal" type="danger" size="small" style="margin-top:4px">异常</el-tag>
            </div>
            <span v-else style="color:#999">暂无</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="360" align="center" fixed="right">
          <template #default="{ row }">
            <el-button size="small" link type="primary" @click="viewCurve(row)">查看曲线</el-button>
            <el-button size="small" link type="success" @click="openRecordDialog(row)">检测</el-button>
            <el-button v-if="row.latest_record?.is_abnormal || row.risk_level !== 'none'" size="small" link type="warning" @click="openCreateTask(row)">
              创建处置
            </el-button>
            <el-button v-if="row.latest_disposal_task" size="small" link type="primary" @click="openHandleTask(row.latest_disposal_task)">
              处理任务
            </el-button>
            <el-button v-if="row.status==='fermenting'" size="small" link type="warning" @click="completeBatch(row)">完成</el-button>
            <el-button size="small" link type="danger" @click="removeBatch(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div v-if="curveData.batch_no" class="page-container">
      <div class="page-header">
        <div class="page-title">
          <el-icon><TrendCharts /></el-icon>
          <span>发酵曲线 - {{ curveData.batch_no }}</span>
          <el-tag v-if="curveData.abnormal_count > 0" type="danger" style="margin-left:10px">
            异常 {{ curveData.abnormal_count }} 次
          </el-tag>
        </div>
        <div style="color:#8b6914;font-size:13px">
          入窖时间：{{ curveData.entry_date }} | 入窖温度：{{ curveData.entry_temp }}℃ | 预计：{{ curveData.expected_days }}天
        </div>
      </div>

      <div ref="chartRef" style="height:420px"></div>

      <el-table :data="curveData.data" border size="small" style="margin-top:16px">
        <el-table-column prop="day" label="发酵天数" width="100" align="center">
          <template #default="{ row }">第 {{ row.day }} 天</template>
        </el-table-column>
        <el-table-column prop="time" label="检测时间" width="160" />
        <el-table-column prop="cellar_temp" label="窖温(℃)" width="100" align="right" />
        <el-table-column prop="acidity" label="酸度" width="100" align="right" />
        <el-table-column prop="alcohol" label="酒度(°)" width="100" align="right" />
        <el-table-column label="异常" width="80" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_abnormal" type="danger" size="small">异常</el-tag>
            <span v-else style="color:#999">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="abnormal_note" label="异常说明" show-overflow-tooltip />
      </el-table>

      <el-alert v-if="curveData.abnormal_count > 0" type="warning" :closable="false" style="margin-top:16px">
        <template #title>
          <strong>预警提示：</strong>该批次共检测到 {{ curveData.abnormal_count }} 次异常数据，请及时关注发酵状态并采取相应措施。
        </template>
      </el-alert>
    </div>

    <el-dialog v-model="batchDialogVisible" :title="batchForm.id ? '编辑批次' : '入窖登记'" width="600px">
      <el-form :model="batchForm" label-width="110px" :rules="batchRules" ref="batchFormRef">
        <el-form-item label="批次号" prop="batch_no">
          <el-input v-model="batchForm.batch_no" placeholder="如：FJ2026001" />
        </el-form-item>
        <el-form-item label="窖池" prop="cellar_pool">
          <el-select v-model="batchForm.cellar_pool" style="width:100%" placeholder="选择窖池">
            <el-option v-for="p in idlePools" :key="p.id" :label="p.code + ' - ' + p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="粮食配比">
          <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;width:100%">
            <div v-for="(v, k) in grainTypes" :key="k">
              <label style="font-size:12px;color:#606266">{{ k }}</label>
              <el-input-number v-model="grainTypes[k]" :min="0" :max="100" size="small" style="width:100%" />
            </div>
          </div>
        </el-form-item>
        <el-form-item label="粮食总重量" prop="grain_total">
          <el-input-number v-model="batchForm.grain_total" :min="0" :step="100" style="width:100%" />
          <span style="color:#999;font-size:12px;margin-left:8px">kg</span>
        </el-form-item>
        <el-form-item label="酒曲类型" prop="yeast_type">
          <el-select v-model="batchForm.yeast_type" style="width:100%">
            <el-option label="高温大曲" value="高温大曲" />
            <el-option label="中温大曲" value="中温大曲" />
            <el-option label="低温大曲" value="低温大曲" />
            <el-option label="麸曲" value="麸曲" />
          </el-select>
        </el-form-item>
        <el-form-item label="酒曲用量">
          <el-input-number v-model="batchForm.yeast_amount" :min="0" :step="10" style="width:100%" />
          <span style="color:#999;font-size:12px;margin-left:8px">kg</span>
        </el-form-item>
        <el-form-item label="入窖温度" prop="entry_temperature">
          <el-input-number v-model="batchForm.entry_temperature" :min="0" :max="50" :step="0.5" style="width:100%" />
          <span style="color:#999;font-size:12px;margin-left:8px">℃</span>
        </el-form-item>
        <el-form-item label="入窖时间" prop="entry_date">
          <el-date-picker v-model="batchForm.entry_date" type="datetime" style="width:100%" value-format="YYYY-MM-DDTHH:mm:ss" />
        </el-form-item>
        <el-form-item label="预计天数">
          <el-input-number v-model="batchForm.expected_days" :min="1" style="width:100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="batchForm.notes" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="batchDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitBatch">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="recordDialogVisible" title="发酵检测记录" width="520px">
      <el-form :model="recordForm" label-width="100px" :rules="recordRules" ref="recordFormRef">
        <el-form-item label="批次" prop="batch">
          <el-select v-model="recordForm.batch" style="width:100%">
            <el-option v-for="b in fermentingBatches" :key="b.id" :label="b.batch_no" :value="b.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="检测时间" prop="record_time">
          <el-date-picker v-model="recordForm.record_time" type="datetime" style="width:100%" value-format="YYYY-MM-DDTHH:mm:ss" />
        </el-form-item>
        <el-form-item label="窖温" prop="cellar_temp">
          <el-input-number v-model="recordForm.cellar_temp" :min="0" :max="60" :step="0.1" style="width:100%" />
          <span style="color:#999;font-size:12px;margin-left:8px">℃</span>
        </el-form-item>
        <el-form-item label="酸度" prop="acidity">
          <el-input-number v-model="recordForm.acidity" :min="0" :max="10" :step="0.01" style="width:100%" />
        </el-form-item>
        <el-form-item label="酒度" prop="alcohol">
          <el-input-number v-model="recordForm.alcohol" :min="0" :max="80" :step="0.1" style="width:100%" />
          <span style="color:#999;font-size:12px;margin-left:8px">°</span>
        </el-form-item>
        <el-form-item label="环境温度">
          <el-input-number v-model="recordForm.ambient_temp" :min="0" :max="50" :step="0.1" style="width:100%" />
        </el-form-item>
        <el-form-item label="环境湿度">
          <el-input-number v-model="recordForm.ambient_humidity" :min="0" :max="100" :step="1" style="width:100%" />
        </el-form-item>
        <el-form-item label="检测人">
          <el-input v-model="recordForm.operator" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="recordForm.notes" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="recordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitRecord">提交检测</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="createTaskVisible" title="创建处置任务" width="560px">
      <el-form :model="taskForm" label-width="100px" :rules="taskRules" ref="taskFormRef">
        <el-form-item label="关联批次">
          <el-input v-model="taskBatchDisplay" disabled />
        </el-form-item>
        <el-form-item label="任务标题" prop="title">
          <el-input v-model="taskForm.title" placeholder="简要描述问题" />
        </el-form-item>
        <el-form-item label="风险来源" prop="source">
          <el-select v-model="taskForm.source" style="width:100%">
            <el-option label="发酵检测异常" value="fermentation" />
            <el-option label="陈酿温湿度异常" value="aging_env" />
            <el-option label="人工创建" value="manual" />
          </el-select>
        </el-form-item>
        <el-form-item label="风险等级" prop="risk_level">
          <el-radio-group v-model="taskForm.risk_level">
            <el-radio-button label="low">低</el-radio-button>
            <el-radio-button label="medium">中</el-radio-button>
            <el-radio-button label="high">高</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="责任人" prop="responsible_person">
          <el-input v-model="taskForm.responsible_person" placeholder="酿酒师姓名" />
        </el-form-item>
        <el-form-item label="风险描述">
          <el-input v-model="taskForm.description" type="textarea" :rows="3" placeholder="描述异常情况..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createTaskVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCreateTask">创建任务</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="handleTaskVisible" :title="'处置任务 - ' + (currentTask?.task_no || '')" width="600px">
      <div v-if="currentTask" style="margin-bottom:16px">
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="任务编号">{{ currentTask.task_no }}</el-descriptions-item>
          <el-descriptions-item label="风险来源">{{ currentTask.source_display }}</el-descriptions-item>
          <el-descriptions-item label="风险等级">
            <el-tag v-if="currentTask.risk_level === 'high'" type="danger">高风险</el-tag>
            <el-tag v-else-if="currentTask.risk_level === 'medium'" type="warning">中风险</el-tag>
            <el-tag v-else type="info">低风险</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag v-if="currentTask.status === 'pending'" type="warning">待处置</el-tag>
            <el-tag v-else-if="currentTask.status === 'processing'" type="primary">处置中</el-tag>
            <el-tag v-else-if="currentTask.status === 'completed'" type="info">待复核</el-tag>
            <el-tag v-else-if="currentTask.status === 'reviewed'" type="success">复核通过</el-tag>
            <el-tag v-else type="danger">退回</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="责任人">{{ currentTask.responsible_person || '-' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(currentTask.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="任务标题" :span="2">{{ currentTask.title }}</el-descriptions-item>
          <el-descriptions-item label="风险描述" :span="2">{{ currentTask.description || '-' }}</el-descriptions-item>
          <el-descriptions-item v-if="currentTask.disposal_measures" label="处置措施" :span="2">{{ currentTask.disposal_measures }}</el-descriptions-item>
          <el-descriptions-item v-if="currentTask.review_opinion" label="复核意见" :span="2">{{ currentTask.review_opinion }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <div v-if="currentTask?.status === 'pending' || currentTask?.status === 'returned'" style="text-align:center;padding:10px 0">
        <el-button type="primary" @click="startProcessTask">开始处置</el-button>
      </div>

      <div v-if="currentTask?.status === 'processing'">
        <el-form :model="handleForm" label-width="100px" :rules="handleRules" ref="handleFormRef">
          <el-form-item label="处置人" prop="disposal_person">
            <el-input v-model="handleForm.disposal_person" />
          </el-form-item>
          <el-form-item label="处置措施" prop="disposal_measures">
            <el-input v-model="handleForm.disposal_measures" type="textarea" :rows="4" placeholder="请填写具体处置措施..." />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="handleTaskVisible = false">取消</el-button>
          <el-button type="primary" @click="submitDisposal">提交处置，申请复核</el-button>
        </template>
      </div>

      <div v-if="currentTask?.status === 'completed'">
        <el-form :model="reviewForm" label-width="100px" :rules="reviewRules" ref="reviewFormRef">
          <el-form-item label="复核人" prop="reviewer">
            <el-input v-model="reviewForm.reviewer" />
          </el-form-item>
          <el-form-item label="复核意见" prop="review_opinion">
            <el-input v-model="reviewForm.review_opinion" type="textarea" :rows="3" placeholder="请填写复核意见..." />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="handleTaskVisible = false">取消</el-button>
          <el-button type="danger" @click="submitReview(false)">退回重办</el-button>
          <el-button type="success" @click="submitReview(true)">复核通过</el-button>
        </template>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import { batchApi, cellarPoolApi, recordApi, statsApi, disposalTaskApi } from '@/api'

const batches = ref<any[]>([])
const pools = ref<any[]>([])
const filterStatus = ref('')
const filterRisk = ref('')
const filterDisposal = ref('')
const selectedBatch = ref<number | null>(null)
const chartRef = ref<HTMLElement>()
let chart: any = null

const curveData = reactive<any>({
  batch_no: '', entry_date: '', entry_temp: 0, expected_days: 0, abnormal_count: 0, data: []
})

const fermentingBatches = computed(() => batches.value.filter(b => b.status === 'fermenting'))
const completedCount = computed(() => batches.value.filter(b => b.status === 'completed').length)
const recordCount = computed(() => batches.value.reduce((s, b) => s + (b.record_count || 0), 0))
const abnormalCount = ref(0)
const pendingTasks = computed(() => batches.value.filter(b => b.disposal_status === 'pending' || b.disposal_status === 'processing').length)
const highRiskCount = computed(() => batches.value.filter(b => b.risk_level === 'high').length)

const filteredBatches = computed(() => {
  return batches.value.filter(b => {
    const matchStatus = !filterStatus.value || b.status === filterStatus.value
    const matchRisk = !filterRisk.value || b.risk_level === filterRisk.value
    const matchDisposal = !filterDisposal.value || b.disposal_status === filterDisposal.value
    return matchStatus && matchRisk && matchDisposal
  })
})
const idlePools = computed(() => pools.value.filter(p => p.status === 'idle'))

const grainTypes = reactive<Record<string, number>>({ '高粱': 60, '小麦': 25, '玉米': 15 })

const batchDialogVisible = ref(false)
const batchFormRef = ref()
const defaultBatchForm = () => ({
  id: null, batch_no: '', cellar_pool: null, grain_total: 0,
  yeast_type: '中温大曲', yeast_amount: 200, entry_temperature: 22,
  entry_date: new Date().toISOString().slice(0, 19), expected_days: 30, notes: ''
})
const batchForm = ref<any>(defaultBatchForm())
const batchRules = {
  batch_no: [{ required: true, message: '请输入批次号', trigger: 'blur' }],
  cellar_pool: [{ required: true, message: '请选择窖池', trigger: 'change' }],
  grain_total: [{ required: true, message: '请输入粮食总重量', trigger: 'blur' }],
  yeast_type: [{ required: true, message: '请选择酒曲类型', trigger: 'change' }],
  entry_temperature: [{ required: true, message: '请输入入窖温度', trigger: 'blur' }],
  entry_date: [{ required: true, message: '请选择入窖时间', trigger: 'change' }],
}

const recordDialogVisible = ref(false)
const recordFormRef = ref()
const defaultRecordForm = () => ({
  batch: null, record_time: new Date().toISOString().slice(0, 19),
  cellar_temp: 25, acidity: 1.5, alcohol: 5,
  ambient_temp: 22, ambient_humidity: 65, operator: '', notes: ''
})
const recordForm = ref<any>(defaultRecordForm())
const recordRules = {
  batch: [{ required: true, message: '请选择批次', trigger: 'change' }],
  record_time: [{ required: true, message: '请选择检测时间', trigger: 'change' }],
  cellar_temp: [{ required: true, message: '请输入窖温', trigger: 'blur' }],
  acidity: [{ required: true, message: '请输入酸度', trigger: 'blur' }],
  alcohol: [{ required: true, message: '请输入酒度', trigger: 'blur' }],
}

const createTaskVisible = ref(false)
const taskFormRef = ref()
const currentBatch = ref<any>(null)
const taskBatchDisplay = computed(() => currentBatch.value ? currentBatch.value.batch_no + ' - ' + currentBatch.value.cellar_pool_code : '')
const defaultTaskForm = () => ({
  batch: null, title: '', source: 'fermentation', risk_level: 'medium',
  responsible_person: '', description: ''
})
const taskForm = ref<any>(defaultTaskForm())
const taskRules = {
  title: [{ required: true, message: '请输入任务标题', trigger: 'blur' }],
  source: [{ required: true, message: '请选择风险来源', trigger: 'change' }],
  risk_level: [{ required: true, message: '请选择风险等级', trigger: 'change' }],
  responsible_person: [{ required: true, message: '请输入责任人', trigger: 'blur' }],
}

const handleTaskVisible = ref(false)
const currentTask = ref<any>(null)
const handleFormRef = ref()
const handleForm = reactive({ disposal_person: '', disposal_measures: '' })
const handleRules = {
  disposal_person: [{ required: true, message: '请输入处置人', trigger: 'blur' }],
  disposal_measures: [{ required: true, message: '请填写处置措施', trigger: 'blur' }],
}
const reviewFormRef = ref()
const reviewForm = reactive({ reviewer: '', review_opinion: '' })
const reviewRules = {
  reviewer: [{ required: true, message: '请输入复核人', trigger: 'blur' }],
  review_opinion: [{ required: true, message: '请填写复核意见', trigger: 'blur' }],
}

const formatDate = (s: string) => s ? s.replace('T', ' ').slice(0, 16) : '-'

const loadData = async () => {
  const [bs, ps, ov] = await Promise.all([batchApi.list(), cellarPoolApi.list(), statsApi.overview()])
  batches.value = bs.results
  pools.value = ps.results
  abnormalCount.value = (ov as any).batches?.abnormal_records || 0
}

const viewCurve = async (row: any) => {
  selectedBatch.value = row.id
  await loadCurve(row.id)
  window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })
}

const loadCurve = async (id?: number) => {
  const bid = id || selectedBatch.value
  if (!bid) {
    Object.assign(curveData, { batch_no: '', entry_date: '', data: [] })
    return
  }
  const data: any = await batchApi.curve(bid)
  Object.assign(curveData, data)
  await nextTick()
  renderChart()
}

const renderChart = () => {
  if (!chartRef.value) return
  if (!chart) {
    chart = echarts.init(chartRef.value)
    window.addEventListener('resize', () => chart?.resize())
  }
  const data = curveData.data || []
  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['窖温(℃)', '酸度', '酒度(°)'], top: 0 },
    grid: { left: 50, right: 60, top: 40, bottom: 40 },
    xAxis: {
      type: 'category',
      data: data.map((d: any) => '第' + d.day + '天'),
      axisLabel: { color: '#666' }
    },
    yAxis: [
      { type: 'value', name: '温度/酒度', axisLabel: { color: '#666' } },
      { type: 'value', name: '酸度', axisLabel: { color: '#666' } }
    ],
    series: [
      {
        name: '窖温(℃)', type: 'line', smooth: true,
        data: data.map((d: any) => d.cellar_temp),
        itemStyle: { color: '#e67e22' },
        markPoint: {
          data: data.filter((d: any) => d.is_abnormal).map((d: any) => ({
            name: '异常', coord: ['第' + d.day + '天', d.cellar_temp],
            value: '异常', itemStyle: { color: '#e74c3c' }
          }))
        }
      },
      {
        name: '酸度', type: 'line', smooth: true, yAxisIndex: 1,
        data: data.map((d: any) => d.acidity),
        itemStyle: { color: '#3498db' }
      },
      {
        name: '酒度(°)', type: 'line', smooth: true,
        data: data.map((d: any) => d.alcohol),
        itemStyle: { color: '#9b59b6' }
      }
    ]
  }
  chart.setOption(option)
}

const openBatchDialog = (row: any) => {
  batchForm.value = row ? { ...row } : defaultBatchForm()
  if (row) batchForm.value.cellar_pool = row.cellar_pool
  batchDialogVisible.value = true
}

const submitBatch = async () => {
  await batchFormRef.value.validate()
  const payload = { ...batchForm.value }
  payload.grain_ratio = { ...grainTypes }
  if (payload.id) {
    await batchApi.update(payload.id, payload)
    ElMessage.success('修改成功')
  } else {
    await batchApi.create(payload)
    ElMessage.success('入窖登记成功')
  }
  batchDialogVisible.value = false
  loadData()
}

const removeBatch = async (row: any) => {
  await ElMessageBox.confirm(`确认删除批次「${row.batch_no}」吗？`, '提示', { type: 'warning' })
  await batchApi.delete(row.id)
  ElMessage.success('删除成功')
  loadData()
}

const completeBatch = async (row: any) => {
  await ElMessageBox.confirm(`确认批次「${row.batch_no}」已完成发酵并出酒吗？`, '提示', { type: 'warning' })
  await batchApi.complete(row.id)
  ElMessage.success('批次已完成')
  loadData()
}

const openRecordDialog = (row: any) => {
  recordForm.value = defaultRecordForm()
  if (row) recordForm.value.batch = row.id
  recordDialogVisible.value = true
}

const submitRecord = async () => {
  await recordFormRef.value.validate()
  const res: any = await recordApi.create(recordForm.value)
  if (res.is_abnormal) {
    ElMessage.warning('检测数据存在异常：' + (res.abnormal_note || '请关注并及时处置'))
  } else {
    ElMessage.success('检测记录已保存')
  }
  recordDialogVisible.value = false
  loadData()
  if (selectedBatch.value === recordForm.value.batch) {
    loadCurve(recordForm.value.batch)
  }
}

const openCreateTask = (row: any) => {
  currentBatch.value = row
  taskForm.value = defaultTaskForm()
  taskForm.value.batch = row.id
  taskForm.value.risk_level = row.risk_level === 'none' ? 'medium' : row.risk_level
  if (row.latest_record?.is_abnormal) {
    taskForm.value.title = row.batch_no + ' 发酵检测异常'
    taskForm.value.description = row.latest_record.abnormal_note || ''
    taskForm.value.source = 'fermentation'
  } else {
    taskForm.value.title = row.batch_no + ' 风险处置'
  }
  createTaskVisible.value = true
}

const submitCreateTask = async () => {
  await taskFormRef.value.validate()
  const payload = { ...taskForm.value }
  await disposalTaskApi.create(payload)
  ElMessage.success('处置任务创建成功')
  createTaskVisible.value = false
  loadData()
}

const openHandleTask = (task: any) => {
  currentTask.value = { ...task }
  handleForm.disposal_person = task.disposal_person || ''
  handleForm.disposal_measures = task.disposal_measures || ''
  reviewForm.reviewer = task.reviewer || ''
  reviewForm.review_opinion = task.review_opinion || ''
  handleTaskVisible.value = true
}

const startProcessTask = async () => {
  if (!currentTask.value) return
  await disposalTaskApi.startProcess(currentTask.value.id)
  ElMessage.success('已开始处置')
  handleTaskVisible.value = false
  loadData()
}

const submitDisposal = async () => {
  await handleFormRef.value.validate()
  if (!currentTask.value) return
  await disposalTaskApi.submitDisposal(currentTask.value.id, { ...handleForm })
  ElMessage.success('处置措施已提交，等待复核')
  handleTaskVisible.value = false
  loadData()
}

const submitReview = async (passed: boolean) => {
  await reviewFormRef.value.validate()
  if (!currentTask.value) return
  await disposalTaskApi.review(currentTask.value.id, { ...reviewForm, passed })
  ElMessage.success(passed ? '复核通过' : '已退回重办')
  handleTaskVisible.value = false
  loadData()
}

onMounted(async () => {
  await loadData()
  if (fermentingBatches.value.length > 0) {
    selectedBatch.value = fermentingBatches.value[0].id
    loadCurve()
  }
})
</script>
