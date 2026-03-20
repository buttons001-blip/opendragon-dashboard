#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取加拿大指数和数字货币实时数据
"""

import json
import requests
from datetime import datetime
import os

def fetch_yahoo_data(symbol):
    """从 Yahoo Finance 获取数据"""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        result = data['chart']['result'][0]
        meta = result['meta']
        
        return {
            'value': meta.get('regularMarketPrice', 0),
            'change': meta.get('regularMarketPrice', 0) - meta.get('previousClose', 0),
            'changePercent': ((meta.get('regularMarketPrice', 0) - meta.get('previousClose', 0)) / meta.get('previousClose', 1)) * 100
        }
    except Exception as e:
        print(f"获取 {symbol} 失败：{str(e)}")
        return None

def main():
    print("获取加拿大指数和数字货币数据...")
    
    result = {
        'timestamp': datetime.now().isoformat(),
        'ca': {},
        'crypto': {}
    }
    
    # 加拿大指数
    ca_indices = {
        'TSX': '^GSPTSE',
        'S&P/TSX 60': '^SPTSX60',
        'TSX Venture': '^JX'
    }
    
    for name, symbol in ca_indices.items():
        print(f"获取 {name} ({symbol})...")
        data = fetch_yahoo_data(symbol)
        if data:
            result['ca'][name] = {
                'value': round(data['value'], 2),
                'change': round(data['change'], 2),
                'changePercent': round(data['changePercent'], 2)
            }
            print(f"  ✓ {name}: {data['value']} ({data['changePercent']:+.2f}%)")
    
    # 数字货币
    crypto = {
        'BTC': 'BTC-USD',
        'ETH': 'ETH-USD',
        'SOL': 'SOL-USD',
        'LINK': 'LINK-USD'
    }
    
    for name, symbol in crypto.items():
        print(f"获取 {name} ({symbol})...")
        data = fetch_yahoo_data(symbol)
        if data:
            result['crypto'][name] = {
                'value': round(data['value'], 2),
                'change': round(data['change'], 2),
                'changePercent': round(data['changePercent'], 2)
            }
            print(f"  ✓ {name}: {data['value']} ({data['changePercent']:+.2f}%)")
    
    # 保存 - 保留 stocks 字段
    output_file = '/home/admin/.openclaw/workspace/stock-dashboard/data/ca_crypto.json'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 读取现有文件，保留 stocks 字段
    existing_data = {}
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                if 'stocks' in existing_data:
                    result['stocks'] = existing_data['stocks']
                    print("✓ 保留 stocks 字段")
        except:
            pass
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n数据已保存到：{output_file}")

if __name__ == '__main__':
    main()
