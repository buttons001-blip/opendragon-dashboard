#!/bin/bash
# 部署字体修复到 Cloudflare Pages

echo "🚀 准备部署字体修复到 OpenDragon 仪表盘..."

# 1. 确认文件已更新
echo "✅ 检查字体CSS文件..."
ls -la css/comprehensive-font-fix.css

echo "✅ 检查index.html..."
grep -n "comprehensive-font-fix.css" index.html

# 2. 提交到 Git
echo "📤 提交更改到 GitHub..."
cd /home/admin/.openclaw/workspace/stock-dashboard

# 配置 Git（如果需要）
git config --global user.email "admin@opendragon.icu"
git config --global user.name "OpenDragon Admin"

# 添加和提交更改
git add css/comprehensive-font-fix.css index.html
git commit -m "fix: 字体显示问题修复 - 添加强力中文字体栈"

# 推送到远程仓库
git push origin main

echo "✅ 已推送到 GitHub！"
echo "🔄 Cloudflare Pages 将在几分钟内自动部署更新。"
echo ""
echo "📱 部署完成后，请强制刷新 https://www.opendragon.icu 页面："
echo "   - Chrome: Ctrl+F5 或 Ctrl+Shift+R"
echo "   - 手机: 清除浏览器缓存或使用无痕模式"
echo ""
echo "💡 如果仍有问题，请告诉我，我们可以进一步调试！"