# 雪茄库存管理系统 - 完整备份

**备份时间**：2026-04-22 09:25  
**数据源**：Cloudflare D1 数据库  
**总记录数**：1454 条

---

## 数据库结构

### cigars 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT PRIMARY KEY | 飞书记录 ID |
| brand | TEXT NOT NULL | 品牌 |
| model | TEXT NOT NULL | 型号 |
| origin | TEXT | 产地 |
| quantity | INTEGER | 数量 |
| ringGauge | REAL | 环径 |
| length | REAL | 长度 |
| price | REAL | 现单价 |
| total_price | REAL | 预估总价 |
| specification | TEXT | 规格 |
| year | INTEGER | 生产日期 |
| arrived | TEXT | 到货 |
| storageLocation | TEXT | 地点 |
| purchaseLocation | TEXT | 购买地点 |
| packaging | TEXT | 包装 |
| strength | TEXT | 强度等级 |
| flavors | TEXT | 主要风味（JSON） |
| tastingNotes | TEXT | 品吸反馈 |
| logo | TEXT | Logo 路径 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### 索引

- `idx_brand` - 品牌索引
- `idx_origin` - 产地索引
- `idx_storage` - 地点索引
- `idx_year` - 年份索引

---

## 品牌统计（Top 20）

| 品牌 | 记录数 |
|------|--------|
| Cohiba | 89 |
| Montecristo | 76 |
| Romeo y Julieta | 68 |
| Partagas | 54 |
| Punch | 42 |
| Davidoff | 38 |
| Arturo Fuente | 38 |
| Padron | 35 |
| My Father | 32 |
| Arturo Fuente Opus X | 32 |
| H.Upmann | 28 |
| Bolivar | 25 |
| Fonseca | 24 |
| Vegas Robaina | 22 |
| La Gloria Cubana | 20 |
| Trinidad | 18 |
| Hoyo | 16 |
| San Cristobal | 15 |
| VegaFina | 14 |
| Cuaba | 12 |

---

## 产地分布

| 产地 | 记录数 |
|------|--------|
| 古巴 | 980 |
| 非古 | 320 |
| 多米尼加共和国 | 45 |
| 尼加拉瓜 | 38 |
| 洪都拉斯 | 25 |
| 其他 | 46 |

---

## 包装分布

| 包装 | 记录数 |
|------|--------|
| 木盒 | 520 |
| 纸盒 | 380 |
| 铝管 | 210 |
| 铁盒 | 150 |
| 罐装 | 95 |
| 散支 | 65 |
| 保湿盒 | 24 |
| 其他 | 10 |

---

## 强度等级分布

| 强度等级 | 记录数 |
|----------|--------|
| 中等 | 420 |
| 中等至浓郁 | 380 |
| 浓郁 | 310 |
| 温和至中等 | 180 |
| 中等至偏浓 | 120 |
| 偏浓 | 44 |

---

## 数据存储

### D1 数据库
- **数据库名称**：cigars-db
- **数据库 ID**：8aab2131-8ff2-4834-906a-e521670577a0
- **区域**：APAC（亚太地区）
- **记录数**：1454 条
- **存储大小**：约 2.3 MB

### 同步配置
- **D1 → 飞书**：每小时自动同步
- **飞书 → D1**：手动触发
- **同步脚本**：`scripts/sync_d1_to_feishu.py`

---

## 功能清单

### ✅ 已实现
- [x] 记录列表查看（分页/搜索）
- [x] 单条记录查看
- [x] 记录编辑保存
- [x] 新增记录
- [x] 删除记录
- [x] D1 数据库存储
- [x] 飞书反向同步
- [x] 品牌/产地/包装筛选
- [x] 响应式 UI（手机/PC）

### 🔄 开发中
- [ ] Logo 上传（需要 R2 存储）
- [ ] 记录标签系统
- [ ] 品吸记录管理
- [ ] 品牌故事管理

### 📋 计划中
- [ ] 批量导入/导出
- [ ] 数据统计报表
- [ ] 价格趋势分析
- [ ] 库存预警

---

## API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/cigars/list` | GET | 获取列表（支持分页/搜索） |
| `/api/cigars/get?id=xxx` | GET | 获取单条记录 |
| `/api/cigars/create` | POST | 创建新记录 |
| `/api/cigars/update` | POST | 更新记录 |
| `/api/cigars/delete` | POST | 删除记录 |

---

## 技术栈

- **前端**：Vue 3 + Tailwind CSS
- **后端**：Cloudflare Workers + Pages Functions
- **数据库**：Cloudflare D1 (SQLite)
- **存储**：Cloudflare Pages (静态文件)
- **同步**：飞书 API + Python 脚本

---

## 部署信息

- **域名**：cigars.opendragon.icu
- **Pages 项目**：cigars
- **D1 数据库**：cigars-db
- **GitHub 仓库**：buttons001-blip/opendragon-dashboard
- **自动部署**：Git Push → Cloudflare Pages

---

**备份完成** ✅
