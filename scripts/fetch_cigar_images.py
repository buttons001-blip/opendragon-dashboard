#!/usr/bin/env python3
"""
批量抓取雪茄图片并存入库存数据库
"""
import json
import time
import urllib.request
import urllib.error
import ssl

# 忽略SSL验证
ssl._create_default_https_context = ssl._create_unverified_context

def search_cigar_image(brand, model):
    """使用 DuckDuckGo API 搜索雪茄图片"""
    query = f"{brand} {model} cigar"
    url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1&skip_disambig=1"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get('Image'):
                return data['Image']
    except Exception as e:
        print(f"  搜索失败: {e}")
    
    return None

def main():
    # 读取库存数据
    inventory_file = '/home/admin/.openclaw/workspace/stock-dashboard/data/cigar_inventory.json'
    
    with open(inventory_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    inventory = data.get('inventory', [])
    total = len(inventory)
    
    print(f"📦 共 {total} 条雪茄记录，开始抓取图片...")
    
    # 统计
    success_count = 0
    fail_count = 0
    
    for i, item in enumerate(inventory):
        brand = item.get('brand', '')
        model = item.get('model', '')
        
        # 检查是否已有图片
        if item.get('image'):
            print(f"[{i+1}/{total}] 跳过 (已有图片): {brand} {model}")
            continue
        
        print(f"[{i+1}/{total}] 搜索: {brand} {model}")
        
        # 搜索图片
        image_url = search_cigar_image(brand, model)
        
        if image_url:
            item['image'] = image_url
            success_count += 1
            print(f"  ✅ 找到: {image_url[:50]}...")
        else:
            fail_count += 1
            print(f"  ❌ 未找到")
        
        # 避免请求过快
        time.sleep(1.5)
        
        # 每50条保存一次进度
        if (i + 1) % 50 == 0:
            with open(inventory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"\n💾 已保存进度 ({i+1}/{total})\n")
    
    # 最终保存
    with open(inventory_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎉 完成!")
    print(f"  ✅ 成功: {success_count}")
    print(f"  ❌ 失败: {fail_count}")

if __name__ == '__main__':
    main()