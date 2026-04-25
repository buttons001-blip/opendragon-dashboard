#!/bin/bash
# Git 自动推送脚本 - 仅股票项目（每天凌晨 2:30 运行）

cd /home/admin/.openclaw/workspace/stock-dashboard

# 股票相关文件（仅推送股票项目相关文件）
STOCK_FILES="test/stockmarket/ scripts/sync_openclaw_to_json.py scripts/fetch_indices.py scripts/fetch_ca_crypto.py _redirects index.html"

# 检查是否有股票数据变更
STOCK_CHANGES=""
for file in $STOCK_FILES; do
    if git status --porcelain "$file" 2>/dev/null | grep -q "."; then
        STOCK_CHANGES="yes"
        break
    fi
done

# 股票数据推送（每天 2:30）
if [ "$STOCK_CHANGES" = "yes" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 检测到股票数据变更，开始推送..."
    
    # 只添加股票相关文件
    git add -f test/stockmarket/ scripts/sync_openclaw_to_json.py scripts/fetch_indices.py scripts/fetch_ca_crypto.py _redirects index.html 2>/dev/null
    git commit -m "Auto-commit: 股票项目更新 $(date '+%Y-%m-%d %H:%M:%S')"
    git push origin main
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 股票项目推送完成"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 无股票数据变更"
fi
