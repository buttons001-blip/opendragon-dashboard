#!/usr/bin/env node

/**
 * 从飞书多维表格生成前端交易数据 JSON
 * 使用前需先通过 feishu_bitable_list_records 获取数据并保存
 */

const fs = require('fs');
const path = require('path');

// 市场选项 ID 映射（包括选项 ID 和中文名称）
const MARKET_MAP = {
    'optB8Myx1q': 'cn',      // A 股
    'optIgh0YNL': 'hk',      // 港股
    'optSPng1ZB': 'us',      // 美股
    'optUMJt6AP': 'ca',      // 加股
    'optw0vmW3q': 'crypto',  // 数字货币
    'A 股': 'cn',
    '港股': 'hk',
    '美股': 'us',
    '加股': 'ca',
    '数字货币': 'crypto'
};

// 市场名称映射
const MARKET_NAMES = {
    'optB8Myx1q': 'A 股',
    'optIgh0YNL': '港股',
    'optSPng1ZB': '美股',
    'optUMJt6AP': '加股',
    'optw0vmW3q': '数字货币',
    'cn': 'A 股',
    'hk': '港股',
    'us': '美股',
    'ca': '加股',
    'crypto': '数字货币'
};

/**
 * 处理飞书记录，生成前端需要的格式
 */
function processRecords(records) {
    const markets = {};
    
    // 初始化市场
    Object.keys(MARKET_MAP).forEach(key => {
        markets[MARKET_MAP[key]] = {
            name: MARKET_NAMES[key],
            trades: [],
            holdings: [],
            initialCapital: 0,
            realizedProfit: 0
        };
    });
    
    // 按市场分类处理记录
    records.forEach(record => {
        const fields = record.fields || {};
        const marketKey = fields['市场'];
        
        if (!marketKey || !MARKET_MAP[marketKey]) {
            return; // 跳过非市场记录（如系统备份）
        }
        
        const marketCode = MARKET_MAP[marketKey];
        const market = markets[marketCode];
        
        const tradeType = fields['交易类型'];
        const code = fields['代码'] || '';
        const name = fields['名称'] || '';
        const price = parseFloat(fields['成交价'] || 0);
        const quantity = parseFloat(fields['数量'] || 0);
        const amount = parseFloat(fields['成交金额'] || 0);
        const tradeDate = fields['交易日期'] ? new Date(fields['交易日期']).toISOString().split('T')[0] : '';
        const reason = fields['备注'] || '';  // "备注"字段就是原因
        const status = fields['状态'] || '';
        
        // 构建交易记录
        const trade = {
            type: tradeType,
            code,
            name,
            price,
            quantity,
            amount,
            date: tradeDate,
            reason,
            status
        };
        
        // 处理不同类型的交易
        if (tradeType === '充值') {
            market.initialCapital += amount;
            market.trades.push(trade);
        } else if (tradeType === '提现') {
            market.trades.push(trade);
        } else if (tradeType === '买入') {
            market.trades.push(trade);
            
            // 更新持仓
            const existing = market.holdings.find(h => h.code === code);
            if (existing) {
                const totalCost = existing.costPrice * existing.quantity + amount;
                const newQty = existing.quantity + quantity;
                existing.costPrice = totalCost / newQty;
                existing.quantity = newQty;
            } else {
                market.holdings.push({
                    code,
                    name,
                    costPrice: price,
                    quantity,
                    reason
                });
            }
        } else if (tradeType === '卖出') {
            market.trades.push(trade);
            
            // 计算已实现盈亏
            const holding = market.holdings.find(h => h.code === code);
            if (holding) {
                const cost = holding.costPrice * quantity;
                const profit = amount - cost;
                market.realizedProfit += profit;
                
                // 更新持仓
                holding.quantity -= quantity;
                if (holding.quantity <= 0) {
                    market.holdings = market.holdings.filter(h => h.code !== code);
                }
            }
        }
    });
    
    return markets;
}

/**
 * 生成前端 JSON 文件
 */
function generateJSONFiles(markets) {
    const outputDir = path.join(__dirname, 'data');
    
    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }
    
    Object.keys(markets).forEach(marketCode => {
        const market = markets[marketCode];
        const outputFile = path.join(outputDir, `trades_${marketCode}.json`);
        
        const data = {
            timestamp: new Date().toISOString(),
            market: market.name,
            initialCapital: market.initialCapital,
            realizedProfit: market.realizedProfit,
            holdings: market.holdings,
            trades: market.trades
        };
        
        fs.writeFileSync(outputFile, JSON.stringify(data, null, 2), 'utf-8');
        console.log(`✓ 生成：${outputFile} (${market.trades.length} 条交易记录，${market.holdings.length} 个持仓)`);
    });
    
    // 同时生成一份完整数据
    const allFile = path.join(outputDir, 'all_trades.json');
    fs.writeFileSync(allFile, JSON.stringify({
        timestamp: new Date().toISOString(),
        markets
    }, null, 2), 'utf-8');
    console.log(`✓ 生成：${allFile}`);
}

// 主程序
function main() {
    console.log('📊 从飞书数据生成前端 JSON...\n');
    
    // 读取飞书数据（从标准输入或文件）
    let inputData;
    
    if (process.argv[2]) {
        // 从文件读取
        const inputFile = process.argv[2];
        console.log(`读取文件：${inputFile}`);
        inputData = JSON.parse(fs.readFileSync(inputFile, 'utf-8'));
    } else {
        // 从标准输入读取
        console.log('从标准输入读取...');
        let data = '';
        fs.readFileSync(0, 'utf-8').forEach(chunk => data += chunk);
        inputData = JSON.parse(data);
    }
    
    // 处理数据
    const records = inputData.records || [];
    console.log(`读取到 ${records.length} 条记录\n`);
    
    const markets = processRecords(records);
    
    // 输出统计
    console.log('市场统计:');
    Object.keys(markets).forEach(code => {
        const m = markets[code];
        console.log(`  ${m.name}: ${m.trades.length} 条交易，${m.holdings.length} 个持仓，初始资金 ¥${m.initialCapital.toLocaleString()}`);
    });
    
    // 生成 JSON 文件
    console.log('\n生成 JSON 文件:');
    generateJSONFiles(markets);
    
    console.log('\n✅ 完成！');
}

main();
