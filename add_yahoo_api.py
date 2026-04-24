#!/usr/bin/env python3
import os

# 为加股页面添加Yahoo Finance API调用
ca_content = '''// Yahoo Finance API for Canadian stocks
async fetchCanadianStockData() {
    try {
        const symbols = this.stocks.map(s => s.code + '.TO').join(',');
        const response = await fetch(`https://query1.finance.yahoo.com/v8/finance/chart/${symbols}?interval=1d&range=1d`, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        });
        const data = await response.json();
        // 处理Yahoo数据...
        console.log('Yahoo Finance data loaded for CA stocks');
    } catch (error) {
        console.error('Failed to fetch Yahoo Finance data:', error);
    }
}'''

# 为数字货币页面添加Yahoo Finance API调用  
crypto_content = '''// Yahoo Finance API for Crypto
async fetchCryptoData() {
    try {
        const cryptoSymbols = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'LINK-USD'];
        const promises = cryptoSymbols.map(symbol => 
            fetch(`https://query1.finance.yahoo.com/v8/finance/chart/${symbol}?interval=1d&range=1d`, {
                headers: {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            })
        );
        const responses = await Promise.all(promises);
        const data = await Promise.all(responses.map(r => r.json()));
        // 处理加密货币数据...
        console.log('Yahoo Finance crypto data loaded');
    } catch (error) {
        console.error('Failed to fetch Yahoo Finance crypto data:', error);
    }
}'''

print("Yahoo Finance API functions created")
print("Manual integration required in HTML files")