# OpenDragon 股票看板 - 完整备份文档

**备份时间**: 2026-03-28 13:21  
**备份员**: 亨利大管家 👑  
**版本**: v1.0

---

## 📋 目录

1. [系统架构](#系统架构)
2. [数据流程](#数据流程)
3. [核心程序](#核心程序)
4. [定时任务](#定时任务)
5. [配置信息](#配置信息)
6. [前端功能](#前端功能)
7. [交易规则](#交易规则)
8. [故障排查](#故障排查)
9. [恢复指南](#恢复指南)

---

## 系统架构

### 整体架构

```
飞书多维表格 (唯一数据源)
    ↓ 每 5 分钟
Python 同步脚本
    ↓
本地 JSON 文件
    ↓ Git 自动提交 (每 5 分钟)
GitHub 仓库
    ↓ 自动部署
Cloudflare Pages
    ↓
前端网页 (https://www.opendragon.icu)
    ↓ 30 秒轮询
自动检测更新
```

### 组件说明

| 组件 | 位置 | 说明 |
|------|------|------|
| 飞书表格 | https://ocnp5whz0ad6.feishu.cn/wiki/GMj6w7aTFivN3hkSBgHc5W7Anoe | 唯一数据源 |
| 同步脚本 | `/home/admin/.openclaw/workspace/stock-dashboard/scripts/sync_openclaw_to_json.py` | 数据同步 |
| 本地 JSON | `/home/admin/.openclaw/workspace/stock-dashboard/data/trades_*.json` | 5 个市场数据 |
| GitHub 仓库 | https://github.com/buttons001-blip/opendragon-dashboard | 代码+数据托管 |
| 前端页面 | https://www.opendragon.icu | Cloudflare Pages 部署 |

---

## 数据流程

### 1. 数据同步流程

**脚本**: `scripts/sync_openclaw_to_json.py`

**执行频率**: 每 5 分钟

**流程**:
1. 获取飞书 API token
2. 读取飞书表格所有记录（分页，每页 500 条）
3. 按市场分组（A 股、港股、美股、加股、数字货币）
4. 计算每个市场的：
   - 初始资金（充值记录）
   - 持仓（买入 - 卖出）
   - 已实现盈亏（卖出盈亏）
   - 交易记录（所有记录）
5. 保存为 JSON 文件（覆盖旧数据）

**关键字段处理**:
```python
# 去除所有空格（修复"A 股"问题）
market = fields.get('市场', '').replace(' ', '')
trade_type = fields.get('操作类型', '').replace(' ', '')
code = fields.get('代码', '').replace(' ', '')
name = fields.get('名称', '').replace(' ', '')
```

**日期处理**:
```python
# 飞书时间戳转日期（毫秒）
date_obj = datetime.fromtimestamp(date_val / 1000)
date = date_obj.strftime('%Y-%m-%d')

# 修复 2024/2025 年为 2026 年（测试数据）
if date.startswith('2024') or date.startswith('2025'):
    date = '2026' + date[4:]
```

---

### 2. Git 自动提交流程

**Cron 配置**:
```bash
*/5 * * * * cd /home/admin/.openclaw/workspace/stock-dashboard && \
  git add data/ && \
  if ! git diff-index --quiet HEAD -- data/; then \
    git commit -m "auto: sync data $(date +\%Y-\%m-\%d \%H:\%M)" && \
    git push >> /home/admin/.openclaw/workspace/git_auto_commit.log 2>&1; \
  fi
```

**逻辑**:
1. 进入 stock-dashboard 目录
2. git add data/（添加数据文件）
3. 检查是否有变化（git diff-index --quiet HEAD）
4. 如果有变化：commit 并 push
5. 日志输出到 git_auto_commit.log

**日志位置**: `/home/admin/.openclaw/workspace/git_auto_commit.log`

---

### 3. 前端数据加载流程

**页面加载**:
1. Vue.js 初始化
2. 调用 `loadFeishuData()` 从 JSON 文件读取数据
3. 调用 `processTradeData()` 处理数据
4. 计算持仓、盈亏、收益率
5. 渲染页面

**自动轮询**:
```javascript
// 每 30 秒检查更新
this.autoRefreshTimer = setInterval(() => {
    this.checkForUpdates();
}, 30000);

async checkForUpdates() {
    const response = await fetch('data/trades_cn.json?t=' + Date.now());
    const data = await response.json();
    
    if (data.timestamp !== this.lastVersion) {
        await this.loadFeishuData();
        this.showUpdateToast('📊 数据已更新');
    }
}
```

**手动刷新**:
```javascript
async refreshData() {
    this.refreshing = true;
    try {
        const response = await fetch('api/trades_realtime.php?t=' + Date.now());
        const data = await response.json();
        
        if (data.success) {
            this.processTradeData(data);
            this.showUpdateToast('✅ 数据已刷新');
        }
    } catch (e) {
        await this.loadFeishuData();
        this.showUpdateToast('📊 已加载本地数据');
    }
    this.refreshing = false;
}
```

---

## 核心程序

### 1. 同步脚本

**路径**: `scripts/sync_openclaw_to_json.py`

**关键函数**:

```python
def fetch_feishu_records():
    """从飞书读取所有交易记录（分页）"""
    token = get_feishu_token()
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"
    
    all_records = []
    page_token = None
    
    while True:
        params = {'page_size': 500}
        if page_token:
            params['page_token'] = page_token
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        data = response.json()
        
        records = data.get('data', {}).get('items', [])
        all_records.extend(records)
        
        if not data.get('data', {}).get('has_more'):
            break
        page_token = data.get('data', {}).get('page_token')
    
    return all_records

def process_records(records):
    """处理飞书记录，按市场分组"""
    markets = {
        'A 股': {'trades': [], 'holdings': {}, 'initialCapital': 0, 'realizedProfit': 0},
        '港股': {...},
        '美股': {...},
        '加股': {...},
        '数字货币': {...}
    }
    
    for record in records:
        fields = record.get('fields', {})
        
        # 去除所有空格
        market = fields.get('市场', '').replace(' ', '')
        trade_type = fields.get('操作类型', '').replace(' ', '')
        
        # 计算持仓和盈亏
        if trade_type == '充值':
            markets[market]['initialCapital'] += amount
        elif trade_type == '买入' and code:
            # 更新持仓
        elif trade_type == '卖出' and code:
            # 计算已实现盈亏
    
    return markets
```

**环境变量**:
```bash
FEISHU_APP_ID=cli_a923ab8033781cc6
FEISHU_APP_SECRET=6znpJICLLDKf30qQE0usGmdgS4kFkt7S
```

---

### 2. 前端核心逻辑

**收益率计算** (已修正):
```javascript
// 所有市场统一使用此公式
returnRate() { 
    return ((this.realizedProfit / this.initialCapital) * 100).toFixed(2); 
}
```

**持仓计算**:
```javascript
processActions(actions) {
    let initialCapital = 0;
    let cashBalance = 0;
    const holdings = {};
    
    actions.forEach(action => {
        const type = action['交易类型'];
        const code = action['代码'];
        const price = parseFloat(action['成交价'] || 0);
        const quantity = parseFloat(action['数量'] || 0);
        const amount = parseFloat(action['成交金额'] || 0);
        
        if (type === '充值') {
            initialCapital += amount;
            cashBalance += amount;
        } else if (type === '买入') {
            cashBalance -= amount;
            if (!holdings[code]) {
                holdings[code] = {name, quantity: 0, totalCost: 0};
            }
            holdings[code].quantity += quantity;
            holdings[code].totalCost += amount;
            holdings[code].avgCost = holdings[code].totalCost / holdings[code].quantity;
        } else if (type === '卖出') {
            cashBalance += amount;
            if (holdings[code]) {
                const cost = holdings[code].avgCost * quantity;
                const profit = amount - cost;
                realizedProfit += profit;
                holdings[code].quantity -= quantity;
            }
        }
    });
}
```

---

## 定时任务

### Crontab 配置

**查看**: `crontab -l`

**完整配置**:
```bash
# 股票数据同步
*/5 * * * * cd /home/admin/.openclaw/workspace && FEISHU_APP_ID=cli_a923ab8033781cc6 FEISHU_APP_SECRET=6znpJICLLDKf30qQE0usGmdgS4kFkt7S python3 stock-dashboard/scripts/sync_openclaw_to_json.py >> /home/admin/.openclaw/workspace/stock-dashboard/data/sync.log 2>&1

# Git 自动提交
*/5 * * * * cd /home/admin/.openclaw/workspace/stock-dashboard && git add data/ && if ! git diff-index --quiet HEAD -- data/; then git commit -m "auto: sync data $(date +\%Y-\%m-\%d \%H:\%M)" && git push >> /home/admin/.openclaw/workspace/git_auto_commit.log 2>&1; fi

# 大盘指数获取
*/5 * * * * python3 /home/admin/.openclaw/workspace/stock-dashboard/scripts/fetch_indices.py >> /home/admin/.openclaw/workspace/stock-dashboard/data/fetch_indices.log 2>&1

# 加股/数字货币价格获取
*/5 * * * * python3 /home/admin/.openclaw/workspace/stock-dashboard/scripts/fetch_ca_crypto.py >> /home/admin/.openclaw/workspace/stock-dashboard/data/fetch_ca_crypto.log 2>&1

# 雪茄库存获取（其他项目）
*/10 * * * * python3 /home/admin/.openclaw/workspace/stock-dashboard/scripts/fetch_cigar_inventory.py >> /home/admin/.openclaw/workspace/stock-dashboard/data/fetch_cigar_inventory.log 2>&1
```

---

## 配置信息

### 飞书配置

**表格信息**:
- **名称**: 雪茄储存记录 2026 年
- **URL**: https://ocnp5whz0ad6.feishu.cn/wiki/GMj6w7aTFivN3hkSBgHc5W7Anoe
- **App Token**: `LxtibLI9eajhA3sLXYVcYSfynRf`
- **Table ID**: `tbl2AoMbImpRz0vG`

**字段说明**:
| 字段名 | 类型 | 说明 |
|--------|------|------|
| 市场 | 单选 | A 股、港股、美股、加股、数字货币 |
| 操作类型 | 单选 | 充值、提现、买入、卖出 |
| 代码 | 文本 | 股票代码 |
| 名称 | 文本 | 股票名称 |
| 价格 | 数字 | 成交价格 |
| 数量 | 数字 | 成交数量 |
| 成交金额 | 数字 | 成交总金额 |
| 交易日期 | 日期 | 交易日期 |
| 状态 | 单选 | 已建仓、已止损、已止盈等 |
| 操作原因 | 文本 | 交易理由 |
| logo | 附件 | 雪茄 logo 图片 |

### API 配置

**飞书 API**:
```python
FEISHU_APP_ID = 'cli_a923ab8033781cc6'
FEISHU_APP_SECRET = '6znpJICLLDKf30qQE0usGmdgS4kFkt7S'

# 获取 token
url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal"
data = {'app_id': FEISHU_APP_ID, 'app_secret': FEISHU_APP_SECRET}
```

**GitHub**:
- **仓库**: https://github.com/buttons001-blip/opendragon-dashboard
- **分支**: main
- **部署**: Cloudflare Pages 自动部署

**Cloudflare**:
- **域名**: https://www.opendragon.icu
- **部署**: 自动（GitHub push 触发）
- **缓存**: JSON 文件 max-age=0, must-revalidate

---

## 前端功能

### 已实现功能

| 功能 | 状态 | 说明 |
|------|------|------|
| 数据展示 | ✅ | 5 个市场独立页面 |
| 持仓明细 | ✅ | 实时显示持仓股票 |
| 交易记录 | ✅ | 所有交易记录表格 |
| 自动轮询 | ✅ | 30 秒检查更新 |
| 手动刷新 | ✅ | 点击按钮立即刷新 |
| 更新时间 | ✅ | 显示最后更新时间 |
| Toast 提示 | ✅ | 更新时显示提示 |
| 收益率计算 | ✅ | 已实现盈亏/本金 |
| 响应式设计 | ✅ | 适配手机/平板 |

### 页面文件

| 市场 | 文件 | 数据文件 |
|------|------|----------|
| A 股 | `index.html` | `data/trades_cn.json` |
| 港股 | `hk.html` | `data/trades_hk.json` |
| 美股 | `us.html` | `data/trades_us.json` |
| 加股 | `ca.html` | `data/trades_ca.json` |
| 数字货币 | `crypto.html` | `data/trades_crypto.json` |

---

## 交易规则

### 止损止盈规则

| 规则 | 数值 | 说明 |
|------|------|------|
| 止损触发 | -5% | 亏损达到 5% 自动止损 |
| 止盈触发 | +20% | 盈利达到 20% 自动止盈 |
| 加仓条件 | +5% | 盈利达到 5% 可考虑加仓 |

### 收益率计算

**公式**: `收益率 = 已实现盈亏 / 本金 × 100%`

**说明**:
- ✅ 只计算已平仓的盈亏
- ✅ 不包含浮动盈亏
- ✅ 分母为初始本金（不是已投入）

**示例**:
```
本金：¥1,000,000
已实现盈亏：-¥18,966（止损损失）
收益率 = -18,966 / 1,000,000 × 100% = -1.90%
```

### 利弗摩尔十大原则

1. 市场永远正确，顺应最小阻力方向
2. 耐心等待关键点
3. 截断亏损，让利润奔跑
4. 金字塔加仓原则
5. 锁定利润，提取现金
6. 追随领头羊，远离弱势股
7. 绝不向下摊平成本
8. 内幕消息是毒药
9. 投机是一项严肃的事业
10. 最大的敌人是自己

---

## 故障排查

### 常见问题

#### 1. 数据不同步

**症状**: 飞书更新后网页未更新

**排查步骤**:
```bash
# 1. 检查同步脚本日志
tail -20 /home/admin/.openclaw/workspace/stock-dashboard/data/sync.log

# 2. 检查 Git 提交日志
tail -20 /home/admin/.openclaw/workspace/git_auto_commit.log

# 3. 检查 cron 任务
crontab -l | grep stock-dashboard

# 4. 手动执行同步
cd /home/admin/.openclaw/workspace && \
FEISHU_APP_ID=cli_a923ab8033781cc6 \
FEISHU_APP_SECRET=6znpJICLLDKf30qQE0usGmdgS4kFkt7S \
python3 stock-dashboard/scripts/sync_openclaw_to_json.py
```

**常见原因**:
- 飞书 token 过期 → 检查 APP_ID/SECRET
- Git 推送失败 → 检查 GitHub token
- Cron 未执行 → 检查 crontab 配置

---

#### 2. 网页显示旧数据

**症状**: 本地 JSON 已更新，网页仍显示旧数据

**排查步骤**:
```bash
# 1. 检查 JSON 文件时间戳
ls -lh /home/admin/.openclaw/workspace/stock-dashboard/data/trades_cn.json

# 2. 检查 Git 提交
cd /home/admin/.openclaw/workspace/stock-dashboard && git log --oneline -5

# 3. 检查 GitHub 部署
curl -s https://www.opendragon.icu/data/trades_cn.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'时间戳：{d[\"timestamp\"]}')"

# 4. 强制刷新浏览器
# Ctrl+Shift+R (Windows) 或 Cmd+Shift+R (Mac)
```

**常见原因**:
- CDN 缓存 → 等待 1-3 分钟或配置缓存策略
- 浏览器缓存 → 强制刷新
- GitHub 部署延迟 → 检查 GitHub Actions

---

#### 3. 收益率计算错误

**症状**: 收益率包含浮动盈亏

**检查**:
```bash
# 检查前端代码
grep -n "returnRate" /home/admin/.openclaw/workspace/stock-dashboard/index.html

# 应该显示：
# returnRate() { 
#     return ((this.realizedProfit / this.initialCapital) * 100).toFixed(2); 
# }
```

**修复**:
```javascript
// 错误
return ((this.totalProfit / this.initialCapital) * 100).toFixed(2);

// 正确
return ((this.realizedProfit / this.initialCapital) * 100).toFixed(2);
```

---

#### 4. 字段值包含空格

**症状**: A 股记录显示不全

**检查**:
```bash
# 检查同步脚本
grep "market = fields.get" /home/admin/.openclaw/workspace/stock-dashboard/scripts/sync_openclaw_to_json.py

# 应该显示：
# market = fields.get('市场', '').replace(' ', '')
```

**修复**:
```python
# 错误
market = fields.get('市场', '').strip()

# 正确
market = fields.get('市场', '').replace(' ', '')
```

---

## 恢复指南

### 完全恢复步骤

**假设场景**: 系统崩溃，需要从头恢复

#### 1. 恢复代码和数据

```bash
# 1. 克隆 GitHub 仓库
cd /home/admin/.openclaw/workspace
git clone https://github.com/buttons001-blip/opendragon-dashboard.git

# 2. 进入目录
cd stock-dashboard

# 3. 安装依赖
pip3 install -r requirements.txt
```

#### 2. 配置环境变量

```bash
# 编辑 ~/.bashrc 或 ~/.profile
export FEISHU_APP_ID=cli_a923ab8033781cc6
export FEISHU_APP_SECRET=6znpJICLLDKf30qQE0usGmdgS4kFkt7S

# 生效
source ~/.bashrc
```

#### 3. 配置定时任务

```bash
# 编辑 crontab
crontab -e

# 添加配置（见"定时任务"章节）
```

#### 4. 初始化数据

```bash
# 手动执行一次同步
cd /home/admin/.openclaw/workspace && \
FEISHU_APP_ID=cli_a923ab8033781cc6 \
FEISHU_APP_SECRET=6znpJICLLDKf30qQE0usGmdgS4kFkt7S \
python3 stock-dashboard/scripts/sync_openclaw_to_json.py

# 提交初始数据
cd stock-dashboard
git add data/
git commit -m "init: 初始数据"
git push
```

#### 5. 配置 Cloudflare Pages

1. 登录 Cloudflare
2. 创建 Pages 项目
3. 连接 GitHub 仓库 `opendragon-dashboard`
4. 构建配置：
   - 构建命令：留空（静态站点）
   - 输出目录：留空（根目录）
5. 部署！

#### 6. 验证

```bash
# 1. 检查本地 JSON
ls -lh data/trades_*.json

# 2. 检查网页
curl -s https://www.opendragon.icu/ | grep -o "OpenDragon"

# 3. 检查数据
curl -s https://www.opendragon.icu/data/trades_cn.json | python3 -m json.tool | head -20
```

---

### 备份文件位置

| 文件 | 位置 | 说明 |
|------|------|------|
| 同步脚本 | `scripts/sync_openclaw_to_json.py` | 核心同步程序 |
| 前端页面 | `*.html` | 5 个市场页面 |
| 数据文件 | `data/trades_*.json` | 5 个市场数据 |
| 配置文件 | `_headers` | CDN 缓存配置 |
| 文档 | `*.md` | 规则、流程文档 |
| 日志 | `data/sync.log` | 同步日志 |
| 日志 | `../git_auto_commit.log` | Git 提交日志 |

---

### 紧急回滚

**场景**: 新版本有问题，需要回滚

```bash
# 1. 查看提交历史
cd /home/admin/.openclaw/workspace/stock-dashboard
git log --oneline -10

# 2. 回滚到指定版本
git reset --hard <commit_hash>

# 3. 强制推送（谨慎！）
git push --force

# 4. 等待 Cloudflare 重新部署
```

---

## 附录

### A. 关键文件清单

```
stock-dashboard/
├── index.html                    # A 股页面
├── hk.html                       # 港股页面
├── us.html                       # 美股页面
├── ca.html                       # 加股页面
├── crypto.html                   # 数字货币页面
├── scripts/
│   ├── sync_openclaw_to_json.py  # 核心同步脚本
│   ├── fetch_indices.py          # 获取大盘指数
│   └── fetch_ca_crypto.py        # 获取加股/数字货币价格
├── data/
│   ├── trades_cn.json            # A 股数据
│   ├── trades_hk.json            # 港股数据
│   ├── trades_us.json            # 美股数据
│   ├── trades_ca.json            # 加股数据
│   └── trades_crypto.json        # 数字货币数据
├── _headers                      # CDN 缓存配置
└── README.md                     # 项目说明
```

### B. 关键 URL

- **飞书表格**: https://ocnp5whz0ad6.feishu.cn/wiki/GMj6w7aTFivN3hkSBgHc5W7Anoe
- **GitHub 仓库**: https://github.com/buttons001-blip/opendragon-dashboard
- **前端网页**: https://www.opendragon.icu
- **Cloudflare 控制台**: https://dash.cloudflare.com/

### C. 联系信息

- **维护者**: 亨利大管家 👑
- **备份时间**: 2026-03-28
- **文档版本**: v1.0

---

*此文档包含系统完整配置和恢复指南，请妥善保存！*
