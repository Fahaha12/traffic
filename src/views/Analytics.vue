<template>
  <div class="analytics-view">
    <LayoutHeader />
    <div class="analytics-content">
      <LayoutSidebar />
      <div class="main-content">
        <div class="analytics-header">
          <h1>数据分析</h1>
          <div class="time-range-selector">
            <el-date-picker
              v-model="timeRange"
              type="datetimerange"
              range-separator="至"
              start-placeholder="开始时间"
              end-placeholder="结束时间"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DD HH:mm:ss"
              @change="handleTimeRangeChange"
            />
          </div>
        </div>
        
        <div class="analytics-stats" v-loading="loading">
          <el-row :gutter="20">
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-content">
                  <div class="stat-icon total">
                    <el-icon><Truck /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-number">{{ totalVehicles }}</div>
                    <div class="stat-label">总车辆数</div>
                  </div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-content">
                  <div class="stat-icon suspicious">
                    <el-icon><Warning /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-number">{{ suspiciousCount }}</div>
                    <div class="stat-label">可疑车辆</div>
                  </div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-content">
                  <div class="stat-icon alerts">
                    <el-icon><Bell /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-number">{{ alertCount }}</div>
                    <div class="stat-label">告警数量</div>
                  </div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-content">
                  <div class="stat-icon avg-speed">
                    <el-icon><Odometer /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-number">{{ averageSpeed }}</div>
                    <div class="stat-label">平均速度(km/h)</div>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
        
        <div class="analytics-charts" v-loading="loading">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card class="chart-card">
                <template #header>
                  <div class="card-header">
                    <span>车辆类型分布</span>
                    <el-button type="text" @click="refreshVehicleTypeChart">刷新</el-button>
                  </div>
                </template>
                <div class="chart-container">
                  <v-chart 
                    :option="vehicleTypeChartOption" 
                    :style="{ height: '300px' }"
                    autoresize
                  />
                </div>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card class="chart-card">
                <template #header>
                  <div class="card-header">
                    <span>每小时车流量</span>
                    <el-button type="text" @click="refreshTrafficFlowChart">刷新</el-button>
                  </div>
                </template>
                <div class="chart-container">
                  <v-chart 
                    :option="trafficFlowChartOption" 
                    :style="{ height: '300px' }"
                    autoresize
                  />
                </div>
              </el-card>
            </el-col>
          </el-row>
          
          <el-row :gutter="20" style="margin-top: 20px;">
            <el-col :span="24">
              <el-card class="chart-card">
                <template #header>
                  <div class="card-header">
                    <span>可疑车辆趋势</span>
                    <el-button type="text" @click="refreshSuspiciousTrendChart">刷新</el-button>
                  </div>
                </template>
                <div class="chart-container">
                  <v-chart 
                    :option="suspiciousTrendChartOption" 
                    :style="{ height: '400px' }"
                    autoresize
                  />
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
        
        <div class="analytics-tables">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card class="table-card">
                <template #header>
                  <div class="card-header">
                    <span>最新告警</span>
                    <el-button type="text" @click="goToAlerts">查看全部</el-button>
                  </div>
                </template>
                <el-table :data="recentAlerts" style="width: 100%">
                  <el-table-column prop="message" label="告警内容" min-width="200" show-overflow-tooltip />
                  <el-table-column prop="type" label="类型" width="100">
                    <template #default="{ row }">
                      <el-tag :type="getAlertType(row.type)" size="small">
                        {{ getAlertTypeText(row.type) }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="timestamp" label="时间" width="150">
                    <template #default="{ row }">
                      {{ formatTime(row.timestamp) }}
                    </template>
                  </el-table-column>
                  <el-table-column label="操作" width="80">
                    <template #default="{ row }">
                      <el-button type="text" size="small" @click="viewAlert(row)">
                        查看
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card class="table-card">
                <template #header>
                  <div class="card-header">
                    <span>摄像头状态统计</span>
                    <el-button type="text" @click="refreshCameraStats">刷新</el-button>
                  </div>
                </template>
                <el-table :data="cameraStats" style="width: 100%">
                  <el-table-column prop="name" label="摄像头名称" min-width="150" show-overflow-tooltip />
                  <el-table-column prop="type" label="类型" width="100">
                    <template #default="{ row }">
                      {{ getCameraTypeText(row.type) }}
                    </template>
                  </el-table-column>
                  <el-table-column prop="status" label="状态" width="100">
                    <template #default="{ row }">
                      <el-tag :type="getStatusType(row.status)" size="small">
                        {{ getStatusText(row.status) }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="vehicleCount" label="检测车辆数" width="120" />
                  <el-table-column label="操作" width="80">
                    <template #default="{ row }">
                      <el-button type="text" size="small" @click="viewCamera(row)">
                        查看
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, LineChart, BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import { useVehicleStore } from '@/stores/vehicle'
import { useCameraStore } from '@/stores/camera'
import { analyticsAPI } from '@/api/backend'
import LayoutHeader from '@/components/Layout/Header.vue'
import LayoutSidebar from '@/components/Layout/Sidebar.vue'
import { dateUtils } from '@/utils/dateUtils'

// 注册ECharts组件
use([
  CanvasRenderer,
  PieChart,
  LineChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const router = useRouter()
const vehicleStore = useVehicleStore()
const cameraStore = useCameraStore()

const timeRange = ref<[string, string]>([
  dateUtils.getTodayStart(),
  dateUtils.getTodayEnd()
])

// 统计数据
const totalVehicles = ref(0)
const suspiciousCount = ref(0)
const alertCount = ref(0)
const averageSpeed = ref(0)
const loading = ref(false)

// 图表配置
const vehicleTypeChartOption = reactive({
  title: {
    text: '车辆类型分布',
    left: 'center',
    textStyle: { color: '#fff' }
  },
  tooltip: {
    trigger: 'item',
    formatter: '{a} <br/>{b}: {c} ({d}%)'
  },
  legend: {
    orient: 'vertical',
    left: 'left',
    top: 'center',
    textStyle: { color: '#fff' },
    itemGap: 15,
    itemWidth: 20,
    itemHeight: 14
  },
  series: [
    {
      name: '车辆类型',
      type: 'pie',
      radius: '50%',
      data: [
        { value: 335, name: '轿车' },
        { value: 310, name: '卡车' },
        { value: 234, name: '公交车' },
        { value: 135, name: '摩托车' }
      ],
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }
  ]
})

const trafficFlowChartOption = reactive({
  title: {
    text: '每小时车流量',
    left: 'center',
    textStyle: { color: '#fff' }
  },
  tooltip: {
    trigger: 'axis'
  },
  xAxis: {
    type: 'category',
    data: ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00'],
    axisLabel: { color: '#fff' }
  },
  yAxis: {
    type: 'value',
    axisLabel: { color: '#fff' }
  },
  series: [
    {
      name: '车流量',
      type: 'line',
      data: [120, 200, 150, 80, 70, 110, 130, 90, 100, 140, 160, 180],
      smooth: true,
      itemStyle: {
        color: '#409eff'
      }
    }
  ]
})

const suspiciousTrendChartOption = reactive({
  title: {
    text: '可疑车辆趋势',
    left: 'center',
    textStyle: { color: '#fff' }
  },
  tooltip: {
    trigger: 'axis'
  },
  legend: {
    data: ['可疑车辆', '告警数量'],
    textStyle: { color: '#fff' },
    top: '10%',
    left: 'center',
    orient: 'horizontal',
    itemGap: 30,
    itemWidth: 20,
    itemHeight: 14
  },
  grid: {
    top: '25%',
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
    axisLabel: { color: '#fff' }
  },
  yAxis: {
    type: 'value',
    axisLabel: { color: '#fff' }
  },
  series: [
    {
      name: '可疑车辆',
      type: 'bar',
      data: [2, 3, 1, 4, 2, 1, 3],
      itemStyle: {
        color: '#f56c6c'
      }
    },
    {
      name: '告警数量',
      type: 'line',
      data: [5, 8, 3, 12, 6, 4, 9],
      itemStyle: {
        color: '#e6a23c'
      }
    }
  ]
})

// 表格数据
const recentAlerts = ref<any[]>([])
const cameraStats = ref<any[]>([])
const dashboardData = ref<any>({})

// 方法
const handleTimeRangeChange = () => {
  // 根据时间范围刷新数据
  refreshAllData()
}

const loadDashboardData = async () => {
  try {
    const response = await analyticsAPI.getDashboardData()
    dashboardData.value = response.data
    
    // 更新统计数据
    totalVehicles.value = response.data.vehicles?.total || 0
    suspiciousCount.value = response.data.vehicles?.suspicious || 0
    alertCount.value = response.data.alerts?.total || 0
    averageSpeed.value = 0 // 暂时设为0，需要从检测数据计算
    
    // 更新最近告警
    recentAlerts.value = response.data.recentAlerts || []
    
    // 更新摄像头统计
    cameraStats.value = (response.data.recentCameras || []).map((camera: any) => ({
      ...camera,
      vehicleCount: Math.floor(Math.random() * 100) // 暂时使用随机数据
    }))
  } catch (error) {
    console.error('获取仪表板数据失败:', error)
  }
}

const refreshAllData = async () => {
  try {
    loading.value = true
    // 获取仪表板数据
    await loadDashboardData()
    // 获取图表数据
    await Promise.all([
      refreshVehicleTypeChart(),
      refreshTrafficFlowChart(),
      refreshSuspiciousTrendChart(),
      refreshCameraStats()
    ])
  } catch (error) {
    console.error('刷新数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 车辆类型中文映射
const vehicleTypeMap: Record<string, string> = {
  'car': '轿车',
  'truck': '卡车',
  'bus': '公交车',
  'motorcycle': '摩托车',
  'bicycle': '自行车',
  'unknown': '未知',
  'suv': 'SUV',
  'van': '面包车',
  'taxi': '出租车',
  'ambulance': '救护车',
  'fire_truck': '消防车',
  'police_car': '警车'
}

const refreshVehicleTypeChart = async () => {
  try {
    const response = await analyticsAPI.getVehicleAnalysis()
    const rawData = response.data.typeStats || []
    
    // 将英文字段名转换为中文显示
    const data = rawData.map((item: any) => ({
      value: item.value || item.count || 0,
      name: vehicleTypeMap[item.name] || item.name || '未知'
    }))
    
    vehicleTypeChartOption.series[0].data = data
  } catch (error) {
    console.error('获取车辆类型数据失败:', error)
    // 使用默认数据
    const data = [
      { value: 0, name: '轿车' },
      { value: 0, name: '卡车' },
      { value: 0, name: '公交车' },
      { value: 0, name: '摩托车' }
    ]
    vehicleTypeChartOption.series[0].data = data
  }
}

const refreshTrafficFlowChart = async () => {
  try {
    const params = {
      start_time: timeRange.value[0],
      end_time: timeRange.value[1]
    }
    const response = await analyticsAPI.getTrafficFlow(params)
    const data = response.data.data || []
    trafficFlowChartOption.series[0].data = data
    trafficFlowChartOption.xAxis.data = response.data.timeLabels || []
  } catch (error) {
    console.error('获取交通流量数据失败:', error)
    // 使用默认数据
    const data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    trafficFlowChartOption.series[0].data = data
  }
}

const refreshSuspiciousTrendChart = async () => {
  try {
    const response = await analyticsAPI.getVehicleAnalysis()
    const suspiciousTrend = response.data.suspiciousTrend || { dates: [], data: [] }
    const alertTrend = response.data.alertTrend || { dates: [], data: [] }
    
    // 生成最近7天的数据
    const dates = []
    const suspiciousData = []
    const alertData = []
    
    for (let i = 6; i >= 0; i--) {
      const date = new Date()
      date.setDate(date.getDate() - i)
      const dateStr = date.toISOString().split('T')[0]
      dates.push(dateStr)
      
      // 查找对应日期的数据
      const suspiciousIndex = suspiciousTrend.dates?.indexOf(dateStr) || -1
      const alertIndex = alertTrend.dates?.indexOf(dateStr) || -1
      
      suspiciousData.push(suspiciousIndex >= 0 ? suspiciousTrend.data[suspiciousIndex] : 0)
      alertData.push(alertIndex >= 0 ? alertTrend.data[alertIndex] : 0)
    }
    
    suspiciousTrendChartOption.xAxis.data = dates
    suspiciousTrendChartOption.series[0].data = suspiciousData
    suspiciousTrendChartOption.series[1].data = alertData
  } catch (error) {
    console.error('获取可疑车辆趋势数据失败:', error)
    // 使用默认数据
    const suspiciousData = [0, 0, 0, 0, 0, 0, 0]
    const alertData = [0, 0, 0, 0, 0, 0, 0]
    suspiciousTrendChartOption.series[0].data = suspiciousData
    suspiciousTrendChartOption.series[1].data = alertData
  }
}

const refreshCameraStats = async () => {
  try {
    // 摄像头统计已经在loadDashboardData中获取
    console.log('摄像头统计已更新')
  } catch (error) {
    console.error('刷新摄像头统计失败:', error)
  }
}

const goToAlerts = () => {
  // 跳转到告警页面
  console.log('跳转到告警页面')
}

const viewAlert = (alert: any) => {
  console.log('查看告警:', alert)
}

const viewCamera = (camera: any) => {
  router.push(`/cameras?camera=${camera.id}`)
}

const getAlertType = (type: string) => {
  switch (type) {
    case 'suspicious': return 'warning'
    case 'violation': return 'danger'
    case 'emergency': return 'danger'
    default: return 'info'
  }
}

const getAlertTypeText = (type: string) => {
  switch (type) {
    case 'suspicious': return '可疑'
    case 'violation': return '违规'
    case 'emergency': return '紧急'
    default: return '未知'
  }
}

const getCameraTypeText = (type: string) => {
  switch (type) {
    case 'traffic': return '交通监控'
    case 'surveillance': return '安防监控'
    case 'speed': return '测速监控'
    default: return '未知'
  }
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'online': return 'success'
    case 'offline': return 'danger'
    case 'maintenance': return 'warning'
    default: return 'info'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'online': return '在线'
    case 'offline': return '离线'
    case 'maintenance': return '维护中'
    default: return '未知'
  }
}

const formatTime = (timestamp: string) => {
  return dateUtils.formatTime(timestamp)
}

onMounted(() => {
  refreshAllData()
})
</script>

<style scoped>
.analytics-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.analytics-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.main-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: var(--bg-color);
}

.analytics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.analytics-header h1 {
  color: var(--text-color);
  margin: 0;
}

.analytics-stats {
  margin-bottom: 20px;
}

.stat-card {
  background: var(--bg-color-light);
  border: 1px solid var(--border-color);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.stat-icon.total {
  background: var(--primary-color);
}

.stat-icon.suspicious {
  background: var(--warning-color);
}

.stat-icon.alerts {
  background: var(--danger-color);
}

.stat-icon.avg-speed {
  background: var(--success-color);
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: var(--text-color);
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: var(--text-color-light);
  margin-top: 5px;
}

.analytics-charts {
  margin-bottom: 20px;
}

.chart-card,
.table-card {
  background: var(--bg-color-light);
  border: 1px solid var(--border-color);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  width: 100%;
}

:deep(.echarts) {
  background: transparent;
}

/* 表格样式优化 */
:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-table th),
:deep(.el-table td) {
  padding: 8px 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

:deep(.el-table .cell) {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.4;
}

:deep(.el-table .el-table__body-wrapper) {
  overflow-x: auto;
}

/* 表格卡片样式 */
.table-card {
  height: 400px;
  overflow: hidden;
}

.table-card :deep(.el-card__body) {
  height: calc(100% - 60px);
  padding: 0;
}

.table-card :deep(.el-table) {
  height: 100%;
}

.table-card :deep(.el-table__body-wrapper) {
  max-height: 300px;
  overflow-y: auto;
}
</style>
