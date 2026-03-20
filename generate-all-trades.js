#!/usr/bin/env node

/**
 * 补充港股、美股、加股的交易记录
 * 从持仓数据生成买入交易记录
 */

const fs = require('fs');
const path = require('path');

// 港股数据
const hkTrades = {
    "timestamp": new Date().toISOString(),
    "market": "港股",
    "initialCapital": 500000,  // 假设 50 万港币初始资金
    "realizedProfit": 0,
    "holdings": [
        {"code": "01810", "name": "小米集团", "costPrice": 34.88, "quantity": 5000, "reason": "港股第一期建仓，性价比之王，高端手机 + 汽车+AIoT"},
        {"code": "03690", "name": "美团", "costPrice": 78.75, "quantity": 800, "reason": "港股第一期建仓，本地生活龙头，外卖 + 到店 + 优选"}
    ],
    "trades": [
        {"type": "充值", "code": "", "name": "初始资金", "price": 500000, "quantity": 1, "amount": 500000, "date": "2025-03-14", "reason": "港股模拟交易初始资金", "status": ""},
        {"type": "买入", "code": "01810", "name": "小米集团", "price": 34.88, "quantity": 5000, "amount": 174400, "date": "2025-03-14", "reason": "港股第一期建仓，性价比之王，高端手机 + 汽车+AIoT", "status": ""},
        {"type": "买入", "code": "03690", "name": "美团", "price": 78.75, "quantity": 800, "amount": 63000, "date": "2025-03-14", "reason": "港股第一期建仓，本地生活龙头，外卖 + 到店 + 优选", "status": ""},
        {"type": "卖出", "code": "00700", "name": "腾讯控股", "price": 504.9, "quantity": 100, "amount": 50490, "date": "2025-03-19", "reason": "港股第一期建仓，社交 + 游戏龙头，2026-03-19 止损卖出", "status": "已止损"}
    ]
};

// 美股数据
const usTrades = {
    "timestamp": new Date().toISOString(),
    "market": "美股",
    "initialCapital": 20000,  // 假设 2 万美元初始资金
    "realizedProfit": 0,
    "holdings": [
        {"code": "NVDA", "name": "Nvidia", "costPrice": 182.13, "quantity": 40, "reason": "美股第一期建仓，AI 芯片龙头，GPU+ 数据中心"},
        {"code": "MSFT", "name": "Microsoft", "costPrice": 394.76, "quantity": 10, "reason": "美股第一期建仓，软件 + 云+AI 龙头，企业数字化"},
        {"code": "AMZN", "name": "Amazon", "costPrice": 211.68, "quantity": 6, "reason": "美股第一期建仓，电商 + 云+AI 龙头，全球零售"}
    ],
    "trades": [
        {"type": "充值", "code": "", "name": "初始资金", "price": 20000, "quantity": 1, "amount": 20000, "date": "2025-03-16", "reason": "美股模拟交易初始资金", "status": ""},
        {"type": "买入", "code": "NVDA", "name": "Nvidia", "price": 182.13, "quantity": 40, "amount": 7285.2, "date": "2025-03-16", "reason": "美股第一期建仓，AI 芯片龙头，GPU+ 数据中心", "status": ""},
        {"type": "买入", "code": "MSFT", "name": "Microsoft", "price": 394.76, "quantity": 10, "amount": 3947.6, "date": "2025-03-16", "reason": "美股第一期建仓，软件 + 云+AI 龙头，企业数字化", "status": ""},
        {"type": "买入", "code": "AMZN", "name": "Amazon", "price": 211.68, "quantity": 6, "amount": 1270.08, "date": "2025-03-16", "reason": "美股第一期建仓，电商 + 云+AI 龙头，全球零售", "status": ""}
    ]
};

// 加股数据
const caTrades = {
    "timestamp": new Date().toISOString(),
    "market": "加股",
    "initialCapital": 15000,  // 假设 1.5 万加元初始资金
    "realizedProfit": 0,
    "holdings": [
        {"code": "RY", "name": "皇家银行", "costPrice": 142.5, "quantity": 70, "reason": "加股第一期建仓，金融 50%，加拿大最大银行，高分红"},
        {"code": "ENB", "name": "恩桥", "costPrice": 53.2, "quantity": 100, "reason": "加股第一期建仓，能源 25%，北美最大管道，稳定分红"},
        {"code": "SHOP", "name": "Shopify", "costPrice": 94.1, "quantity": 50, "reason": "加股第一期建仓，科技 25%，电商平台，高增长"}
    ],
    "trades": [
        {"type": "充值", "code": "", "name": "初始资金", "price": 15000, "quantity": 1, "amount": 15000, "date": "2025-03-16", "reason": "加股模拟交易初始资金", "status": ""},
        {"type": "买入", "code": "RY", "name": "皇家银行", "price": 142.5, "quantity": 70, "amount": 9975, "date": "2025-03-16", "reason": "加股第一期建仓，金融 50%，加拿大最大银行，高分红", "status": ""},
        {"type": "买入", "code": "ENB", "name": "恩桥", "price": 53.2, "quantity": 100, "amount": 5320, "date": "2025-03-16", "reason": "加股第一期建仓，能源 25%，北美最大管道，稳定分红", "status": ""},
        {"type": "买入", "code": "SHOP", "name": "Shopify", "price": 94.1, "quantity": 50, "amount": 4705, "date": "2025-03-16", "reason": "加股第一期建仓，科技 25%，电商平台，高增长", "status": ""}
    ]
};

// 数字货币（已有数据，但需要补充初始资金）
const cryptoTrades = {
    "timestamp": new Date().toISOString(),
    "market": "数字货币",
    "initialCapital": 20000,  // 2 万美元
    "realizedProfit": 0,
    "holdings": [
        {"code": "BTC", "name": "比特币", "costPrice": 73573.73, "quantity": 0.108734, "reason": "数字货币第一期建仓，数字黄金，价值存储"},
        {"code": "ETH", "name": "以太坊", "costPrice": 2268.89, "quantity": 2.644461, "reason": "数字货币第一期建仓，智能合约平台，DeFi 基础"},
        {"code": "SOL", "name": "Solana", "costPrice": 93.68, "quantity": 32.022857, "reason": "数字货币第一期建仓，高性能公链，快速低费"},
        {"code": "LINK", "name": "Chainlink", "costPrice": 9.67, "quantity": 206.859749, "reason": "数字货币第一期建仓，预言机龙头，链上链下桥梁"}
    ],
    "trades": [
        {"type": "充值", "code": "", "name": "初始资金", "price": 20000, "quantity": 1, "amount": 20000, "date": "2025-03-14", "reason": "数字货币模拟交易初始资金", "status": ""},
        {"type": "买入", "code": "BTC", "name": "比特币", "price": 73573.73, "quantity": 0.108734, "amount": 7999.99, "date": "2025-03-14", "reason": "数字货币第一期建仓，数字黄金，价值存储", "status": ""},
        {"type": "买入", "code": "ETH", "name": "以太坊", "price": 2268.89, "quantity": 2.644461, "amount": 5999.99, "date": "2025-03-14", "reason": "数字货币第一期建仓，智能合约平台，DeFi 基础", "status": ""},
        {"type": "买入", "code": "SOL", "name": "Solana", "price": 93.68, "quantity": 32.022857, "amount": 2999.99, "date": "2025-03-14", "reason": "数字货币第一期建仓，高性能公链，快速低费", "status": ""},
        {"type": "买入", "code": "LINK", "name": "Chainlink", "price": 9.67, "quantity": 206.859749, "amount": 1999.99, "date": "2025-03-14", "reason": "数字货币第一期建仓，预言机龙头，链上链下桥梁", "status": ""}
    ]
};

// 保存文件
const outputDir = path.join(__dirname, 'data');

function saveFile(filename, data) {
    const filepath = path.join(outputDir, filename);
    fs.writeFileSync(filepath, JSON.stringify(data, null, 2), 'utf-8');
    console.log(`✓ 生成：${filepath}`);
}

console.log('生成交易记录文件...\n');

saveFile('trades_hk.json', hkTrades);
saveFile('trades_us.json', usTrades);
saveFile('trades_ca.json', caTrades);
saveFile('trades_crypto.json', cryptoTrades);

console.log('\n✅ 完成！所有市场交易记录已生成。');
