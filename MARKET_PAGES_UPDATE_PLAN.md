# 各市场页面更新计划

## ✅ 已完成

### A 股 (index.html)
- ✅ 从飞书读取交易记录
- ✅ 显示原因列
- ✅ 优化手机端样式

### 加股 (ca.html)
- ✅ 已修正买入价：RY:220.8, ENB:74.03, SHOP:170.07
- ✅ 实时数据源：Yahoo Finance (RY.TO, ENB.TO, SHOP.TO)
- ⏳ 待添加：从飞书读取交易记录（同 A 股）

## ⏳ 待完成

### 港股 (hk.html)
- ⏳ 添加从飞书读取交易记录
- ⏳ 添加交易记录表格
- ⏳ 实时数据源：Yahoo Finance

### 美股 (us.html)
- ⏳ 添加从飞书读取交易记录
- ⏳ 实时数据源：Yahoo Finance

### 数字货币 (crypto.html)
- ⏳ 添加从飞书读取交易记录
- ⏳ 添加交易记录表格
- ⏳ 实时数据源：Yahoo Finance

## 统一规则（同 A 股）

1. **数据源**: 飞书多维表格 `openclaw` (R9u7b3UTeagvfrsQEiGcgG7snBc)
2. **读取方式**: 从 JSON 文件读取（`data/trades_{market}.json`）
3. **字段映射**:
   - 交易类型 → type
   - 代码 → code
   - 名称 → name
   - 成交价 → price
   - 数量 → quantity
   - 成交金额 → amount
   - 交易日期 → date (格式：YYYY-MM-DD)
   - 备注 → reason (原因)
4. **表格样式**: 与 A 股一致（手机端优化）

## 下一步

1. 为 hk.html, us.html, crypto.html 添加交易记录表格
2. 修改 loadFeishuData 方法从 JSON 读取
3. 测试并推送

---

**更新时间**: 2026-03-21 07:45
