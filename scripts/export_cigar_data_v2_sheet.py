#!/usr/bin/env python3
"""
雪茄库存数据导出脚本 V2 - 飞书表格版本
从飞书表格"雪茄储存记录2026年"读取数据并导出为JSON供前端使用

支持字段：品牌、型号、数量、环径、长度、存放地点、品牌logo、品吸反馈、强度等级、主要风味
"""

import json
import requests
import os
import re
from datetime import datetime

# Feishu Config
SPREADSHEET_TOKEN = "MTR1sFtzIhMZXHt2DbDcGanxnrg"  # 飞书表格token
FEISHU_API_BASE = "https://open.feishu.cn/open-apis"

def get_feishu_token():
    """Get Feishu access token"""
    app_id = "cli_a93fa577bff89bc2"
    app_secret = "2Fi2KePv87sLiTmZSPUcdeWa5Ty2MxQF"
    
    url = f"{FEISHU_API_BASE}/auth/v3/app_access_token/internal"
    try:
        resp = requests.post(url, json={"app_id": app_id, "app_secret": app_secret})
        data = resp.json()
        return data.get("app_access_token")
    except Exception as e:
        print(f"Error getting token: {e}")
        return None

def fetch_sheet_data(token):
    """Fetch data from Feishu Sheet"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # 获取sheet元数据
        meta_url = f"{FEISHU_API_BASE}/sheets/v3/spreadsheets/{SPREADSHEET_TOKEN}/metas"
        resp = requests.get(meta_url, headers=headers)
        meta = resp.json()
        
        if meta.get("code") != 0:
            print(f"Meta error: {meta.get('msg')}")
            return None
        
        # 获取第一个sheet的ID
        sheets = meta.get("data", {}).get("sheets", [])
        if not sheets:
            print("No sheets found")
            return None
        
        sheet_id = sheets[0].get("sheet_id", "0")
        print(f"Using sheet: {sheet_id}")
        
        # 获取sheet内容 - 读取前2000行
        range_str = f"{sheet_id}!A1:Z2000"
        values_url = f"{FEISHU_API_BASE}/sheets/v3/spreadsheets/{SPREADSHEET_TOKEN}/values/{range_str}"
        
        resp = requests.get(values_url, headers=headers)
        data = resp.json()
        
        if data.get("code") != 0:
            print(f"Error fetching sheet: {data.get('msg')}")
            return None
            
        return data.get("data", {}).get("values", [])
    except Exception as e:
        print(f"Error: {e}")
        return None

def parse_sheet_data(values):
    """Parse sheet data to structured format"""
    if not values or len(values) < 2:
        return [], {}
    
    # 第一行是表头
    headers = values[0]
    print(f"Headers found: {headers}")
    
    # 找到关键字段的索引
    header_map = {}
    for i, h in enumerate(headers):
        if h:
            header_map[h.strip()] = i
    
    print(f"Header map: {header_map}")
    
    # 需要的字段
    brand_idx = header_map.get("品牌", -1)
    model_idx = header_map.get("型号", -1)
    quantity_idx = header_map.get("数量", -1)
    ring_idx = header_map.get("环径", -1)
    length_idx = header_map.get("长度", -1)
    location_idx = header_map.get("地点", -1)
    logo_idx = header_map.get("logo", -1)
    feedback_idx = header_map.get("品吸反馈", -1)
    strength_idx = header_map.get("强度等级", -1)
    flavor_idx = header_map.get("主要风味", -1)
    
    inventory = []
    brand_logos = {}
    
    # 从第二行开始解析数据
    for row_idx, row in enumerate(values[1:], start=2):
        if not row or len(row) < 2:
            continue
            
        # 提取字段
        brand = row[brand_idx] if brand_idx >= 0 and brand_idx < len(row) else ""
        model = row[model_idx] if model_idx >= 0 and model_idx < len(row) else ""
        
        if not brand or not model:
            continue
            
        quantity = row[quantity_idx] if quantity_idx >= 0 and quantity_idx < len(row) else ""
        ring_gauge = row[ring_idx] if ring_idx >= 0 and ring_idx < len(row) else ""
        length = row[length_idx] if length_idx >= 0 and length_idx < len(row) else ""
        location = row[location_idx] if location_idx >= 0 and location_idx < len(row) else ""
        brand_logo = row[logo_idx] if logo_idx >= 0 and logo_idx < len(row) else ""
        feedback = row[feedback_idx] if feedback_idx >= 0 and feedback_idx < len(row) else ""
        strength = row[strength_idx] if strength_idx >= 0 and strength_idx < len(row) else ""
        flavor = row[flavor_idx] if flavor_idx >= 0 and flavor_idx < len(row) else ""
        
        # 提取logo URL
        logo_url = ""
        if brand_logo:
            url_match = re.search(r'https?://[^\s<>"\']+', str(brand_logo))
            if url_match:
                logo_url = url_match.group(0)
        
        if brand and logo_url and brand not in brand_logos:
            brand_logos[brand] = logo_url
            
        inventory.append({
            "brand": str(brand).strip(),
            "model": str(model).strip(),
            "quantity": str(quantity),
            "ringGauge": str(ring_gauge),
            "length": str(length),
            "location": str(location),
            "brandLogo": logo_url,
            "tastingFeedback": str(feedback) if feedback else "",
            "strengthLevel": str(strength) if strength else "",
            "mainFlavor": str(flavor) if flavor else "",
            "arrived": "",
            "price": "",
            "totalValue": ""
        })
    
    return inventory, brand_logos

def export_to_json(inventory, brand_logos, output_path):
    """Export to JSON"""
    # 获取唯一品牌列表
    unique_brands = sorted(list(set(item["brand"] for item in inventory)))
    
    # 构建品牌logo映射
    brands_with_logos = {}
    for brand in unique_brands:
        brands_with_logos[brand] = {
            "name": brand,
            "logo": brand_logos.get(brand, "")
        }
    
    data = {
        "brands": unique_brands,
        "brandsWithLogos": brands_with_logos,
        "inventory": inventory,
        "totalRecords": len(inventory),
        "lastUpdated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Exported {len(inventory)} records")
    print(f"✅ Unique brands: {len(unique_brands)}")
    print(f"✅ Brands with logos: {sum(1 for b in brands_with_logos.values() if b['logo'])}")

def main():
    print("🚀 Fetching from Feishu Sheet...")
    token = get_feishu_token()
    if not token:
        print("❌ No token")
        return
    
    values = fetch_sheet_data(token)
    if not values:
        print("❌ No data")
        return
    
    print(f"✅ Fetched {len(values)} rows")
    
    inventory, brand_logos = parse_sheet_data(values)
    
    output_path = "/home/admin/.openclaw/workspace/stock-dashboard/data/cigar_inventory_v2.json"
    export_to_json(inventory, brand_logos, output_path)

if __name__ == "__main__":
    main()
