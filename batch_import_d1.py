#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量导入全部1454条雪茄记录到 D1 数据库
"""

import json
import requests
import time

def load_inventory_data():
    """加载库存数据"""
    with open('data/cigar_inventory.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['cigars']

def import_to_d1(record):
    """导入单条记录到 D1"""
    url = "https://opendragon.icu/api/v1/inventory/create"
    
    # 转换字段格式
    fields = {
        'brand': record['brand'],
        'model': record['model'],
        'origin': record['origin'],
        'quantity': record.get('quantity', 0),
        'ringGauge': record.get('ringGauge'),
        'length': record.get('length'),
        'price': record.get('price'),
        'storageLocation': record.get('storageLocation', ''),
        'purchaseLocation': record.get('purchaseLocation', ''),
        'packaging': record.get('packaging', ''),
        'specification': record.get('specification', ''),
        'year': record.get('year'),
        'strength': record.get('strength', ''),
        'flavors': record.get('flavors', []),
        'tastingNotes': record.get('tastingNotes', ''),
        'logo': record.get('logo', '')
    }
    
    payload = {'fields': fields}
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return True
            else:
                print(f"❌ 导入失败: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def main():
    print("📦 开始批量导入到 D1 数据库...")
    
    records = load_inventory_data()
    total = len(records)
    success_count = 0
    
    print(f"总记录数: {total}")
    
    for i, record in enumerate(records, 1):
        print(f"[{i}/{total}] 导入: {record['brand']} {record['model']}")
        
        if import_to_d1(record):
            success_count += 1
            print(f"✅ 成功 ({success_count}/{total})")
        else:
            print(f"❌ 失败")
        
        # 避免速率限制，每条记录间隔0.5秒
        if i % 10 == 0:
            print(f"📊 进度: {i}/{total} ({success_count} 成功)")
            time.sleep(2)  # 每10条暂停2秒
        else:
            time.sleep(0.5)
    
    print(f"\n🎉 批量导入完成！")
    print(f"成功: {success_count}/{total}")
    print(f"成功率: {success_count/total*100:.1f}%")

if __name__ == '__main__':
    main()