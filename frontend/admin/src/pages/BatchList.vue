<template>
  <div class="bg-white shadow-sm rounded-lg p-4">
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-2">
        <el-input
          v-model="query.batchId"
          placeholder="批次编号"
          size="small"
          clearable
          class="w-48"
        />
        <el-input
          v-model="query.productName"
          placeholder="产品名称"
          size="small"
          clearable
          class="w-48"
        />
        <el-button type="primary" size="small" @click="fetchBatches">查询</el-button>
      </div>
      <div class="flex items-center gap-2">
        <el-button type="primary" size="small" @click="openEdit()">新建批次</el-button>
      </div>
    </div>

    <el-table :data="batches" border size="small" class="w-full" v-loading="loading">
      <el-table-column prop="batch_id" label="批次编号" min-width="140" />
      <el-table-column prop="product_name" label="产品名称" min-width="140" />
      <el-table-column prop="status" label="状态" min-width="80" />
      <el-table-column prop="scan_count" label="扫码次数" min-width="90" />
      <el-table-column prop="created_at" label="创建时间" min-width="160" />
      <el-table-column label="操作" fixed="right" min-width="200">
        <template #default="scope">
          <el-button type="primary" text size="small" @click="openEdit(scope.row)">编辑</el-button>
          <el-button type="success" text size="small" @click="openClone(scope.row)">克隆</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 编辑/新建弹窗 -->
    <el-dialog v-model="editDialog.visible" :title="editDialog.title" width="600px">
      <el-form :model="editForm" label-width="90px" label-position="left">
        <el-form-item label="批次编号">
          <el-input v-model="editForm.batch_id" :disabled="!!editDialog.originalId" />
        </el-form-item>
        <el-form-item label="产品名称">
          <el-input v-model="editForm.product_name" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="editForm.status">
            <el-option label="正常" value="normal" />
            <el-option label="过期" value="expired" />
            <el-option label="召回" value="recall" />
          </el-select>
        </el-form-item>
        <el-form-item label="产地信息 (JSON)">
          <el-input v-model="editForm.origin_info" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="生产过程 (JSON)">
          <el-input v-model="editForm.process_info" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="物流标准 (JSON)">
          <el-input v-model="editForm.logistics_static" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="质检信息 (JSON)">
          <el-input v-model="editForm.quality_report" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="saveBatch">保存</el-button>
      </template>
    </el-dialog>

    <!-- 克隆弹窗 -->
    <el-dialog v-model="cloneDialog.visible" title="克隆批次" width="400px">
      <div class="space-y-3">
        <p class="text-sm text-gray-700">
          将基于批次 <span class="font-mono">{{ cloneDialog.source?.batch_id }}</span> 创建一个新批次，
          除批次编号和扫码次数外，其余字段将默认继承。
        </p>
        <el-input v-model="cloneDialog.newBatchId" placeholder="新批次编号（可留空自动生成）" />
      </div>
      <template #footer>
        <el-button @click="cloneDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="doClone">确认克隆</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '@/api/http'

interface BatchItem {
  batch_id: string
  product_name: string
  status: string
  scan_count: number
  created_at?: string
  origin_info?: string | null
  process_info?: string | null
  logistics_static?: string | null
  quality_report?: string | null
}

const loading = ref(false)
const batches = ref<BatchItem[]>([])

const query = reactive({
  batchId: '',
  productName: '',
})

const editDialog = reactive<{ visible: boolean; title: string; originalId: string | null }>({
  visible: false,
  title: '新建批次',
  originalId: null,
})

const editForm = reactive<BatchItem>({
  batch_id: '',
  product_name: '',
  status: 'normal',
  scan_count: 0,
  origin_info: '',
  process_info: '',
  logistics_static: '',
  quality_report: '',
})

const cloneDialog = reactive<{ visible: boolean; source: BatchItem | null; newBatchId: string }>({
  visible: false,
  source: null,
  newBatchId: '',
})

async function fetchBatches() {
  loading.value = true
  try {
    // 后端暂未实现分页/筛选接口，这里先使用占位逻辑
    // TODO: 你可以根据实际后端 API 替换为真实列表接口
    const res = await http.get<BatchItem[]>('/admin/batches/', {
      params: {
        batch_id: query.batchId || undefined,
        product_name: query.productName || undefined,
      },
    })
    batches.value = res.data
  } catch (e: any) {
    console.error(e)
    ElMessage.error(e?.message || '获取批次列表失败')
  } finally {
    loading.value = false
  }
}

function openEdit(row?: BatchItem) {
  if (row) {
    editDialog.title = '编辑批次'
    editDialog.originalId = row.batch_id
    Object.assign(editForm, row)
  } else {
    editDialog.title = '新建批次'
    editDialog.originalId = null
    Object.assign(editForm, {
      batch_id: '',
      product_name: '',
      status: 'normal',
      scan_count: 0,
      origin_info: '',
      process_info: '',
      logistics_static: '',
      quality_report: '',
    })
  }
  editDialog.visible = true
}

async function saveBatch() {
  try {
    if (!editForm.batch_id || !editForm.product_name) {
      ElMessage.warning('请填写批次编号和产品名称')
      return
    }

    if (editDialog.originalId) {
      await http.put(`/admin/batches/${encodeURIComponent(editDialog.originalId)}/`, editForm)
      ElMessage.success('更新成功')
    } else {
      await http.post('/admin/batches/', editForm)
      ElMessage.success('创建成功')
    }

    editDialog.visible = false
    fetchBatches()
  } catch (e: any) {
    console.error(e)
    ElMessage.error(e?.message || '保存失败')
  }
}

function openClone(row: BatchItem) {
  cloneDialog.source = row
  cloneDialog.newBatchId = ''
  cloneDialog.visible = true
}

async function doClone() {
  if (!cloneDialog.source) return
  try {
    await http.post('/admin/batch/clone', {
      old_batch_id: cloneDialog.source.batch_id,
      new_batch_id: cloneDialog.newBatchId || null,
    })
    ElMessage.success('克隆成功')
    cloneDialog.visible = false
    fetchBatches()
  } catch (e: any) {
    console.error(e)
    ElMessage.error(e?.message || '克隆失败')
  }
}

onMounted(() => {
  fetchBatches()
})
</script>
