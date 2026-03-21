#!/usr/bin/env python3
"""
雪茄库存数据导出脚本
从飞书多维表格读取数据并导出为JSON供前端使用
"""

import json
import requests
import os

# Feishu API Config
APP_TOKEN = "EvEyb9B0VaHcV9sl5WbcrLZYn7d"
TABLE_ID = "tbl1oOymZ0nv8rp2"
FEISHU_API_BASE = "https://open.feishu.cn/open-apis/bitable/v1"

def get_feishu_token():
    """Get Feishu access token"""
    # Try to get from environment or config
    token = os.environ.get('FEISHU_TOKEN')
    if token:
        return token
    
    # Try to read from stock-dashboard config
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
    
    return records

def process_records(records):
    """Process records to extract brand and model data"""
    inventory = []
    
    for record in records:
        fields = record.get("fields", {})
        
        # Extract brand (SingleSelect)
        brand = fields.get("品牌", "")
        if isinstance(brand, dict):
            brand = brand.get("text", "")
        
        # Extract model (Text)
        model = fields.get("型号", "")
        
        # Extract other fields
        quantity = fields.get("数量", "")
        ring_gauge = fields.get("环径", "")
        length = fields.get("长度", "")
        location = fields.get("地点", "")
        arrived = fields.get("到货", "")
        
        if brand and model:
            inventory.append({
                "brand": brand,
                "model": model,
                "quantity": quantity,
                "ringGauge": ring_gauge,
                "length": length,
                "location": location,
                "arrived": arrived
            })
    
    return inventory

def export_to_json(inventory, output_path):
    """Export inventory data to JSON file"""
    data = {
        "brands": sorted(list(set(item["brand"] for item in inventory))),
        "inventory": inventory,
        "totalRecords": len(inventory),
        "lastUpdated": "2026-03-21"
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Exported {len(inventory)} records to {output_path}")
    print(f"Unique brands: {len(data['brands'])}")

def main():
    token = get_feishu_token()
    if not token:
        print("Error: No Feishu token found")
        print("Please set FEISHU_TOKEN environment variable or create feishu_token.txt")
        return
    
    print("Fetching records from Feishu...")
    records = fetch_all_records(APP_TOKEN, TABLE_ID, token)
    print(f"Fetched {len(records)} raw records")
    
    print("Processing records...")
    inventory = process_records(records)
    
    output_path = "/home/admin/.openclaw/workspace/stock-dashboard/data/cigar_inventory.json"
    export_to_json(inventory, output_path)

if __name__ == "__main__":
    main()
