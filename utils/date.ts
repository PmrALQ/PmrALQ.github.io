/**
 * 统一日期格式化工具。
 *
 * 原为各组件内重复定义的局部函数，集中抽至此处复用。
 * 保持与组件内原实现完全一致的行为：
 * - 中文环境 → zh-CN，其他语言 → en-US
 * - 通过 options 控制年份显示与「月」的格式（short / long）
 */

export interface FormatDateOptions {
  /** 是否显示年份，默认 true */
  year?: boolean
  /** 月份格式：'short' = 缩写（如「2月」/「Feb」），'long' = 完整（如「二月」/「February」），默认 'short' */
  month?: 'short' | 'long'
}

export function formatDate(dateStr: string, options: FormatDateOptions = {}): string {
  const date = new Date(dateStr)
  if (Number.isNaN(date.getTime())) return dateStr

  const { year = true, month = 'short' } = options
  const formatOptions: Intl.DateTimeFormatOptions = { day: 'numeric', month }
  if (year) formatOptions.year = 'numeric'

  const locale = useI18n().locale.value
  return date.toLocaleDateString(locale === 'zh' ? 'zh-CN' : 'en-US', formatOptions)
}
