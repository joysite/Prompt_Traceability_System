<template>
  <div class="min-h-screen bg-gray-50 pb-8">
    <!-- 顶部防伪提示区域 -->
    <div class="bg-white shadow-sm px-4 pt-6 pb-4 flex items-start gap-3">
      <van-icon
        v-if="traceData"
        :name="isRisky ? 'warning-o' : 'shield-o'"
        :color="isRisky ? '#ef4444' : '#22c55e'"
        size="32"
      />
      <div class="flex-1">
        <div class="flex items-center justify-between">
          <h1 class="text-base font-semibold text-gray-900">
            {{ traceData?.product_name || '农产品溯源查询' }}
          </h1>
          <span
            v-if="traceData"
            class="text-xs text-gray-500"
          >
            扫码次数：{{ traceData.scan_count }}
          </span>
        </div>
        <p
          v-if="traceData"
          class="mt-1 text-xs leading-relaxed"
          :class="isRisky ? 'text-red-600' : 'text-emerald-600'"
        >
          <span v-if="!isRisky">
            正品校验通过，第 {{ traceData.scan_count }} 次查询。
          </span>
          <span v-else>
            注意：该码已被查询 {{ traceData.scan_count }} 次，谨防假冒。
          </span>
        </p>
        <p v-else class="mt-1 text-xs text-gray-500">
          正在加载溯源信息...
        </p>
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="p-4">
      <van-empty :description="error" />
    </div>

    <div v-else-if="traceData" class="px-4 pt-4 space-y-4">
      <!-- 产地信息 -->
      <van-cell-group inset>
        <van-cell title="产地信息" />
        <div class="px-4 pb-4 text-sm text-gray-700">
          <p v-if="originInfo?.address" class="mb-2">
            产地：{{ originInfo.address }}
          </p>
          <div v-if="originInfo?.images?.length" class="flex gap-2 overflow-x-auto">
            <van-image
              v-for="(img, idx) in originInfo.images"
              :key="idx"
              width="80"
              height="80"
              fit="cover"
              :src="img"
              @click="previewImages(originInfo.images, idx)"
            />
          </div>
        </div>
      </van-cell-group>

      <!-- 生产过程时间轴 -->
      <van-cell-group inset>
        <van-cell title="生产过程" />
        <div class="px-4 pb-4">
          <van-steps direction="vertical" :active="processSteps.length - 1">
            <van-step v-for="(step, index) in processSteps" :key="index">
              <div class="text-sm font-medium text-gray-900">{{ step.title }}</div>
              <div class="mt-1 text-xs text-gray-500">{{ step.time }}</div>
              <div class="mt-1 text-xs text-gray-700">{{ step.desc }}</div>
            </van-step>
          </van-steps>
        </div>
      </van-cell-group>

      <!-- 物流标准 -->
      <van-cell-group inset>
        <van-cell title="物流标准" />
        <div class="px-4 pb-4 text-sm text-gray-700 space-y-2">
          <p>
            本产品采用标准冷链运输（非实时定位）。
          </p>
          <p v-if="logisticsInfo?.description">
            {{ logisticsInfo.description }}
          </p>
          <div v-if="logisticsInfo?.route_images?.length" class="flex gap-2 overflow-x-auto">
            <van-image
              v-for="(img, idx) in logisticsInfo.route_images"
              :key="idx"
              width="120"
              height="80"
              fit="cover"
              :src="img"
              @click="previewImages(logisticsInfo.route_images, idx)"
            />
          </div>
        </div>
      </van-cell-group>

      <!-- 质检信息 -->
      <van-cell-group inset>
        <van-cell title="质检信息" />
        <div class="px-4 pb-4 text-sm text-gray-700 space-y-2">
          <p v-if="qualityInfo?.result">
            检测结果：{{ qualityInfo.result }}
          </p>
          <div v-if="qualityInfo?.report_images?.length" class="flex gap-2 overflow-x-auto">
            <van-image
              v-for="(img, idx) in qualityInfo.report_images"
              :key="idx"
              width="120"
              height="80"
              fit="cover"
              :src="img"
              @click="previewImages(qualityInfo.report_images, idx)"
            />
          </div>
        </div>
      </van-cell-group>
    </div>

    <van-image-preview v-model:show="preview.show" :images="preview.images" :start-position="preview.start" />

    <van-loading v-if="loading" type="spinner" size="24px" class="fixed bottom-4 left-1/2 -translate-x-1/2 text-gray-500">
      加载中...
    </van-loading>
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed, reactive, ref } from 'vue'
import { Toast } from 'vant'
import type { ImagePreviewOptions } from 'vant'

interface TraceResponse {
  batch_id: string
  product_name: string
  origin_info?: string | null
  process_info?: string | null
  logistics_static?: string | null
  quality_report?: string | null
  scan_count: number
  status: string
}

interface OriginInfo {
  address?: string
  images?: string[]
}

interface ProcessStep {
  title: string
  time?: string
  desc?: string
}

interface LogisticsInfo {
  description?: string
  route_images?: string[]
}

interface QualityInfo {
  result?: string
  report_images?: string[]
}

const traceData = ref<TraceResponse | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

const originInfo = ref<OriginInfo | null>(null)
const processSteps = ref<ProcessStep[]>([])
const logisticsInfo = ref<LogisticsInfo | null>(null)
const qualityInfo = ref<QualityInfo | null>(null)

const preview = reactive<{ show: boolean; images: string[]; start: number }>({
  show: false,
  images: [],
  start: 0,
})

const isRisky = computed(() => {
  if (!traceData.value) return false
  return traceData.value.scan_count >= 5
})

function getBatchIdFromUrl(): string | null {
  const url = new URL(window.location.href)
  // 优先使用 query 参数 ?batch_id=xxx
  const fromQuery = url.searchParams.get('batch_id')
  if (fromQuery) return fromQuery
  // 兼容路径最后一段为 batch_id 的情况
  const segments = url.pathname.split('/').filter(Boolean)
  return segments[segments.length - 1] || null
}

function safeParseJSON<T>(value?: string | null): T | null {
  if (!value) return null
  try {
    return JSON.parse(value) as T
  } catch (e) {
    console.warn('Failed to parse JSON field', e)
    return null
  }
}

function previewImages(images: string[], startIndex = 0) {
  if (!images.length) return
  preview.images = images
  preview.start = startIndex
  preview.show = true
}

async function fetchTrace() {
  const batchId = getBatchIdFromUrl()
  if (!batchId) {
    error.value = '缺少批次编号参数（batch_id）'
    return
  }

  loading.value = true
  error.value = null
  try {
    const res = await fetch(`/api/trace/${encodeURIComponent(batchId)}`)
    if (!res.ok) {
      const text = await res.text()
      throw new Error(text || '查询失败')
    }
    const data = (await res.json()) as TraceResponse
    traceData.value = data

    originInfo.value = safeParseJSON<OriginInfo>(data.origin_info)
    processSteps.value = safeParseJSON<ProcessStep[]>(data.process_info) || []
    logisticsInfo.value = safeParseJSON<LogisticsInfo>(data.logistics_static)
    qualityInfo.value = safeParseJSON<QualityInfo>(data.quality_report)
  } catch (e: any) {
    console.error(e)
    error.value = e?.message || '查询失败，请稍后重试'
    Toast.fail(error.value)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchTrace()
})
</script>

<style scoped>
/* 可以在此补充特定样式；全局移动端适配建议放在 Tailwind 配置和全局样式中 */
</style>
