# OpenDragon 看板部署指南

## 项目架构

```
本地修改 → GitHub 提交 → Cloudflare Pages 自动部署 → 网站更新
```

## 仓库位置

- **本地路径**: `/home/admin/.openclaw/workspace/stock-dashboard/`
- **GitHub 仓库**: `https://github.com/buttons001-blip/opendragon-dashboard`
- **网站地址**: `https://www.opendragon.icu/`

## 修改网页流程

### 1. 进入项目目录

```bash
cd /home/admin/.openclaw/workspace/stock-dashboard
```

### 2. 修改文件

编辑需要的 HTML/JS/CSS 文件：
- `index.html` - A股看板
- `hk.html` - 港股看板
- `us.html` - 美股看板
- `ca.html` - 加股看板
- `crypto.html` - 数字货币看板

### 3. 查看修改状态

```bash
git status
```

### 4. 添加修改到暂存区

```bash
git add .
```

或指定文件：
```bash
git add crypto.html
```

### 5. 提交修改

```bash
git commit -m "描述修改内容"
```

示例：
```bash
git commit -m "修复数字货币页面货币符号：¥ → $"
```

### 6. 拉取远程更新（防止冲突）

```bash
git pull origin main --rebase
```

如果有冲突，解决后：
```bash
git add .
git rebase --continue
```

### 7. 推送到 GitHub

```bash
git push origin main
```

### 8. 等待自动部署

- Cloudflare Pages 会自动检测到 GitHub 更新
- 部署通常需要 1-2 分钟
- 访问 `https://www.opendragon.icu/` 查看更新

## 常见问题

### 问题1：修改后网站未更新

**原因**: 修改未提交到 GitHub

**解决**:
```bash
git status                    # 查看未提交的修改
git add .
git commit -m "描述修改"
git push origin main
```

### 问题2：推送时出现冲突

**解决**:
```bash
git pull origin main --rebase
# 解决冲突后
git add .
git rebase --continue
git push origin main
```

### 问题3：货币符号显示错误

**检查**:
- A股: 应该是 `¥`
- 港股: 应该是 `HK$`
- 美股: 应该是 `$`
- 加股: 应该是 `C$`
- 数字货币: 应该是 `$`

## 数据更新说明

### 实时数据（A股/港股/美股）
- 网页直接调用 API 获取
- 无需手动更新

### 定时数据（加股/数字货币）
- 由后台脚本定时抓取
- 存入 `data/` 目录下的 JSON 文件
- 网页从 JSON 文件读取

### 交易记录
- 从飞书多维表格读取
- 存储在 `data/trades_*.json` 文件中

## 备份提醒

重要修改前建议备份：
```bash
cd /home/admin/.openclaw/workspace
tar -czf stock-dashboard-backup-$(date +%Y%m%d_%H%M).tar.gz stock-dashboard/
```

## 相关文件

- `MEMORY.md` - 长期记忆和配置
- `AGENTS.md` - 助手配置
- `HEARTBEAT.md` - 定时任务清单
