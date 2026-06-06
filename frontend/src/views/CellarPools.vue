<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-title">
        <el-icon><OfficeBuilding /></el-icon>
        <span>窖池管理</span>
      </div>
      <el-button type="primary" @click="openDialog(null)">
        <el-icon><Plus /></el-icon>新增窖池
      </el-button>
    </div>

    <div class="stat-cards">
      <div class="stat-card">
        <div class="label">窖池总数</div>
        <div class="value">{{ overview.cellar_pools.total }}<span class="unit">个</span></div>
      </div>
      <div class="stat-card">
        <div class="label">发酵中</div>
        <div class="value" style="color:#e6a23c">{{ overview.cellar_pools.fermenting }}<span class="unit">个</span></div>
      </div>
      <div class="stat-card">
        <div class="label">空闲</div>
        <div class="value" style="color:#67c23a">{{ overview.cellar_pools.idle }}<span class="unit">个</span></div>
      </div>
      <div class="stat-card">
        <div class="label">发酵批次</div>
        <div class="value">{{ overview.batches.fermenting }}<span class="unit">个</span></div>
      </div>
    </div>

    <div class="filter-bar">
      <el-select v-model="filterStatus" placeholder="状态筛选" clearable style="width:160px">
        <el-option label="空闲" value="idle" />
        <el-option label="发酵中" value="fermenting" />
        <el-option label="清洁中" value="cleaning" />
        <el-option label="维护中" value="maintenance" />
      </el-select>
      <el-input v-model="keyword" placeholder="搜索窖池编号/名称" clearable style="width:240px" :prefix-icon="Search" />
    </div>

    <el-table :data="filteredList" border stripe style="width:100%">
      <el-table-column prop="code" label="窖池编号" width="120" />
      <el-table-column prop="name" label="窖池名称" width="140" />
      <el-table-column prop="location" label="位置" width="180" />
      <el-table-column prop="volume" label="容量(kg)" width="110" align="right" />
      <el-table-column prop="built_year" label="建造年份" width="110" align="center" />
      <el-table-column label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :class="'tag-' + row.status" effect="light">{{ row.status_display }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="当前批次" width="160">
        <template #default="{ row }">
          <span v-if="row.active_batch" style="color:#c69c6d;font-weight:600">{{ row.active_batch.batch_no }}</span>
          <span v-else style="color:#999">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="notes" label="备注" show-overflow-tooltip />
      <el-table-column label="操作" width="160" align="center" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" link @click="openDialog(row)">编辑</el-button>
          <el-button size="small" type="danger" link @click="removeItem(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑窖池' : '新增窖池'" width="520px">
      <el-form :model="form" label-width="100px" :rules="rules" ref="formRef">
        <el-form-item label="窖池编号" prop="code">
          <el-input v-model="form.code" placeholder="如：JC-001" />
        </el-form-item>
        <el-form-item label="窖池名称" prop="name">
          <el-input v-model="form.name" placeholder="如：老窖一号" />
        </el-form-item>
        <el-form-item label="位置" prop="location">
          <el-input v-model="form.location" />
        </el-form-item>
        <el-form-item label="容量(kg)" prop="volume">
          <el-input-number v-model="form.volume" :min="0" :step="500" style="width:100%" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" style="width:100%">
            <el-option label="空闲" value="idle" />
            <el-option label="发酵中" value="fermenting" />
            <el-option label="清洁中" value="cleaning" />
            <el-option label="维护中" value="maintenance" />
          </el-select>
        </el-form-item>
        <el-form-item label="建造年份">
          <el-input-number v-model="form.built_year" :min="1900" :max="2100" style="width:100%" />
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
import { cellarPoolApi, statsApi } from '@/api'

const list = ref<any[]>([])
const overview = ref<any>({
  cellar_pools: { total: 0, fermenting: 0, idle: 0 },
  batches: { fermenting: 0 },
})
const filterStatus = ref('')
const keyword = ref('')
const dialogVisible = ref(false)
const formRef = ref()

const defaultForm = () => ({
  id: null, code: '', name: '', location: '', volume: 0,
  status: 'idle', built_year: 2020, notes: ''
})
const form = ref<any>(defaultForm())

const rules = {
  code: [{ required: true, message: '请输入窖池编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入窖池名称', trigger: 'blur' }],
  volume: [{ required: true, message: '请输入容量', trigger: 'blur' }],
}

const filteredList = computed(() => {
  return list.value.filter(item => {
    const matchStatus = !filterStatus.value || item.status === filterStatus.value
    const kw = keyword.value.trim()
    const matchKw = !kw || item.code.includes(kw) || item.name.includes(kw) || item.location.includes(kw)
    return matchStatus && matchKw
  })
})

const loadData = async () => {
  const [pools, ov] = await Promise.all([cellarPoolApi.list(), statsApi.overview()])
  list.value = pools.results
  overview.value = ov
}

const openDialog = (row: any) => {
  form.value = row ? { ...row } : defaultForm()
  dialogVisible.value = true
}

const submitForm = async () => {
  await formRef.value.validate()
  if (form.value.id) {
    await cellarPoolApi.update(form.value.id, form.value)
    ElMessage.success('修改成功')
  } else {
    await cellarPoolApi.create(form.value)
    ElMessage.success('新增成功')
  }
  dialogVisible.value = false
  loadData()
}

const removeItem = async (row: any) => {
  await ElMessageBox.confirm(`确认删除窖池「${row.code}」吗？`, '提示', { type: 'warning' })
  await cellarPoolApi.delete(row.id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(loadData)
</script>
