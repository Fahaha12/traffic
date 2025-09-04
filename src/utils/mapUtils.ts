// 地图工具函数

// 计算两点之间的距离（米）
export const calculateDistance = (
  lat1: number,
  lng1: number,
  lat2: number,
  lng2: number
): number => {
  const R = 6371000 // 地球半径（米）
  const dLat = toRadians(lat2 - lat1)
  const dLng = toRadians(lng2 - lng1)
  
  const a = 
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRadians(lat1)) * Math.cos(toRadians(lat2)) *
    Math.sin(dLng / 2) * Math.sin(dLng / 2)
  
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return R * c
}

// 角度转弧度
const toRadians = (degrees: number): number => {
  return degrees * (Math.PI / 180)
}

// 弧度转角度
const toDegrees = (radians: number): number => {
  return radians * (180 / Math.PI)
}

// 计算两点之间的方位角
export const calculateBearing = (
  lat1: number,
  lng1: number,
  lat2: number,
  lng2: number
): number => {
  const dLng = toRadians(lng2 - lng1)
  const lat1Rad = toRadians(lat1)
  const lat2Rad = toRadians(lat2)
  
  const y = Math.sin(dLng) * Math.cos(lat2Rad)
  const x = 
    Math.cos(lat1Rad) * Math.sin(lat2Rad) -
    Math.sin(lat1Rad) * Math.cos(lat2Rad) * Math.cos(dLng)
  
  let bearing = toDegrees(Math.atan2(y, x))
  return (bearing + 360) % 360
}

// 根据距离和方位角计算目标点
export const calculateDestination = (
  lat: number,
  lng: number,
  distance: number,
  bearing: number
): { lat: number; lng: number } => {
  const R = 6371000 // 地球半径（米）
  const latRad = toRadians(lat)
  const lngRad = toRadians(lng)
  const bearingRad = toRadians(bearing)
  
  const newLatRad = Math.asin(
    Math.sin(latRad) * Math.cos(distance / R) +
    Math.cos(latRad) * Math.sin(distance / R) * Math.cos(bearingRad)
  )
  
  const newLngRad = lngRad + Math.atan2(
    Math.sin(bearingRad) * Math.sin(distance / R) * Math.cos(latRad),
    Math.cos(distance / R) - Math.sin(latRad) * Math.sin(newLatRad)
  )
  
  return {
    lat: toDegrees(newLatRad),
    lng: toDegrees(newLngRad)
  }
}

// 计算多边形的中心点
export const calculatePolygonCenter = (points: Array<{ lat: number; lng: number }>): { lat: number; lng: number } => {
  if (points.length === 0) {
    return { lat: 0, lng: 0 }
  }
  
  if (points.length === 1) {
    return points[0]
  }
  
  let totalLat = 0
  let totalLng = 0
  
  points.forEach(point => {
    totalLat += point.lat
    totalLng += point.lng
  })
  
  return {
    lat: totalLat / points.length,
    lng: totalLng / points.length
  }
}

// 计算多边形的边界框
export const calculateBounds = (points: Array<{ lat: number; lng: number }>): {
  north: number
  south: number
  east: number
  west: number
} => {
  if (points.length === 0) {
    return { north: 0, south: 0, east: 0, west: 0 }
  }
  
  let north = points[0].lat
  let south = points[0].lat
  let east = points[0].lng
  let west = points[0].lng
  
  points.forEach(point => {
    north = Math.max(north, point.lat)
    south = Math.min(south, point.lat)
    east = Math.max(east, point.lng)
    west = Math.min(west, point.lng)
  })
  
  return { north, south, east, west }
}

// 判断点是否在多边形内
export const isPointInPolygon = (
  point: { lat: number; lng: number },
  polygon: Array<{ lat: number; lng: number }>
): boolean => {
  let inside = false
  
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    if (
      polygon[i].lng > point.lng !== polygon[j].lng > point.lng &&
      point.lat < (polygon[j].lat - polygon[i].lat) * (point.lng - polygon[i].lng) / (polygon[j].lng - polygon[i].lng) + polygon[i].lat
    ) {
      inside = !inside
    }
  }
  
  return inside
}

// 计算轨迹的总距离
export const calculateTrajectoryDistance = (points: Array<{ lat: number; lng: number }>): number => {
  if (points.length < 2) {
    return 0
  }
  
  let totalDistance = 0
  
  for (let i = 1; i < points.length; i++) {
    totalDistance += calculateDistance(
      points[i - 1].lat,
      points[i - 1].lng,
      points[i].lat,
      points[i].lng
    )
  }
  
  return totalDistance
}

// 计算轨迹的平均速度
export const calculateAverageSpeed = (
  points: Array<{ lat: number; lng: number; timestamp: string }>
): number => {
  if (points.length < 2) {
    return 0
  }
  
  const totalDistance = calculateTrajectoryDistance(points)
  const startTime = new Date(points[0].timestamp).getTime()
  const endTime = new Date(points[points.length - 1].timestamp).getTime()
  const totalTime = (endTime - startTime) / 1000 // 转换为秒
  
  if (totalTime === 0) {
    return 0
  }
  
  return totalDistance / totalTime // 米/秒
}

// 简化轨迹（道格拉斯-普克算法）
export const simplifyTrajectory = (
  points: Array<{ lat: number; lng: number }>,
  tolerance: number = 0.0001
): Array<{ lat: number; lng: number }> => {
  if (points.length <= 2) {
    return points
  }
  
  const simplified: Array<{ lat: number; lng: number }> = []
  
  const douglasPeucker = (start: number, end: number) => {
    let maxDistance = 0
    let maxIndex = 0
    
    for (let i = start + 1; i < end; i++) {
      const distance = perpendicularDistance(points[i], points[start], points[end])
      if (distance > maxDistance) {
        maxDistance = distance
        maxIndex = i
      }
    }
    
    if (maxDistance > tolerance) {
      douglasPeucker(start, maxIndex)
      douglasPeucker(maxIndex, end)
    } else {
      simplified.push(points[end])
    }
  }
  
  simplified.push(points[0])
  douglasPeucker(0, points.length - 1)
  
  return simplified
}

// 计算点到线段的垂直距离
const perpendicularDistance = (
  point: { lat: number; lng: number },
  lineStart: { lat: number; lng: number },
  lineEnd: { lat: number; lng: number }
): number => {
  const A = point.lat - lineStart.lat
  const B = point.lng - lineStart.lng
  const C = lineEnd.lat - lineStart.lat
  const D = lineEnd.lng - lineStart.lng
  
  const dot = A * C + B * D
  const lenSq = C * C + D * D
  
  if (lenSq === 0) {
    return Math.sqrt(A * A + B * B)
  }
  
  const param = dot / lenSq
  
  let xx, yy
  
  if (param < 0) {
    xx = lineStart.lat
    yy = lineStart.lng
  } else if (param > 1) {
    xx = lineEnd.lat
    yy = lineEnd.lng
  } else {
    xx = lineStart.lat + param * C
    yy = lineStart.lng + param * D
  }
  
  const dx = point.lat - xx
  const dy = point.lng - yy
  
  return Math.sqrt(dx * dx + dy * dy)
}

// 格式化距离
export const formatDistance = (distance: number): string => {
  if (distance < 1000) {
    return `${Math.round(distance)}米`
  } else {
    return `${(distance / 1000).toFixed(2)}公里`
  }
}

// 格式化速度
export const formatSpeed = (speed: number): string => {
  if (speed < 1) {
    return `${Math.round(speed * 1000)}毫米/秒`
  } else if (speed < 1000) {
    return `${speed.toFixed(2)}米/秒`
  } else {
    return `${(speed / 1000).toFixed(2)}公里/秒`
  }
}

// 获取地图缩放级别对应的实际距离
export const getZoomLevelDistance = (zoom: number): number => {
  // 基于Web墨卡托投影的近似计算
  const earthCircumference = 40075017 // 地球周长（米）
  return earthCircumference / Math.pow(2, zoom + 8)
}

// 根据距离获取合适的缩放级别
export const getZoomLevelFromDistance = (distance: number): number => {
  const earthCircumference = 40075017
  return Math.log2(earthCircumference / distance) - 8
}

export default {
  calculateDistance,
  calculateBearing,
  calculateDestination,
  calculatePolygonCenter,
  calculateBounds,
  isPointInPolygon,
  calculateTrajectoryDistance,
  calculateAverageSpeed,
  simplifyTrajectory,
  formatDistance,
  formatSpeed,
  getZoomLevelDistance,
  getZoomLevelFromDistance
}
