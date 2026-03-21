#!/usr/bin/env python3
"""
雪茄库存数据同步脚本
从飞书多维表格读取数据并保存为JSON
"""

import json
import os
import sys

# Add parent directory to path to import feishu modules
sys.path.insert(0, '/home/admin/.openclaw/workspace/stock-dashboard')

# Feishu Config
APP_TOKEN = "EvEyb9B0VaHcV9sl5WbcrLZYn7d"
TABLE_ID = "tbl1oOymZ0nv8rp2"
FEISHU_API_BASE = "https://open.feishu.cn/open-apis"

def get_feishu_token():
    """Get Feishu access token using app_id and app_secret"""
    import urllib.request
    import urllib.error
    
    app_id = "cli_a93fa577bff89bc2"
    app_secret = "2Fi2KePv87sLiTmZSPUcdeWa5Ty2MxQF"
    
    url = f"{FEISHU_API_BASE}/auth/v3/app_access_token/internal"
    data = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode('utf-8')
    
    headers = {"Content-Type": "application/json"}
    
    try:
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get("app_access_token")
    except Exception as e:
        print(f"Error getting token: {e}")
        return None

def fetch_all_records(token):
    """Fetch all records from Feishu Bitable"""
    import urllib.request
    import urllib.error
    
    records = []
    page_token = None
    max_pages = 10
    page_count = 0
    
    while page_count < max_pages:
        url = f"{FEISHU_API_BASE}/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records?page_size=500"
        if page_token:
            url += f"&page_token={page_token}"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=60) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                if data.get("code") != 0:
                    print(f"API Error: {data.get('msg')}")
                    break
                
                items = data.get("data", {}).get("items", [])
                records.extend(items)
                
                has_more = data.get("data", {}).get("has_more", False)
                page_token = data.get("data", {}).get("page_token")
                page_count += 1
                
                print(f"Fetched page {page_count}: {len(items)} records")
                
                if not has_more or not page_token:
                    break
                    
        except Exception as e:
            print(f"Error fetching records: {e}")
            break
    
    return records

def process_records(records):
    """Process records to extract brand and model data"""
    inventory = []
    brands = set()
    
    for record in records:
        fields = record.get("fields", {})
        
        # Extract brand (SingleSelect)
        brand = fields.get("品牌", "")
        if isinstance(brand, dict):
            brand = brand.get("text", "")
        
        # Extract model (Text)
        model = fields.get("型号", "")
        
        if brand and model:
            inventory.append({
                "brand": brand,
                "model": model,
                "quantity": fields.get("数量", ""),
                "ringGauge": fields.get("环径", ""),
                "length": fields.get("长度", ""),
                "location": fields.get("地点", ""),
                "arrived": fields.get("到货", ""),
                "price": fields.get("现单价", ""),
                "totalValue": fields.get("预估总价", "")
            })
            brands.add(brand)
    
    return inventory, sorted(list(brands))

def save_to_json(inventory, brands, output_path):
    """Save data to JSON file"""
    data = {
        "success": True,
        "brands": brands,
        "inventory": inventory,
        "totalRecords": len(inventory),
        "lastUpdated": "2026-03-21"
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\nSaved {len(inventory)} records to {output_path}")
    print(f"Unique brands: {len(brands)}")

def main():
    print("Fetching cigar inventory from Feishu...")
    
    # Get token
    token = get_feishu_token()
    if not token:
        print("Failed to get Feishu token")
        return 1
    print("Got Feishu token successfully")
    
    # Fetch records
    print("\nFetching records...")
    records = fetch_all_records(token)
    print(f"\nTotal records fetched: {len(records)}")
    
    # Process records
    print("\nProcessing records...")
    inventory, brands = process_records(records)
    
    # Save to JSON
    output_path = "/home/admin/.openclaw/workspace/stock-dashboard/data/cigar_inventory.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    save_to_json(inventory, brands, output_path)
    
    print("\nDone!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
