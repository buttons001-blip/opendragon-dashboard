# 雪茄品牌故事功能说明

**创建时间**：2026-04-21  
**维护者**：亨利大管家 👑

---

## 📋 功能概述

在雪茄管理系统的**品吸页面**中显示雪茄品牌的故事介绍，帮助用户了解品牌历史和文化背景。

### 显示位置
- 品吸页面 → 选择雪茄后 → 基本信息下方
- 品牌 Logo 和基本信息卡片之后

### 品牌分类
- 🇨 **古巴品牌**：显示红色"古巴"标记（30 个）
- 🌍 **非古品牌**：显示蓝色"非古"标记（150 个）

---

## 📁 数据文件

### 主数据文件
- **路径**：`test/cigars/data/cigar_brand_stories.json`
- **大小**：52KB
- **记录数**：180 条品牌故事
- **格式**：JSON

### 数据结构
```json
[
  {
    "品牌名称": "Cohiba",
    "类型": "古巴",
    "品牌故事": "1966 年诞生于古巴革命后的传奇品牌..."
  },
  {
    "品牌名称": "Arturo Fuente",
    "类型": "非古",
    "品牌故事": "1912 年由 Arturo Fuente 在古巴创立..."
  }
]
```

### 备份文件
- **路径**：`test/cigars/data/cigar_brand_stories_backup_YYYYMMDD.json`
- **备份策略**：每次更新前手动备份

---

## 🎯 数据来源

### 原始数据
- **来源文件**：`古巴非古雪茄品牌故事表.xlsx`
- **位置**：飞书消息附件 / 本地媒体目录
- **记录数**：180 条（30 古巴 + 150 非古）

### 数据转换
```python
# 使用脚本将 Excel 转换为 JSON
import pandas as pd
import json

df = pd.read_excel('古巴非古雪茄品牌故事表.xlsx')
brand_stories = []
for _, row in df.iterrows():
    brand_stories.append({
        '品牌名称': row['品牌名称'],
        '类型': row['类型'],
        '品牌故事': row['品牌故事']
    })

with open('cigar_brand_stories.json', 'w', encoding='utf-8') as f:
    json.dump(brand_stories, f, ensure_ascii=False, indent=2)
```

---

## 💻 技术实现

### 前端代码位置
- **文件**：`test/cigars/index.html`
- **框架**：Vue 3

### 核心代码逻辑

#### 1. 数据加载
```javascript
// 加载品牌故事数据（无论雪茄数据从哪来都加载）
const brandDataResp = await fetch('./data/cigar_brand_stories.json?t=' + Date.now());
const brandData = await brandDataResp.json();

// 构建品牌故事映射表
brandStories.value = {};
for (const item of brandData) {
  const brandName = item['品牌名称'];
  const type = item['类型'] || '';
  const story = item['品牌故事'];
  
  if (brandName && story) {
    const isCuban = type === '古巴';
    brandStories.value[brandName] = {
      text: story,
      origin: type === '古巴' ? '古巴' : '非古',
      isCuban: isCuban
    };
  }
}
```

#### 2. 计算属性
```javascript
const brandStory = computed(() => {
  if (!selectedRecordForTaste.value) return null;
  const brand = selectedRecordForTaste.value.brand;
  const story = brandStories.value[brand];
  return story || null;
});
```

#### 3. 页面显示
```html
<div v-if="brandStory" class="bg-amber-50 rounded-xl p-4 mb-4">
  <h4 class="font-medium text-amber-800 mb-2">
    📖 品牌故事
    <span v-if="brandStory.isCuban" class="ml-2 px-2 py-0.5 bg-red-200 text-red-800 rounded-full text-xs">🇨 古巴</span>
    <span v-else-if="brandStory.origin" class="ml-2 px-2 py-0.5 bg-blue-200 text-blue-800 rounded-full text-xs">🌍 {{ brandStory.origin }}</span>
  </h4>
  <p class="text-sm text-amber-700 whitespace-pre-line">{{ brandStory.text }}</p>
</div>
```

---

## 📊 数据统计

### 品牌覆盖
| 类型 | 数量 | 占比 |
|------|------|------|
| 古巴品牌 | 30 | 16.7% |
| 非古品牌 | 150 | 83.3% |
| **总计** | **180** | **100%** |

### 与库存匹配
- **雪茄库存品牌数**：71 个
- **有品牌故事的品牌**：51 个
- **覆盖率**：71.8%

### 缺失品牌故事的品牌（20 个）
- VegaFina
- Belinda
- Liga
- Cao
- Blend 42
- Hoyo
- Edmundo Dantes
- EI Rey Del Mundo
- Ezra Zion
- La Escepcion
- ...等

---

## 🔧 维护指南

### 更新品牌故事
1. 准备 Excel 数据文件（包含"品牌名称"、"类型"、"品牌故事"三列）
2. 备份现有数据：
   ```bash
   cp cigar_brand_stories.json cigar_brand_stories_backup_$(date +%Y%m%d).json
   ```
3. 转换 Excel 为 JSON
4. 测试页面显示
5. 提交 Git

### 添加新品牌
1. 在 Excel 中添加新行
2. 确保"品牌名称"与雪茄库存中的品牌名称完全一致
3. 重新生成 JSON 文件

### 调试技巧
1. 打开浏览器控制台（F12）
2. 查看日志：
   - `品牌故事数据加载成功，记录数：180`
   - `品牌故事映射表构建完成：170 个品牌`
   - `brandStory 计算：{brand: "xxx", hasStory: true/false}`
3. 检查网络请求（Network 标签）：
   - `cigar_brand_stories.json` 状态码应为 200

---

## 📝 版本历史

| 日期 | 版本 | 变更内容 |
|------|------|----------|
| 2026-04-21 | v1.0 | 初始版本，添加 180 条品牌故事数据 |
| 2026-04-21 | v1.1 | 修复数据加载时机问题，确保独立加载 |

---

## 🔗 相关链接

- **雪茄管理系统**：https://cigars.opendragon.icu/
- **品吸页面**：https://cigars.opendragon.icu/test/cigars/index.html
- **数据文件**：`test/cigars/data/cigar_brand_stories.json`
- **代码文件**：`test/cigars/index.html`

---

**亨利大管家 👑 — 真诚帮忙，先尝试解决再提问**
