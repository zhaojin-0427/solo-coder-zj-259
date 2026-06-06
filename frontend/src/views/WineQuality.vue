<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-title">
        <el-icon><Medal /></el-icon>
        <span>酒质登记</span>
      </div>
      <el-button type="primary" @click="openDialog(null)">
        <el-icon><Plus /></el-icon>登记酒质
      </el-button>
    </div>

    <div class="stat-cards">
      <div class="stat-card">
        <div class="label">登记批次</div>
        <div class="value">{{ list.length }}<span class="unit">批</span></div>
      </div>
      <div class="stat-card">
        <div class="label">总出酒量</div>
        <div class="value" style="color:#c69c6d">{{ totalOutput }}<span class="unit">kg</span></div>
      </div>
      <div class="stat-card">
        <div class="label">优级酒占比</div>
        <div class="value" style="color:#e6a23c">{{ premiumRate }}<span class="unit">%</span></div>
      </div>
      <div class="stat-card">
        <div class="label">平均出酒率</div>
        <div class="value" style="color:#67c23a">{{ avgYieldRate }}<span class="unit">%</span></div>
      </div>
    </div>

    <div class="filter-bar">
      <el-select v-model="filterGrade" placeholder="酒质等级" clearable style="width:160px">
        <el-option label="优级" value="premium" />
        <el-option label="一级" value="grade1" />
        <el-option label="二级" value="grade2" />
        <el-option label="不合格" value="substandard" />
      </el-select>
      <el-input v-model="keyword" placeholder="搜索批次号" clearable style="width:240px" :prefix-icon="Search" />
    </div>

    <el-table :data="filteredList" border stripe style="width:100%">
      <el-table-column prop="batch_no" label="批次号" width="130" />
      <el-table-column prop="produce_date" label="出酒日期" width="120" />
      <el-table-column prop="total_output" label="出酒量(kg)" width="120" align="right" />
      <el-table-column label="出酒率" width="100" align="right">
        <template #default="{ row }">
          <span style="color:#67c23a;font-weight:600">{{ row.yield_rate }}%</span>
        </template>
      </el-table-column>
      <el-table-column label="酒质等级" width="100" align="center">
        <template #default="{ row }">
          <el-tag :class="'tag-' + row.grade" effect="light">{{ row.grade_display }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="alcohol_content" label="酒精度(°)" width="100" align="right" />
      <el-table-column prop="acidity" label="总酸(g/L)" width="100" align="right" />
      <el-table-column prop="ester" label="总酯(g/L)" width="100" align="right" />
      <el-table-column prop="sensory_score" label="感官评分" width="100" align="right" />
      <el-table-column prop="storage_location" label="陈酿位置" width="160" show-overflow-tooltip />
      <el-table-column prop="tasting_notes" label="品鉴记录" show-overflow-tooltip />
      <el-table-column label="操作" width="160" align="center" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" link @click="openDialog(row)">编辑</el-button>
          <el-button size="small" type="danger" link @click="removeItem(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑酒质' : '登记酒质'" width="620px">
      <el-form :model="form" label-width="110px" :rules="rules" ref="formRef">
        <el-form-item label="对应批次" prop="batch">
          <el-select v-model="form.batch" style="width:100%" placeholder="选择已完成发酵的批次" :disabled="!!form.id">
            <el-option v-for="b in completedBatches" :key="b.id" :label="b.batch_no + ' - ' + b.cellar_pool_code" :value="b.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="出酒日期" prop="produce_date">
          <el-date-picker v-model="form.produce_date" type="date" style="width:100%" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="出酒总量" prop="total_output">
          <el-input-number v-model="form.total_output" :min="0" :step="10" style="width:100%" />
          <span style="color:#999;font-size:12px;margin-left:8px">kg</span>
        </el-form-item>
        <el-form-item label="酒质等级" prop="grade">
          <el-select v-model="form.grade" style="width:100%">
            <el-option label="优级" value="premium" />
            <el-option label="一级" value="grade1" />
            <el-option label="二级" value="grade2" />
            <el-option label="不合格" value="substandard" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="酒精度" prop="alcohol_content">
              <el-input-number v-model="form.alcohol_content" :min="0" :max="100" :step="0.1" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="总酸">
              <el-input-number v-model="form.acidity" :min="0" :step="0.01" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="总酯">
              <el-input-number v-model="form.ester" :min="0" :step="0.01" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="感官评分">
          <el-input-number v-model="form.sensory_score" :min="0" :max="100" :step="0.5" style="width:100%" />
        </el-form-item>
        <el-form-item label="陈酿位置">
          <el-input v-model="form.storage_location" placeholder="如：地下酒窖A区1排1架" />
        </el-form-item>
        <el-form-item label="品鉴记录">
          <el-input v-model="form.tasting_notes" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.notes" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { qualityApi, batchApi } from '@/api'

const list = ref<any[]>([])
const completedBatches = ref<any[]>([])
const filterGrade = ref('')
const keyword = ref('')
const dialogVisible = ref(false)
const formRef = ref()

const defaultForm = () => ({
  id: null, batch: null, produce_date: new Date().toISOString().slice(0, 10),
  total_output: 0, grade: 'grade1', alcohol_content: 55, acidity: 1.5, ester: 3.0,
  sensory_score: 85, storage_location: '', tasting_notes: '', notes: ''
})
const form = ref<any>(defaultForm())

const rules = {
  batch: [{ required: true, message: '请选择批次', trigger: 'change' }],
  produce_date: [{ required: true, message: '请选择出酒日期', trigger: 'change' }],
  total_output: [{ required: true, message: '请输入出酒总量', trigger: 'blur' }],
  grade: [{ required: true, message: '请选择酒质等级', trigger: 'change' }],
  alcohol_content: [{ required: true, message: '请输入酒精度', trigger: 'blur' }],
}

const totalOutput = computed(() => list.value.reduce((s, x) => s + x.total_output, 0).toFixed(2))
const premiumRate = computed(() => {
  if (list.value.length === 0) return 0
  const premium = list.value.filter(x => x.grade === 'premium').length
  return ((premium / list.value.length) * 100).toFixed(1)
})
const avgYieldRate = computed(() => {
  if (list.value.length === 0) return 0
  const sum = list.value.reduce((s, x) => s + (x.yield_rate || 0), 0)
  return (sum / list.value.length).toFixed(2)
})

const filteredList = computed(() => {
  return list.value.filter(item => {
    const matchGrade = !filterGrade.value || item.grade === filterGrade.value
    const kw = keyword.value.trim()
    const matchKw = !kw || item.batch_no.includes(kw)
    return matchGrade && matchKw
  })
})

const loadData = async () => {
  const [qs, bs] = await Promise.all([qualityApi.list(), batchApi.list({ status: 'completed' })])
  list.value = qs.results
  completedBatches.value = bs.results.filter((b: any) => !qs.results.find((q: any) => q.batch === b.id))
}

const openDialog = (row: any) => {
  form.value = row ? { ...row } : defaultForm()
  if (row) form.value.batch = row.batch
  dialogVisible.value = true
}

const submitForm = async () => {
  await formRef.value.validate()
  if (form.value.id) {
    await qualityApi.update(form.value.id, form.value)
    ElMessage.success('修改成功')
  } else {
    await qualityApi.create(form.value)
    ElMessage.success('登记成功')
  }
  dialogVisible.value = false
  loadData()
}

const removeItem = async (row: any) => {
  await ElMessageBox.confirm(`确认删除批次「${row.batch_no}」的酒质记录吗？`, '提示', { type: 'warning' })
  await qualityApi.delete(row.id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(loadData)
</script>
