#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从飞书多维表格"雪茄储存记录 2026 年"同步雪茄库存到本地 JSON 文件
"""

import json
import requests
from datetime import datetime
import os
import base64

# 飞书配置 - 雪茄储存记录 2026 年
FEISHU_CONFIG = {
    'app_token': 'LxtibLI9eajhA3sLXYVcYSfynRf',
    'table_id': 'tbl2AoMbImpRz0vG'
}

# 输出配置
OUTPUT_FILE = '/home/admin/.openclaw/workspace/stock-dashboard/data/cigar_inventory.json'
LOGO_DIR = '/home/admin/.openclaw/workspace/stock-dashboard/logos'

def get_feishu_token():
    """获取飞书 API token"""
    app_id = os.getenv('FEISHU_APP_ID', 'cli_a923ab8033781cc6')
    app_secret = os.getenv('FEISHU_APP_SECRET', '6znpJICLLDKf30qQE0usGmdgS4kFkt7S')
    
    url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal"
    headers = {'Content-Type': 'application/json'}
    data = {'app_id': app_id, 'app_secret': app_secret}
    
    response = requests.post(url, headers=headers, json=data, timeout=30)
    if response.status_code == 200:
        return response.json().get('app_access_token', '')
    return None

def fetch_feishu_records():
    """从飞书读取所有雪茄记录"""
    token = get_feishu_token()
    if not token:
        print("❌ 获取飞书 Token 失败")
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
            print(f"❌ API 错误：{data.get('msg')}")
            return None
        
        records = data.get('data', {}).get('items', [])
        all_records.extend(records)
        
        if not data.get('data', {}).get('has_more'):
            break
        page_token = data.get('data', {}).get('page_token')
    
    return all_records

def process_records(records):
    """处理飞书记录，转换为雪茄库存格式"""
    cigars = []
    
    for record in records:
        fields = record.get('fields', {})
        record_id = record.get('id', '')
        
        # 解析字段
        cigar = {
            'id': record_id,
            'brand': fields.get('品牌', '').strip(),
            'model': fields.get('型号', '').strip(),
            'quantity': int(fields.get('数量', 0) or 0),
            'ringGauge': int(fields.get('环径', 0) or 0),
            'length': int(fields.get('长度', 0) or 0),
            'storageLocation': fields.get('储存位置', '').strip(),
            'price': float(fields.get('单价', 0) or 0),
            'origin': fields.get('产地', '').strip(),
            'purchaseLocation': fields.get('购买地点', '').strip(),
            'specification': fields.get('规格', '').strip(),
            'year': int(fields.get('年份', 0) or 0),
            'arrived': fields.get('是否到货', '').strip(),
            'strength': fields.get('浓度', '').strip(),
            'flavors': [],
            'tastingNotes': fields.get('品吸笔记', '').strip()
        }
        
        # 处理风味字段（可能是多选）
        flavors = fields.get('风味', [])
        if isinstance(flavors, list):
            cigar['flavors'] = [f.strip() for f in flavors if f]
        elif isinstance(flavors, str):
            cigar['flavors'] = [f.strip() for f in flavors.split(',') if f.strip()]
        
        # 处理图片/Logo（如果有附件字段）
        logo_field = fields.get('Logo', [])
        if isinstance(logo_field, list) and len(logo_field) > 0:
            # 取第一个图片的 URL
            logo_url = logo_field[0].get('url', '') if isinstance(logo_field[0], dict) else ''
            if logo_url:
                cigar['logoUrl'] = logo_url
        
        cigars.append(cigar)
    
    return cigars

def save_cigar_data(cigars, output_file):
    """保存雪茄数据到 JSON 文件"""
    # 确保目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    result = {
        'timestamp': datetime.now().isoformat(),
        'total': len(cigars),
        'source': '飞书多维表格 - 雪茄储存记录 2026 年',
        'cigars': cigars
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 已保存 {len(cigars)} 条雪茄数据到 {output_file}")
    
    # 统计信息
    brands = set(c['brand'] for c in cigars if c['brand'])
    origins = set(c['origin'] for c in cigars if c['origin'])
    total_quantity = sum(c['quantity'] for c in cigars)
    
    print(f"  - 品牌数量：{len(brands)}")
    print(f"  - 产地数量：{len(origins)}")
    print(f"  - 总数量：{total_quantity} 支")

def main():
    print("🚬 从飞书同步雪茄库存数据...")
    print(f"   表格：{FEISHU_CONFIG['app_token']}")
    print(f"   表 ID: {FEISHU_CONFIG['table_id']}")
    
    records = fetch_feishu_records()
    if not records:
        print("❌ 读取失败")
        return
    
    print(f"✓ 读取到 {len(records)} 条记录")
    
    cigars = process_records(records)
    save_cigar_data(cigars, OUTPUT_FILE)
    
    print("\n✅ 同步完成！")

if __name__ == '__main__':
    main()
