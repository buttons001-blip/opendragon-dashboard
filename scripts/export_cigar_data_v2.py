#!/usr/bin/env python3
"""
雪茄库存数据导出脚本 V2
从飞书多维表格"雪茄储存记录2026年"读取数据并导出为JSON供前端使用

支持字段：品牌、型号、数量、环径、长度、存放地点、品牌logo、品吸体验
"""

import json
import requests
import os
import re
from datetime import datetime

# Feishu API Config - 雪茄储存记录2026年 (新表格)
APP_TOKEN = "LxtibLI9eajhA3sLXYVcYSfynRf"  # 新多维表格
TABLE_ID = "tbl2AoMbImpRz0vG"  # Sheet1
FEISHU_API_BASE = "https://open.feishu.cn/open-apis/bitable/v1"
FEISHU_DRIVE_BASE = "https://open.feishu.cn/open-apis/drive/v1"

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
    
    # Get new token
    app_id = "cli_a93fa577bff89bc2"
    app_secret = "2Fi2KePv87sLiTmZSPUcdeWa5Ty2MxQF"
    
    url = f"https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal"
    try:
        resp = requests.post(url, json={"app_id": app_id, "app_secret": app_secret})
        data = resp.json()
        token = data.get("app_access_token")
        if token:
            os.makedirs('/home/admin/.openclaw/workspace/stock-dashboard', exist_ok=True)
            with open('/home/admin/.openclaw/workspace/stock-dashboard/feishu_token.txt', 'w') as f:
                f.write(token)
        return token
    except Exception as e:
        print(f"Error getting token: {e}")
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

def get_attachment_url(token, file_token):
    """Get temporary download URL for attachment"""
    if not file_token:
        return ""
    
    # Method 1: Use batch_get_tmp_download_url API
    url = f"{FEISHU_DRIVE_BASE}/medias/batch_get_tmp_download_url?file_tokens={file_token}"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        resp = requests.get(url, headers=headers)
        data = resp.json()
        if data.get("code") == 0:
            urls = data.get("data", {}).get("tmp_download_urls", [])
            if urls and len(urls) > 0:
                return urls[0].get("tmp_download_url", "")
    except Exception as e:
        print(f"Error getting attachment URL (method 1): {e}")
    
    # Method 2: Try direct download API
    try:
        url = f"{FEISHU_DRIVE_BASE}/medias/{file_token}/download"
        resp = requests.get(url, headers=headers, allow_redirects=False)
        if resp.status_code == 302 or resp.status_code == 301:
            return resp.headers.get('Location', '')
    except Exception as e:
        print(f"Error getting attachment URL (method 2): {e}")
    
    return ""

def download_image(url, filepath):
    """Download image from URL"""
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(resp.content)
            return True
    except Exception as e:
        print(f"Error downloading image: {e}")
    return False

def sanitize_filename(filename):
    """Sanitize filename for filesystem"""
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    if len(filename) > 50:
        filename = filename[:50]
    return filename

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

def process_records(records, token):
    """Process records to extract all required fields"""
    inventory = []
    brand_logos = {}
    
    logos_dir = "/home/admin/.openclaw/workspace/stock-dashboard/images/brand_logos"
    os.makedirs(logos_dir, exist_ok=True)
    
    for record in records:
        fields = record.get("fields", {})
        
        brand = extract_field_value(fields.get("品牌"), 'select')
        model = extract_field_value(fields.get("型号"))
        quantity = extract_field_value(fields.get("数量"))
        ring_gauge = extract_field_value(fields.get("环径"))
        length = extract_field_value(fields.get("长度"))
        location = extract_field_value(fields.get("地点"), 'select')
        
        # Extract brand logo
        brand_logo = ""
        logo_field = fields.get("logo")
        if logo_field and brand:
            file_token = None
            if isinstance(logo_field, list) and len(logo_field) > 0:
                file_token = logo_field[0].get("file_token", "")
            elif isinstance(logo_field, dict):
                file_token = logo_field.get("file_token", "")
            
            if file_token:
                safe_brand = sanitize_filename(brand)
                logo_path = f"{logos_dir}/{safe_brand}.png"
                web_path = f"images/brand_logos/{safe_brand}.png"
                
                if os.path.exists(logo_path):
                    brand_logo = web_path
                else:
                    tmp_url = get_attachment_url(token, file_token)
                    if tmp_url and download_image(tmp_url, logo_path):
                        brand_logo = web_path
                        print(f"Downloaded logo for {brand}")
        
        if brand and brand_logo:
            brand_logos[brand] = brand_logo
        
        # Extract tasting feedback
        tasting_feedback = ""
        feedback_field = fields.get("品吸反馈")
        if feedback_field:
            if isinstance(feedback_field, dict):
                tasting_feedback = feedback_field.get("text", "")
            else:
                tasting_feedback = str(feedback_field)
        
        # Extract strength level
        strength_level = ""
        strength_field = fields.get("强度等级")
        if strength_field:
            if isinstance(strength_field, dict):
                strength_level = strength_field.get("text", "")
            else:
                strength_level = str(strength_field)
        
        # Extract main flavor
        main_flavor = ""
        flavor_field = fields.get("主要风味")
        if flavor_field:
            if isinstance(flavor_field, list):
                flavors = []
                for item in flavor_field:
                    if isinstance(item, dict):
                        flavors.append(item.get("text", ""))
                    else:
                        flavors.append(str(item))
                main_flavor = ", ".join(flavors)
            elif isinstance(flavor_field, dict):
                main_flavor = flavor_field.get("text", "")
            else:
                main_flavor = str(flavor_field)
        
        arrived = extract_field_value(fields.get("到货"))
        price = extract_field_value(fields.get("现单价"))
        total_value = extract_field_value(fields.get("预估总价"))
        
        if brand and model:
            inventory.append({
                "brand": brand,
                "model": model,
                "quantity": quantity,
                "ringGauge": ring_gauge,
                "length": length,
                "location": location,
                "brandLogo": brand_logo,
                "tastingFeedback": tasting_feedback,
                "strengthLevel": strength_level,
                "mainFlavor": main_flavor,
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
    
    unique_brands = sorted(list(set(item["brand"] for item in inventory)))
    
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
    print("🚀 Fetching records from Feishu...")
    token = get_feishu_token()
    if not token:
        print("❌ Failed to get Feishu token")
        return
    
    print("✅ Got Feishu token")
    
    records = fetch_all_records(APP_TOKEN, TABLE_ID, token)
    print(f"✅ Fetched {len(records)} raw records")
    
    if not records:
        print("⚠️ No records found.")
        return
    
    print("🔄 Processing records and downloading logos...")
    inventory, brand_logos = process_records(records, token)
    
    output_path = "/home/admin/.openclaw/workspace/stock-dashboard/data/cigar_inventory_v2.json"
    export_to_json(inventory, brand_logos, output_path)
    
    print("\n✅ Done!")

if __name__ == "__main__":
    main()
