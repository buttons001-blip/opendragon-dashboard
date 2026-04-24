#!/usr/bin/env python3
import os
import re

# 市场页面文件列表
market_files = [
    'test/stockmarket/stock.html',
    'test/stockmarket/hk.html', 
    'test/stockmarket/us.html',
    'test/stockmarket/ca.html',
    'test/stockmarket/crypto.html'
]

# 正确的市场链接映射
market_links = {
    'A股': '/stock',
    '港股': '/hk',
    '美股': '/us', 
    '加股': '/ca',
    '数字货币': '/crypto'
}

for file_path in market_files:
    if not os.path.exists(file_path):
        continue
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修正市场切换标签中的链接
    for market_name, market_path in market_links.items():
        # 替换各种可能的链接格式
        content = re.sub(rf'<a href="[^"]*{market_name.lower()}\.html"', f'<a href="{market_path}"', content)
        content = re.sub(rf'<a href="[^"]*index\.html"', '<a href="/stock"', content)
        content = re.sub(rf'<a href="[^"]*/crypto"', '<a href="/crypto"', content)
    
    # 确保返回首页链接正确
    content = re.sub(r'<a href="[^"]*www\.opendragon\.icu[^"]*"', '<a href="https://www.opendragon.icu/"', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 修正市场链接: {file_path}")

print("✅ 所有市场页面链接修正完成！")