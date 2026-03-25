# 🐉 OpenDragon 股票仪表盘

> A 股模拟交易系统 · 利弗摩尔原则实践 · 五大市场

## ⚡ 核心功能流程（最重要！）

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           数据流工作流程                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   1️⃣ 交易操作（买入/卖出）                                             │
│       ↓                                                                │
│   2️⃣ 飞书多维表格 "OpenDragon 投资组合"                                 │
│       📋 https://ocnp5whz0ad6.feishu.cn/wiki/Pk17wdNRFicbQpkaYvwcayW0nrb │
│       ↓ 手动同步                                                        │
│   3️⃣ 本地 JSON 文件 (data/trades_*.json)                                │
│       ↓ 前端读取                                                        │
│   4️⃣ 网页端显示 + 实时行情                                             │
│       📡 腾讯财经 API / Yahoo Finance                                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 📁 数据文件说明

| 文件 | 用途 | 市场 |
|:-----|:-----|:-----|
| `data/trades_cn.json` | 交易记录 | A股 |
| `data/trades_hk.json` | 交易记录 | 港股 |
| `data/trades_us.json` | 交易记录 | 美股 |
| `data/trades_ca.json` | 交易记录 | 加股 |
| `data/trades_crypto.json` | 交易记录 | 数字货币 |
| `data/ca_crypto.json` | 实时行情缓存 | 加股/数字货币 |
| `data/indices.json` | 全球指数 | 全部 |

### 📊 数据源配置

| 市场 | 实时行情 | 数据源 | 缓存 |
|:-----|:---------|:-------|:-----|
| A股 | 腾讯财经 API | 直接调用 | - |
| 港股 | 腾讯财经 API | 直接调用 | - |
| 美股 | 腾讯财经 API | 直接调用 | - |
| 加股 | 本地 JSON | Yahoo Finance 抓取 | 每5分钟更新 |
| 数字货币 | 本地 JSON | Yahoo Finance 抓取 | 每5分钟更新 |

**说明：**
- A股/港股/美股：前端直接调用腾讯财经 API 获取实时行情
- 加股/数字货币：后端脚本从 Yahoo Finance 抓取数据 → 存到 `data/ca_crypto.json` → 前端读取本地 JSON（带 `cache: 'no-store'` 避免缓存）

### 🔧 交易后操作流程

**每次买卖股票后，必须执行以下步骤：**

1. **更新飞书多维表格** - 在"OpenDragon 投资组合"表中添加记录
2. **同步本地 JSON** - 更新 `data/trades_{market}.json`
3. **推送 GitHub** - `git add . && git commit && git push`
4. **等待部署** - Cloudflare Pages 自动部署（1-2分钟）

### JSON 文件格式

```json
{
  "timestamp": "2026-03-23T00:00:00.000Z",
  "initialCapital": 1000000,
  "realizedProfit": -10392,
  "holdings": [
    {
      "code": "300750",
      "name": "宁德时代",
      "costPrice": 404.9,
      "quantity": 200,
      "reason": "新能源龙头"
    }
  ],
  "trades": [
    {
      "type": "买入",
      "code": "300750",
      "name": "宁德时代",
      "price": 404.9,
      "quantity": 200,
      "amount": 80980,
      "date": "2026-03-16",
      "reason": "新能源龙头",
      "status": ""
    }
  ]
}
```

---

## 功能特性

- 📜 利弗摩尔十大原则展示
- 📊 持仓实时行情
- 💰 动态盈亏计算
- 📈 资金概览仪表盘
- 📝 操作记录展示
- 🔄 交易日自动刷新
- 📱 响应式设计（手机/PC 适配）

## 技术栈

- Vue 3（CDN 引入，无需构建）
- ECharts 5（图表库）
- 腾讯财经 API / Yahoo Finance（实时行情）
- Cloudflare Pages（免费托管）

## 部署到 Cloudflare Pages

### 步骤 1：上传到 GitHub

```bash
# 初始化 git 仓库
git init
git add .
git commit -m "Initial commit: OpenDragon 股票仪表盘"

# 推送到 GitHub（替换为你的仓库地址）
git remote add origin https://github.com/YOUR_USERNAME/opendragon-dashboard.git
git branch -M main
git push -u origin main
```

### 步骤 2：Cloudflare Pages 部署

1. 登录 https://dash.cloudflare.com
2. 左侧菜单 → **Workers & Pages** → **Create application**
3. 选择 **Pages** 标签 → **Connect to Git**
4. 选择刚才的仓库
5. 配置：
   - **Project name:** `opendragon-dashboard`
   - **Production branch:** `main`
   - **Build command:** (留空)
   - **Build output directory:** `.` (根目录)
6. 点击 **Save and Deploy**

### 步骤 3：绑定自定义域名

1. 进入项目 → **Custom domains**
2. 点击 **Add custom domain**
3. 输入 `www.opendragon.icu`
4. Cloudflare 会自动配置 DNS 和 HTTPS

**完成！** 🎉

---

## 本地开发

```bash
python3 -m http.server 8888
# 访问 http://localhost:8888
```

---

## 飞书多维表格

- **投资组合**: https://ocnp5whz0ad6.feishu.cn/wiki/Pk17wdNRFicbQpkaYvwcayW0nrb
- **候选股票池**: https://ocnp5whz0ad6.feishu.cn/base/EGjabj93JaaGyusF4lXcSLb0nYg

---

---

## 📋 稳定运行规则（2026-03-25 确立）

### ⚠️ 核心原则：飞书表格是唯一数据源

所有修改只在飞书多维表格进行，不要手动编辑 JSON 文件！

### 🔄 自动同步流程

```
飞书多维表格 → sync_feishu_to_json.py（每5分钟） → GitHub → 网页端
```

**已配置定时任务：**
- 每5分钟自动同步飞书数据到GitHub
- 每5分钟自动推送数据到服务器

### ✅ 正确操作规范

| 操作 | 步骤 |
|------|------|
| **买入** | 在飞书表格添加记录，状态选"已建仓" |
| **卖出/止损** | 在飞书表格添加记录，交易类型选"卖出"，状态选"已止损" |
| **充值** | 在飞书表格添加记录，交易类型选"充值" |

### ⚠️ 注意事项

1. **不要复制/重复已有记录** - 会导致持仓显示错误
2. **交易类型和状态必须从下拉框选择** - 不要手动输入
3. **验证流程** - 操作后检查网页端显示，强制刷新 `Ctrl+Shift+R`

### 🔧 常见问题排查

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 持仓显示已平仓的股票 | 飞书表格有重复记录 | 删除重复的持仓记录 |
| 交易类型显示乱码 | 同步脚本未映射选项ID | 已修复（2026-03-25） |
| 实时行情不更新 | 数据未推送到GitHub | 检查自动同步任务 |

### 📞 问题排查命令

```bash
# 检查飞书记录数
curl -s "https://open.feishu.cn/open-apis/bitable/v1/apps/..."

# 检查本地数据
cat data/trades_cn.json | python3 -m json.tool | head -20

# 检查服务器数据
curl -s "https://www.opendragon.icu/data/trades_cn.json"
```

---

## 许可证

MIT