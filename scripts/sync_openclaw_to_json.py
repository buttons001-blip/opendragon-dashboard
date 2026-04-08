#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从飞书多维表格 openclaw 同步交易记录到本地JSON文件
"""

import json
import requests
from datetime import datetime
import os

# 飞书配置 - openclaw 表格
FEISHU_CONFIG = {
    'app_token': 'GA4ibckhcahr6asxah0cOFZmn4b',
    'table_id': 'tbl1tSS4VOOCDywu'
}

def get_feishu_token():
    """获取飞书 API token"""
    app_id = os.getenv('FEISHU_APP_ID', '')
    app_secret = os.getenv('FEISHU_APP_SECRET', '')
    
    if not app_id or not app_secret:
        print("❌ 未配置飞书Token")
        return None
    
    url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal"
    headers = {'Content-Type': 'application/json'}
    data = {'app_id': app_id, 'app_secret': app_secret}
    
    response = requests.post(url, headers=headers, json=data, timeout=30)
    if response.status_code == 200:
        return response.json().get('app_access_token', '')
    return None

def fetch_feishu_records():
    """从飞书读取所有交易记录"""
    token = get_feishu_token()
    if not token:
        return None
    
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_CONFIG['app_token']}/tables/{FEISHU_CONFIG['table_id']}/records"
    headers = {'Authorization': f'Bearer {token}'}
    
    all_records = []
    page_token = None
    
    while True:
        params = {'page_size': 500}
        if page_token:
            params['page_token'] = page_token
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        if response.status_code != 200:
            print(f"❌ 请求失败：{response.status_code}")
            return None
        
        data = response.json()
        if data.get('code') != 0:
            print(f"❌ API错误：{data.get('msg')}")
            return None
        
        records = data.get('data', {}).get('items', [])
        all_records.extend(records)
        
        if not data.get('data', {}).get('has_more'):
            break
        page_token = data.get('data', {}).get('page_token')
    
    return all_records

def process_records(records):
    """处理飞书记录，按市场分组"""
    markets = {
        'A股': {'trades': [], 'holdings': {}, 'initialCapital': 0, 'realizedProfit': 0},
        '港股': {'trades': [], 'holdings': {}, 'initialCapital': 0, 'realizedProfit': 0},
        '美股': {'trades': [], 'holdings': {}, 'initialCapital': 0, 'realizedProfit': 0},
        '加股': {'trades': [], 'holdings': {}, 'initialCapital': 0, 'realizedProfit': 0},
        '数字货币': {'trades': [], 'holdings': {}, 'initialCapital': 0, 'realizedProfit': 0}
    }
    
    for record in records:
        fields = record.get('fields', {})
        
        # 解析字段（去除所有空格）
        market = fields.get('市场', '').replace(' ', '')
        trade_type = fields.get('操作类型', '').replace(' ', '')
        code = fields.get('代码', '').replace(' ', '')
        name = fields.get('名称', '').replace(' ', '')
        price = float(fields.get('价格', 0) or 0)
        quantity = float(fields.get('数量', 0) or 0)
        amount = float(fields.get('成交金额', 0) or 0)
        reason = fields.get('操作原因', '').replace(' ', '')
        status = fields.get('状态', '').replace(' ', '')
        
        # 处理日期 - 飞书时间戳是毫秒（UTC 时间）
        date_val = fields.get('日期', '')
        if isinstance(date_val, int):
            # 使用 UTC 时间解析，避免时区转换导致日期偏移
            date_obj = datetime.utcfromtimestamp(date_val / 1000)
            date = date_obj.strftime('%Y-%m-%d')
            # 将2024年、2025年转换为2026年（测试数据问题）
            if date.startswith('2024') or date.startswith('2025'):
                date = '2026' + date[4:]
        else:
            date = date_val
        
        # 构建交易记录
        trade = {
            'type': trade_type,
            'market': market,
            'code': code,
            'name': name,
            'price': round(price, 2),
            'quantity': quantity,
            'amount': round(amount, 2),
            'date': date,
            'status': status,
            'reason': reason
        }
        
        if market in markets:
            markets[market]['trades'].append(trade)
            
            # 计算持仓和盈亏
            if trade_type == '充值':
                markets[market]['initialCapital'] += amount
            elif trade_type == '买入' and code:
                if code not in markets[market]['holdings']:
                    markets[market]['holdings'][code] = {'name': name, 'qty': 0, 'cost': 0, 'total_cost': 0}
                markets[market]['holdings'][code]['qty'] += quantity
                markets[market]['holdings'][code]['total_cost'] += amount
                if markets[market]['holdings'][code]['qty'] > 0:
                    markets[market]['holdings'][code]['cost'] = markets[market]['holdings'][code]['total_cost'] / markets[market]['holdings'][code]['qty']
            elif trade_type == '卖出' and code:
                if code in markets[market]['holdings'] and markets[market]['holdings'][code]['qty'] > 0:
                    avg_cost = markets[market]['holdings'][code]['cost']
                    profit = (price - avg_cost) * quantity
                    markets[market]['realizedProfit'] += profit
                    markets[market]['holdings'][code]['qty'] -= quantity
                    markets[market]['holdings'][code]['total_cost'] = markets[market]['holdings'][code]['qty'] * avg_cost
    
    return markets

def save_market_data(market_name, data, output_file):
    """保存市场数据到JSON文件"""
    # 构建持仓列表
    holdings_list = []
    for code, h in data['holdings'].items():
        if h['qty'] > 0:
            holdings_list.append({
                'code': code,
                'name': h['name'],
                'costPrice': round(h['cost'], 2),
                'quantity': h['qty']
            })
    
    result = {
        'timestamp': datetime.now().isoformat(),
        'market': market_name,
        'initialCapital': data['initialCapital'],
        'realizedProfit': round(data['realizedProfit'], 2),
        'holdings': holdings_list,
        'trades': data['trades']
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 已保存 {market_name} 数据到 {output_file} ({len(data['trades'])}条交易, {len(holdings_list)}只持仓)")

def main():
    print("📊 从飞书 openclaw 表格同步交易记录...")
    
    records = fetch_feishu_records()
    if not records:
        print("❌ 读取失败")
        return
    
    print(f"✓ 读取到 {len(records)} 条记录")
    
    markets = process_records(records)
    
    # 保存各市场数据
    output_dir = '/home/admin/.openclaw/workspace/stock-dashboard/test/stockmarket/data'
    
    market_files = {
        'A股': 'trades_cn.json',
        '港股': 'trades_hk.json',
        '美股': 'trades_us.json',
        '加股': 'trades_ca.json',
        '数字货币': 'trades_crypto.json'
    }
    
    for market, filename in market_files.items():
        if markets[market]['trades']:
            save_market_data(market, markets[market], f"{output_dir}/{filename}")
        else:
            print(f"⚠ {market} 无数据，跳过")
    
    print("\n✅ 同步完成！")

if __name__ == '__main__':
    main()
