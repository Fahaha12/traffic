<template>
  <el-form
    ref="formRef"
    :model="form"
    :rules="rules"
    label-width="100px"
    @submit.prevent="handleSubmit"
  >
    <el-form-item label="摄像头名称" prop="name">
      <el-input v-model="form.name" placeholder="请输入摄像头名称" />
    </el-form-item>
    
    <el-form-item label="摄像头类型" prop="type">
      <el-select v-model="form.type" placeholder="请选择类型" style="width: 100%">
        <el-option label="交通监控" value="traffic" />
        <el-option label="安防监控" value="surveillance" />
        <el-option label="测速监控" value="speed" />
      </el-select>
    </el-form-item>
    
    <el-form-item label="流媒体地址" prop="streamUrl">
      <el-input v-model="form.streamUrl" placeholder="请输入流媒体地址" />
    </el-form-item>
    
    <el-form-item label="流媒体类型" prop="streamType">
      <el-select v-model="form.streamType" placeholder="请选择类型" style="width: 100%">
        <el-option label="RTMP" value="rtmp" />
        <el-option label="HLS" value="hls" />
        <el-option label="WebRTC" value="webrtc" />
      </el-select>
    </el-form-item>
    
    <el-form-item label="位置信息">
      <el-row :gutter="10">
        <el-col :span="12">
          <el-form-item prop="lat">
            <el-input v-model="form.lat" placeholder="纬度" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item prop="lng">
            <el-input v-model="form.lng" placeholder="经度" />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form-item>
    
    <el-form-item label="分辨率">
      <el-row :gutter="10">
        <el-col :span="12">
          <el-form-item prop="width">
            <el-input-number v-model="form.width" :min="320" :max="4096" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item prop="height">
            <el-input-number v-model="form.height" :min="240" :max="2160" style="width: 100%" />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form-item>
    
    <el-form-item label="帧率" prop="fps">
      <el-input-number v-model="form.fps" :min="1" :max="60" style="width: 100%" />
    </el-form-item>
    
    <el-form-item label="朝向角度" prop="direction">
      <el-input-number v-model="form.direction" :min="0" :max="360" style="width: 100%" />
    </el-form-item>
    
    <el-form-item>
      <el-button type="primary" @click="handleSubmit" :loading="loading">
        添加摄像头
      </el-button>
      <el-button @click="handleCancel">取消</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useCameraStore } from '@/stores/camera'
import type { Camera } from '@/types'

const emit = defineEmits<{
  success: []
  cancel: []
}>()

const formRef = ref<FormInstance>()
const loading = ref(false)
const cameraStore = useCameraStore()

const form = reactive({
  name: '',
  type: '',
  streamUrl: '',
  streamType: 'hls',
  lat: '',
  lng: '',
  width: 1920,
  height: 1080,
  fps: 25,
  direction: 0
})

const rules: FormRules = {
  name: [
    { required: true, message: '请输入摄像头名称', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择摄像头类型', trigger: 'change' }
  ],
  streamUrl: [
    { required: true, message: '请输入流媒体地址', trigger: 'blur' }
  ],
  streamType: [
    { required: true, message: '请选择流媒体类型', trigger: 'change' }
  ],
  lat: [
    { required: true, message: '请输入纬度', trigger: 'blur' },
    { pattern: /^-?\d+\.?\d*$/, message: '请输入有效的纬度', trigger: 'blur' }
  ],
  lng: [
    { required: true, message: '请输入经度', trigger: 'blur' },
    { pattern: /^-?\d+\.?\d*$/, message: '请输入有效的经度', trigger: 'blur' }
  ]
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    loading.value = true
    
    // 创建摄像头对象
    const newCamera: Camera = {
      id: `camera_${Date.now()}`, // 生成唯一ID
      name: form.name,
      type: form.type as Camera['type'],
      position: {
        lat: parseFloat(form.lat),
        lng: parseFloat(form.lng)
      },
      streamUrl: form.streamUrl,
      streamType: form.streamType as Camera['streamType'],
      resolution: {
        width: form.width,
        height: form.height
      },
      fps: form.fps,
      direction: form.direction,
      status: 'offline', // 新添加的摄像头默认为离线状态
      lastUpdate: new Date().toISOString()
    }
    
    // 添加到store
    cameraStore.addCamera(newCamera)
    
    // 模拟API调用延迟
    await new Promise(resolve => setTimeout(resolve, 500))
    
    ElMessage.success('摄像头添加成功')
    emit('success')
  } catch (error) {
    console.error('添加摄像头失败:', error)
    ElMessage.error('添加摄像头失败')
  } finally {
    loading.value = false
  }
}

const handleCancel = () => {
  emit('cancel')
}
</script>

<style scoped>
:deep(.el-form-item__label) {
  color: var(--text-color);
}

:deep(.el-input__inner),
:deep(.el-select .el-input__inner) {
  background: var(--bg-color-light);
  border-color: var(--border-color);
  color: var(--text-color);
}
</style>
