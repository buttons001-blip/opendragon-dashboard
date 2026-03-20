#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从飞书多维表格读取交易记录数据
生成 JSON 文件供前端使用
"""

import json
import requests
from datetime import datetime
import os

# 飞书配置
FEISHU_CONFIG = {
    'app_token': 'R9u7b3UTeagvfrsQEiGcgG7snBc',
    'table_id': 'tblYYndqV1vTDg8I'
}

def get_feishu_token():
    """获取飞书 API token"""
    # 需要从环境变量或配置文件中读取
    # 这里假设已经配置好
    return os.getenv('FEISHU_TOKEN', '')

def fetch_feishu_records():
    """从飞书读取所有交易记录"""
    token = get_feishu_token()
    if not token:
        print("❌ 未配置 FEISHU_TOKEN 环境变量")
        return None
    
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_CONFIG['app_token']}/tables/{FEISHU_CONFIG['table_id']}/records"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    all_records = []
    page_token = None
    
    while True:
        params = {'page_size': 500}
        if page_token:
            params['page_token'] = page_token
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ 请求失败：{response.status_code} - {response.text}")
            return None
        
        data = response.json()
        if data.get('code') != 0:
            print(f"❌ API 错误：{data.get('msg')}")
            return None
        
        records = data.get('data', {}).get('items', [])
        all_records.extend(records)
        
        if not data.get('data', {}).get('has_more'):
            break
        
        page_token = data.get('data', {}).get('page_token')
    
    return all_records

def process_records(records):
    """处理飞书记录，按市场分类"""
    markets = {
        'A 股': [],
        '港股': [],
        '美股': [],
        '加股': [],
        '数字货币': []
    }
    
    for record in records:
        fields = record.get('fields', {})
        market = fields.get('市场', '')
        
        # 市场选项 ID 映射
        market_map = {
            'optB8Myx1q': 'A 股',
            'optIgh0YNL': '港股',
            'optSPng1ZB': '美股',
            'optUMJt6AP': '加股',
            'optw0vmW3q': '数字货币'
        }
        
        market_name = market_map.get(market, market)
        
        if market_name in markets:
            # 提取交易记录字段
            trade_record = {
                '交易类型': fields.get('交易类型', ''),
                '市场': market_name,
                '代码': fields.get('代码', ''),
                '名称': fields.get('名称', ''),
                '成交价': fields.get('成交价', 0),
                '数量': fields.get('数量', 0),
                '成交金额': fields.get('成交金额', 0),
                '成交日期': fields.get('交易日期', ''),
                '状态': fields.get('状态', ''),
                '备注': fields.get('备注', '')  # 这就是"原因"
            }
            markets[market_name].append(trade_record)
    
    return markets

def main():
    print("📊 从飞书读取交易记录...")
    
    records = fetch_feishu_records()
    if not records:
        print("❌ 读取失败")
        return
    
    print(f"✓ 读取到 {len(records)} 条记录")
    
    # 处理记录
    markets_data = process_records(records)
    
    # 输出统计
    for market, trades in markets_data.items():
        print(f"  {market}: {len(trades)} 条记录")
    
    # 保存为 JSON 文件
    output_dir = '/home/admin/.openclaw/workspace/stock-dashboard/data'
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存每个市场的数据
    for market, trades in markets_data.items():
        filename = f"trades_{market}.json"
        # 文件名处理
        file_map = {
            'A 股': 'trades_cn.json',
            '港股': 'trades_hk.json',
            '美股': 'trades_us.json',
            '加股': 'trades_ca.json',
            '数字货币': 'trades_crypto.json'
        }
        
        output_file = os.path.join(output_dir, file_map.get(market, filename))
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'market': market,
                'trades': trades
            }, f, ensure_ascii=False, indent=2)
        
        print(f"  ✓ 保存到：{output_file}")
    
    # 同时保存一份完整数据
    output_file = os.path.join(output_dir, 'all_trades.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'markets': markets_data
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 所有数据已保存到：{output_dir}")

if __name__ == '__main__':
    main()
