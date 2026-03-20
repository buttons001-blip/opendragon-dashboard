# 加拿大个股实时行情信源

## 信源信息

**数据源**: Yahoo Finance API  
**Endpoint**: `https://query1.finance.yahoo.com/v8/finance/chart/{SYMBOL}.TO`  
**测试日期**: 2026-03-21  
**状态**: ✅ 测试通过

## 股票代码格式

多伦多证券交易所（TSX）股票需要在代码后添加 `.TO` 后缀：

| 股票名称 | 代码 | Yahoo 代码 |
|---------|------|-----------|
| 皇家银行 | RY | RY.TO |
| 恩桥 | ENB | ENB.TO |
| Shopify | SHOP | SHOP.TO |

## 数据字段

```json
{
  "price": 218.50,         // 当前价格
  "change": -1.75,         // 涨跌额
  "changePercent": -0.79   // 涨跌幅 (%)
}
```

## 获取脚本

**位置**: `/home/admin/.openclaw/workspace/stock-dashboard/scripts/fetch_ca_crypto.py`

**功能**:
- 获取加拿大指数（TSX）
- 获取加拿大个股（RY, ENB, SHOP）
- 获取数字货币（BTC, ETH, SOL, LINK）

**输出**: `/home/admin/.openclaw/workspace/stock-dashboard/data/ca_crypto.json`

## 更新频率

- 手动触发或定时任务
- 建议：交易时间内每 30 秒更新一次

## 注意事项

1. Yahoo Finance 部分指数代码可能失效（如 ^SPTSX60, ^JX）
2. 个股数据稳定，推荐使用
3. 需要设置 User-Agent 避免被屏蔽

## 测试记录

**2026-03-21 测试**:
- ✅ RY.TO - $218.50 (-0.79%)
- ✅ ENB.TO - $73.32 (-1.16%)
- ✅ SHOP.TO - $160.64 (-4.53%)

所有个股数据获取成功，可以投入使用。
