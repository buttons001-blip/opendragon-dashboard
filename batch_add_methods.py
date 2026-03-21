#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为所有市场页面添加 loadFeishuData 和 processActions 方法
"""

import re

# loadFeishuData 方法
LOAD_FEISHU_METHOD = """                async loadFeishuData() {
                    try {
                        // 从 JSON 文件读取飞书数据
                        const response = await fetch('data/trades_{market}.json?t=' + Date.now());
                        const data = await response.json();
                        
                        // 转换为 processActions 需要的格式
                        const actions = data.trades.map(t => ({
                            '交易类型': t.type,
                            '市场': data.market,
                            '代码': t.code,
                            '名称': t.name,
                            '成交价': t.price,
                            '数量': t.quantity,
                            '成交金额': t.amount,
                            '交易日期': t.date,
                            '状态': t.status,
                            '备注': t.reason
                        }));
                        
                        this.processActions(actions);
                        
                        this.apiStatus = '飞书数据 ✓';
                        this.apiStatusClass = 'success';
                    } catch (e) {
                        console.error('读取飞书数据失败:', e);
                        this.apiStatus = '读取失败';
                        this.apiStatusClass = 'error';
                    }
                },
                
"""

# processActions 方法
PROCESS_ACTIONS_METHOD = """                processActions(actions) {
                    let initialCapital = 0;
                    let cashBalance = 0;
                    const holdings = {};
                    const closed = [];
                    
                    actions.forEach(action => {
                        const type = action['交易类型'];
                        const code = action['代码'];
                        const name = action['名称'];
                        const price = parseFloat(action['成交价'] || 0);
                        const quantity = parseFloat(action['数量'] || 0);
                        const amount = parseFloat(action['成交金额'] || 0);
                        
                        if (type === '充值') {
                            initialCapital += amount;
                            cashBalance += amount;
                        } else if (type === '提现') {
                            cashBalance -= amount;
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
                                closed.push({
                                    code, name,
                                    costPrice: holdings[code].avgCost,
                                    sellPrice: price,
                                    quantity,
                                    profit,
                                    closeDate: '2026-03-20',
                                    reason: action['状态'] === '已止损' ? '止损' : '止盈'
                                });
                                holdings[code].quantity -= quantity;
                                if (holdings[code].quantity <= 0) {
                                    delete holdings[code];
                                }
                            }
                        }
                    });
                    
                    this.initialCapital = initialCapital;
                    this.availableCapital = cashBalance;
                    this.closedPositions = closed;
                    this.realizedProfit = closed.reduce((sum, c) => sum + c.profit, 0);
                    
                    // 构建交易记录
                    this.transactions = actions.map((a, i) => {
                        let dateStr = '2026-03-16';
                        if (a['交易日期']) {
                            const d = new Date(a['交易日期']);
                            const year = d.getFullYear();
                            const month = String(d.getMonth() + 1).padStart(2, '0');
                            const day = String(d.getDate()).padStart(2, '0');
                            dateStr = `${year}-${month}-${day}`;
                        }
                        return {
                            id: i,
                            date: dateStr,
                            type: a['交易类型'],
                            code: a['代码'] || '-',
                            name: a['名称'],
                            price: parseFloat(a['成交价'] || 0).toFixed(2),
                            quantity: parseFloat(a['数量'] || 0),
                            amount: parseFloat(a['成交金额'] || 0),
                            reason: a['备注'] || ''
                        };
                    });
                    
                    this.stocks = Object.keys(holdings).map(code => ({
                        code,
                        name: holdings[code].name,
                        cost: holdings[code].avgCost,
                        price: holdings[code].avgCost,
                        prevClose: holdings[code].avgCost,
                        qty: holdings[code].quantity,
                        profitRate: 0,
                        dayChange: 0,
                        dayChangePercent: '0.00'
                    }));
                },
                
"""

def add_methods(filename, market):
    """添加方法到文件"""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已添加
    if 'loadFeishuData' in content:
        print(f"✓ {filename}: 方法已存在")
        return False
    
    # 替换 market 占位符
    load_method = LOAD_FEISHU_METHOD.replace('{market}', market)
    
    # 找到 methods: { 后插入
    if 'methods: {' in content:
        content = content.replace('methods: {', 'methods: {\n' + load_method + PROCESS_ACTIONS_METHOD)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ {filename}: 方法已添加")
        return True
    else:
        print(f"✗ {filename}: 未找到 methods: {{")
        return False

def add_mounted_call(filename):
    """在 mounted 方法中添加 loadFeishuData 调用"""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已添加
    if 'await this.loadFeishuData()' in content:
        print(f"✓ {filename}: mounted 调用已存在")
        return False
    
    # 在 async mounted() {后添加
    if 'async mounted() {' in content:
        content = content.replace(
            'async mounted() {',
            'async mounted() {\n                // 从飞书读取交易记录\n                await this.loadFeishuData();\n                '
        )
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ {filename}: mounted 调用已添加")
        return True
    else:
        print(f"✗ {filename}: 未找到 async mounted() {{")
        return False

def main():
    pages = [
        ('us.html', 'us'),
        ('ca.html', 'ca'),
        ('crypto.html', 'crypto')
    ]
    
    print("开始批量添加 JavaScript 方法...\n")
    
    for filename, market in pages:
        print(f"处理 {filename} (market={market}):")
        add_methods(filename, market)
        add_mounted_call(filename)
        print()
    
    print("完成！")

if __name__ == '__main__':
    main()
