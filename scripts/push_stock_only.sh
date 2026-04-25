#!/bin/bash
# 只推送股票相关文件（15个左右）
cd /home/admin/.openclaw/workspace/stock-dashboard

# 股票相关文件列表
STOCK_FILES=(
    "test/stockmarket/"
    "test/index/index.html"
    "_redirects"
)

# 检查是否有变更
CHANGES=""
for file in "${STOCK_FILES[@]}"; do
    if git status --porcelain "$file" 2>/dev/null | grep -q "."; then
        CHANGES="yes"
        break
    fi
done

if [ "$CHANGES" = "yes" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 检测到股票数据变更，开始推送..."
    
    # 只添加股票相关文件
    git add -f test/stockmarket/ test/index/index.html _redirects 2>/dev/null
    git commit -m "Auto-commit: 股票项目更新 $(date '+%Y-%m-%d %H:%M:%S')"
    git push origin main
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 股票项目推送完成"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 无股票数据变更"
fi