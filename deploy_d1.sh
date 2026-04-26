#!/bin/bash
# D1 数据库部署脚本

set -e

echo "🚀 开始 D1 数据库部署..."

# 检查是否设置了 Cloudflare API Token
if [ -z "$CLOUDFLARE_API_TOKEN" ]; then
    echo "❌ 错误: 未设置 CLOUDFLARE_API_TOKEN 环境变量"
    echo "请先设置: export CLOUDFLARE_API_TOKEN='your-api-token'"
    exit 1
fi

cd /home/admin/.openclaw/workspace/stock-dashboard

echo "🔧 步骤 1: 创建数据库表结构..."
npx wrangler d1 execute cigars-db --local --file=workers/create_tables.sql

echo "✅ 表结构创建成功！"

echo "🔧 步骤 2: 部署 Workers API..."
npx wrangler deploy

echo "✅ Workers API 部署成功！"

echo "🔧 步骤 3: 导入测试数据..."
# 这里会调用 Workers API 导入测试数据
curl -X POST "https://opendragon.icu/api/v1/inventory/create" \
  -H "Content-Type: application/json" \
  -d '{
    "fields": {
      "brand": "Punch",
      "model": "Coronas A/T", 
      "origin": "古巴",
      "quantity": 25,
      "ringGauge": 42,
      "length": 127,
      "price": 5.36,
      "storageLocation": "测试修改",
      "purchaseLocation": "COH",
      "packaging": "木盒",
      "specification": "25",
      "year": 2019,
      "strength": "中等",
      "flavors": ["雪松木", "花香", "坚果", "皮革", "泥煤", "甘草"],
      "tastingNotes": "前段以雪松木和淡雅花香为主导，味道相当清淡，淡淡的灌木丛气息伴随着更明显的雪松香味。中段逐渐浮现出坚果与烘焙香料的韵味，皮革和雪松的味道中夹杂着泥煤和甘草的味道。后段回归到纯净的木质基调并带有微妙回甜，余味非常圆润均衡",
      "logo": "./logos/punch_古巴.png"
    }
  }'

echo "✅ 测试数据导入成功！"

echo "🎉 D1 部署完成！"
echo "🌐 API 端点: https://opendragon.icu/api/v1/"
echo "📊 可以开始批量导入全部1454条记录了！"