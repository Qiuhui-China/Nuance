// 错误类型常量与映射
export const ERROR_TYPES = {
  vocabulary: {
    label: "词汇提升",
    description: "使用更准确或高级的词汇",
    color: "#4CAF50",  // 绿色
    severity: 1  // 1-3级，1为最轻微
  },
  grammar: {
    label: "语法修正",
    description: "纠正语法结构错误",
    color: "#FF9800",  // 橙色
    severity: 2
  },
  pronunciation: {
    label: "发音建议",
    description: "改进发音或音标标注",
    color: "#2196F3",  // 蓝色
    severity: 1
  },
  expression: {
    label: "表达优化",
    description: "使表达更自然地道",
    color: "#9C27B0",  // 紫色
    severity: 2
  },
  punctuation: {
    label: "标点修正",
    description: "纠正标点符号使用",
    color: "#607D8B",  // 蓝灰色
    severity: 1
  },
  spelling: {
    label: "拼写纠正",
    description: "修正单词拼写错误",
    color: "#F44336",  // 红色
    severity: 1
  },
  word_order: {
    label: "词序调整",
    description: "调整单词或短语顺序",
    color: "#795548",  // 棕色
    severity: 2
  },
  preposition: {
    label: "介词修正",
    description: "纠正介词使用",
    color: "#00BCD4",  // 青色
    severity: 2
  },
  tense: {
    label: "时态纠正",
    description: "修正动词时态",
    color: "#FF5722",  // 深橙色
    severity: 2
  },
  article: {
    label: "冠词修正",
    description: "纠正a/an/the的使用",
    color: "#8BC34A",  // 浅绿色
    severity: 1
  },
  capitalization: {
    label: "大小写修正",
    description: "纠正字母大小写",
    color: "#E91E63",  // 粉红色
    severity: 1
  },
  perfect:{
    label:"非常完美",
    description:"文章非常完美，没有错误",
    color:"#4CAF50",
    severity:0
  }
}

// 按严重程度分类
export const SEVERITY_LEVELS = {
  1: { name: "轻微", icon: "🔵" },
  2: { name: "中等", icon: "🟠" },
  3: { name: "严重", icon: "🔴" }
}

// 获取所有类型标签（用于下拉选择等）
export const ERROR_TYPE_LABELS = Object.entries(ERROR_TYPES).map(
  ([value, config]) => ({
    value,
    label: config.label,
    color: config.color
  })
)


// 默认导出主要配置
export default {
  ERROR_TYPES,
  SEVERITY_LEVELS,
  ERROR_TYPE_LABELS
}