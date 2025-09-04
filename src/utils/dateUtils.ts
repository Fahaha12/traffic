import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'
import relativeTime from 'dayjs/plugin/relativeTime'
import customParseFormat from 'dayjs/plugin/customParseFormat'
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'

// 配置dayjs
dayjs.locale('zh-cn')
dayjs.extend(relativeTime)
dayjs.extend(customParseFormat)
dayjs.extend(utc)
dayjs.extend(timezone)

// 日期格式化工具函数
export const dateUtils = {
  // 格式化日期时间
  formatDateTime: (date: string | Date, format = 'YYYY-MM-DD HH:mm:ss') => {
    return dayjs(date).format(format)
  },

  // 格式化日期
  formatDate: (date: string | Date, format = 'YYYY-MM-DD') => {
    return dayjs(date).format(format)
  },

  // 格式化时间
  formatTime: (date: string | Date, format = 'HH:mm:ss') => {
    return dayjs(date).format(format)
  },

  // 相对时间
  fromNow: (date: string | Date) => {
    return dayjs(date).fromNow()
  },

  // 获取时间戳
  getTimestamp: (date?: string | Date) => {
    return dayjs(date).valueOf()
  },

  // 获取今天的开始时间
  getTodayStart: () => {
    return dayjs().startOf('day').toISOString()
  },

  // 获取今天的结束时间
  getTodayEnd: () => {
    return dayjs().endOf('day').toISOString()
  },

  // 获取昨天的开始时间
  getYesterdayStart: () => {
    return dayjs().subtract(1, 'day').startOf('day').toISOString()
  },

  // 获取昨天的结束时间
  getYesterdayEnd: () => {
    return dayjs().subtract(1, 'day').endOf('day').toISOString()
  },

  // 获取本周的开始时间
  getWeekStart: () => {
    return dayjs().startOf('week').toISOString()
  },

  // 获取本周的结束时间
  getWeekEnd: () => {
    return dayjs().endOf('week').toISOString()
  },

  // 获取本月的开始时间
  getMonthStart: () => {
    return dayjs().startOf('month').toISOString()
  },

  // 获取本月的结束时间
  getMonthEnd: () => {
    return dayjs().endOf('month').toISOString()
  },

  // 获取时间范围
  getTimeRange: (type: 'today' | 'yesterday' | 'week' | 'month' | 'custom', customRange?: { start: string; end: string }) => {
    switch (type) {
      case 'today':
        return {
          start: dateUtils.getTodayStart(),
          end: dateUtils.getTodayEnd()
        }
      case 'yesterday':
        return {
          start: dateUtils.getYesterdayStart(),
          end: dateUtils.getYesterdayEnd()
        }
      case 'week':
        return {
          start: dateUtils.getWeekStart(),
          end: dateUtils.getWeekEnd()
        }
      case 'month':
        return {
          start: dateUtils.getMonthStart(),
          end: dateUtils.getMonthEnd()
        }
      case 'custom':
        return customRange || { start: '', end: '' }
      default:
        return { start: '', end: '' }
    }
  },

  // 判断是否为今天
  isToday: (date: string | Date) => {
    return dayjs(date).isSame(dayjs(), 'day')
  },

  // 判断是否为昨天
  isYesterday: (date: string | Date) => {
    return dayjs(date).isSame(dayjs().subtract(1, 'day'), 'day')
  },

  // 判断是否为本周
  isThisWeek: (date: string | Date) => {
    return dayjs(date).isSame(dayjs(), 'week')
  },

  // 判断是否为本月
  isThisMonth: (date: string | Date) => {
    return dayjs(date).isSame(dayjs(), 'month')
  },

  // 计算时间差（毫秒）
  diff: (date1: string | Date, date2: string | Date, unit: dayjs.ManipulateType = 'millisecond') => {
    return dayjs(date1).diff(dayjs(date2), unit)
  },

  // 添加时间
  add: (date: string | Date, amount: number, unit: dayjs.ManipulateType) => {
    return dayjs(date).add(amount, unit).toISOString()
  },

  // 减去时间
  subtract: (date: string | Date, amount: number, unit: dayjs.ManipulateType) => {
    return dayjs(date).subtract(amount, unit).toISOString()
  },

  // 获取时间段的开始和结束
  getRange: (date: string | Date, unit: dayjs.OpUnitType) => {
    return {
      start: dayjs(date).startOf(unit).toISOString(),
      end: dayjs(date).endOf(unit).toISOString()
    }
  },

  // 格式化持续时间
  formatDuration: (milliseconds: number) => {
    const duration = dayjs.duration(milliseconds)
    const hours = Math.floor(duration.asHours())
    const minutes = duration.minutes()
    const seconds = duration.seconds()

    if (hours > 0) {
      return `${hours}小时${minutes}分钟`
    } else if (minutes > 0) {
      return `${minutes}分钟${seconds}秒`
    } else {
      return `${seconds}秒`
    }
  },

  // 获取当前时间
  now: () => {
    return dayjs().toISOString()
  },

  // 获取当前时间戳
  nowTimestamp: () => {
    return dayjs().valueOf()
  }
}

export default dateUtils
