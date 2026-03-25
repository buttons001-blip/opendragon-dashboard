#!/usr/bin/env python3
"""
雪茄库存数据导出脚本 V2
从飞书多维表格"雪茄储存记录2026年"读取数据并导出为JSON供前端使用

支持字段：品牌、型号、数量、环径、长度、存放地点、品牌logo、品吸体验
"""

import json
import requests
import os
from datetime import datetime

# Feishu API Config - 雪茄储存记录2026年
APP_TOKEN = "DGVYbJ0mKaN7rVsXA5mcJjQdnTe"  # 雪茄储存记录2026年表格
TABLE_ID = "tbl35elLH4pejLRr"  # Sheet1
FEISHU_API_BASE = "https://open.feishu.cn/open-apis/bitable/v1"

def get_feishu_token():
    """Get Feishu access token"""
    token = os.environ.get('FEISHU_TOKEN')
    if token:
        return token
    
    try:
        with open('/home/admin/.openclaw/workspace/stock-dashboard/feishu_token.txt', 'r') as f:
            return f.read().strip()
    except:
        pass
    
    return None

def fetch_all_records(app_token, table_id, token):
    """Fetch all records from Feishu Bitable"""
    records = []
    page_token = None
    
    while True:
        url = f"{FEISHU_API_BASE}/apps/{app_token}/tables/{table_id}/records"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        params = {"page_size": 500}
        if page_token:
            params["page_token"] = page_token
            
        try:
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            
            if data.get("code") != 0:
                print(f"Error: {data.get('msg')}")
                break
                
            items = data.get("data", {}).get("items", [])
            records.extend(items)
            
            if not data.get("data", {}).get("has_more"):
                break
            page_token = data.get("data", {}).get("page_token")
        except Exception as e:
            print(f"Error fetching records: {e}")
            break
    
    return records

def extract_field_value(field_value, field_type='text'):
    """Extract value from Feishu field format"""
    if field_value is None:
        return ""
    
    if isinstance(field_value, dict):
        if field_type == 'select':
            return field_value.get("text", "")
        if "text" in field_value:
            return field_value.get("text", "")
        return str(field_value)
    
    if isinstance(field_value, list):
        values = []
        for item in field_value:
            if isinstance(item, dict):
                values.append(item.get("text", ""))
            else:
                values.append(str(item))
        return ", ".join(values) if values else ""
    
    return str(field_value) if field_value else ""

def process_records(records):
    """Process records to extract all required fields"""
    inventory = []
    brand_logos = {}
    
    for record in records:
        fields = record.get("fields", {})
        
        brand = extract_field_value(fields.get("品牌"), 'select')
        model = extract_field_value(fields.get("型号"))
        quantity = extract_field_value(fields.get("数量"))
        ring_gauge = extract_field_value(fields.get("环径"))
        length = extract_field_value(fields.get("长度"))
        location = extract_field_value(fields.get("存放地点"), 'select') or extract_field_value(fields.get("地点"), 'select')
        
        # Extract brand logo (字段名: logo)
        brand_logo = ""
        logo_field = fields.get("logo")
        if logo_field:
            if isinstance(logo_field, list) and len(logo_field) > 0:
                brand_logo = logo_field[0].get("url", "") or logo_field[0].get("tmp_url", "")
            elif isinstance(logo_field, dict):
                brand_logo = logo_field.get("url", "") or logo_field.get("text", "")
            else:
                brand_logo = str(logo_field)
        
        if brand and brand_logo:
            brand_logos[brand] = brand_logo
        
        # Extract tasting experience (字段名: 品吸反馈)
        tasting_experience = ""
        taste_field = fields.get("品吸反馈")
        if taste_field:
            if isinstance(taste_field, dict):
                tasting_experience = taste_field.get("text", "")
            else:
                tasting_experience = str(taste_field)
        
        arrived = extract_field_value(fields.get("到货"))
        price = extract_field_value(fields.get("价格") or fields.get("单价"))
        total_value = extract_field_value(fields.get("总价") or fields.get("总价值"))
        
        if brand and model:
            inventory.append({
                "brand": brand,
                "model": model,
                "quantity": quantity,
                "ringGauge": ring_gauge,
                "length": length,
                "location": location,
                "brandLogo": brand_logo,
                "tastingExperience": tasting_experience,
                "arrived": arrived,
                "price": price,
                "totalValue": total_value
            })
    
    return inventory, brand_logos

def export_to_json(inventory, brand_logos, output_path):
    """Export inventory data to JSON file"""
    brands_with_logos = {}
    for item in inventory:
        brand = item["brand"]
        if brand not in brands_with_logos:
            brands_with_logos[brand] = {
                "name": brand,
                "logo": item.get("brandLogo", "") or brand_logos.get(brand, "")
            }
    
    data = {
        "brands": sorted(list(brands_with_logos.keys())),
        "brandsWithLogos": brands_with_logos,
        "inventory": inventory,
        "totalRecords": len(inventory),
        "lastUpdated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Exported {len(inventory)} records to {output_path}")
    print(f"✅ Unique brands: {len(data['brands'])}")
    print(f"✅ Brands with logos: {sum(1 for b in brands_with_logos.values() if b['logo'])}")
    
    return data

def main():
    token = get_feishu_token()
    if not token:
        print("❌ Error: No Feishu token found")
        return
    
    print("🚀 Fetching records from Feishu...")
    records = fetch_all_records(APP_TOKEN, TABLE_ID, token)
    print(f"✅ Fetched {len(records)} raw records")
    
    if not records:
        print("⚠️ No records found.")
        return
    
    print("🔄 Processing records...")
    inventory, brand_logos = process_records(records)
    
    output_path = "/home/admin/.openclaw/workspace/stock-dashboard/data/cigar_inventory_v2.json"
    export_to_json(inventory, brand_logos, output_path)

if __name__ == "__main__":
    main()
