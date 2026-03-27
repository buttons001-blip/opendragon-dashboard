# OpenDragon 股票看板操作规则

## 数据架构

### 1. 数据源（唯一）
- **飞书多维表格**: `openclaw`
  - App Token: `GA4ibckhcahr6asxah0cOFZmn4b`
  - Table ID: `tbl1tSS4VOOCDywu`
  - URL: https://ocnp5whz0ad6.feishu.cn/wiki/HLeHwBHHriTWOokX2HkcHtbEnhe

### 2. 数据流向
```
飞书 openclaw 表格
    ↓ (定时同步)
本地 JSON 文件 (stock-dashboard/data/)
    ↓ (git push)
GitHub 仓库
    ↓ (Cloudflare Pages)
前端网页显示
```

### 3. 同步机制
- **定时任务**: 每5分钟自动同步
- **脚本位置**: `/home/admin/.openclaw/workspace/stock-dashboard/scripts/sync_openclaw_to_json.py`
- **Git提交**: 自动提交到GitHub

## 文件结构

### 前端页面
| 市场 | 文件 | 数据源 |
|------|------|--------|
| A股 | `index.html` | `data/trades_cn.json` |
| 港股 | `hk.html` | `data/trades_hk.json` |
| 美股 | `us.html` | `data/trades_us.json` |
| 加股 | `ca.html` | `data/trades_ca.json` |
| 数字货币 | `crypto.html` | `data/trades_crypto.json` |

### 数据文件
- **位置**: `stock-dashboard/data/trades_*.json`
- **格式**: JSON，包含 trades, holdings, initialCapital, realizedProfit

## 修改规则

### 1. 数据更新
- **不要**直接修改JSON文件
- 所有数据修改必须在**飞书openclaw表格**中进行
- 等待5分钟自动同步，或手动运行同步脚本

### 2. 前端修改
- 从GitHub/Cloudflare部署，不是本地服务器
- 修改后需要 `git push` 到GitHub
- 使用相对路径 `./data/xxx.json` 读取数据

### 3. 页面结构
- **A股页面**: 显示持仓明细 + 交易记录
- **其他市场**: 只显示交易记录，**不显示已清仓记录**
- 已清仓记录在交易记录中体现（状态=已止损）

## 紧急修复步骤

### 如果数据为空
1. 检查飞书表格数据是否正常
2. 手动运行同步: `python3 stock-dashboard/scripts/sync_openclaw_to_json.py`
3. 提交到GitHub: `git add data/ && git commit -m "sync data" && git push`

### 如果页面显示错误
1. 从昨晚备份恢复: `cp /tmp/workspace/stock-dashboard/xxx.html ./`
2. 更新飞书配置: `sed -i 's/旧token/GA4ibckhcahr6asxah0cOFZmn4b/g'`
3. 提交到GitHub

## 备份位置
- **昨晚备份**: `/home/admin/.openclaw/workspace/backups/openclaw_config_20260326_2100.tar.gz`
- **临时备份**: `/tmp/workspace/stock-dashboard/`

## 定时任务
```bash
# 查看定时任务
crontab -l | grep stock

# 手动执行同步
python3 /home/admin/.openclaw/workspace/stock-dashboard/scripts/sync_openclaw_to_json.py
```

## 域名
- **访问地址**: https://www.opendragon.icu
- **GitHub仓库**: https://github.com/buttons001-blip/opendragon-dashboard

---
**最后更新**: 2026-03-27
**规则版本**: v1.0
