#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取全球主要股市指数实时数据
数据源：Yahoo Finance API
输出：JSON 格式，供前端页面使用
"""

import json
import requests
from datetime import datetime
import os

# 指数配置
INDICES = {
    'cn': {
        '上证指数': {'symbol': '000001.SS', 'name': '上证指数'},
        '深证成指': {'symbol': '399001.SZ', 'name': '深证成指'},
        '科创 50': {'symbol': '000688.SS', 'name': '科创 50'}
    },
    'hk': {
        '恒生指数': {'symbol': '^HSI', 'name': '恒生指数'},
        '国企指数': {'symbol': '^HSCE', 'name': '国企指数'},
        '恒生科技': {'symbol': '^HSTECH', 'name': '恒生科技'}
    },
    'us': {
        '道琼斯': {'symbol': '^DJI', 'name': '道琼斯'},
        '纳斯达克': {'symbol': '^IXIC', 'name': '纳斯达克'},
        '标普 500': {'symbol': '^GSPC', 'name': '标普 500'}
    },
    'ca': {
        'TSX': {'symbol': '^GSPTSE', 'name': 'TSX'},
        'S&P/TSX 60': {'symbol': '^SPTSX60', 'name': 'S&P/TSX 60'},
        'TSX Venture': {'symbol': '^JX', 'name': 'TSX Venture'}
    },
    'crypto': {
        'BTC': {'symbol': 'BTC-USD', 'name': '比特币'},
        'ETH': {'symbol': 'ETH-USD', 'name': '以太坊'},
        'SOL': {'symbol': 'SOL-USD', 'name': 'Solana'}
    }
}

def fetch_yahoo_data(symbol):
    """从 Yahoo Finance 获取数据"""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        result = data['chart']['result'][0]
        meta = result['meta']
        
        return {
            'value': meta.get('regularMarketPrice', 0),
            'prevClose': meta.get('previousClose', 0),
            'change': meta.get('regularMarketPrice', 0) - meta.get('previousClose', 0),
            'changePercent': ((meta.get('regularMarketPrice', 0) - meta.get('previousClose', 0)) / meta.get('previousClose', 1)) * 100
        }
    except Exception as e:
        print(f"获取 {symbol} 失败：{str(e)}")
        return None

def fetch_all_indices():
    """获取所有指数数据"""
    result = {
        'timestamp': datetime.now().isoformat(),
        'cn': {},
        'hk': {},
        'us': {},
        'ca': {},
        'crypto': {}
    }
    
    for market, symbols in INDICES.items():
        for name, config in symbols.items():
            print(f"获取 {config['name']} ({config['symbol']})...")
            data = fetch_yahoo_data(config['symbol'])
            
            if data:
                result[market][name] = {
                    'value': round(data['value'], 2),
                    'change': round(data['change'], 2),
                    'changePercent': round(data['changePercent'], 2)
                }
                print(f"  ✓ {name}: {data['value']} ({data['changePercent']:+.2f}%)")
            else:
                print(f"  ✗ {name}: 获取失败")
                result[market][name] = {
                    'value': 0,
                    'change': 0,
                    'changePercent': 0
                }
    
    return result

def save_to_json(data, filepath):
    """保存数据到 JSON 文件"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n数据已保存到：{filepath}")

def main():
    print("=" * 60)
    print("获取全球股市指数实时数据")
    print("=" * 60)
    
    # 获取数据
    data = fetch_all_indices()
    
    # 保存文件
    output_file = '/home/admin/.openclaw/workspace/stock-dashboard/data/indices.json'
    save_to_json(data, output_file)
    
    # 打印摘要
    print("\n" + "=" * 60)
    print("数据摘要:")
    for market, indices in data.items():
        if market != 'timestamp':
            print(f"\n{market.upper()}:")
            for name, values in indices.items():
                print(f"  {name}: {values['value']} ({values['changePercent']:+.2f}%)")
    
    print("\n" + "=" * 60)
    print("完成!")

if __name__ == '__main__':
    main()
