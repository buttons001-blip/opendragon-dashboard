#!/usr/bin/env python3
import os
import re

# HTML文件列表
html_files = [
    'test/stockmarket/index.html',
    'test/stockmarket/stock.html', 
    'test/stockmarket/hk.html',
    'test/stockmarket/us.html',
    'test/stockmarket/ca.html',
    'test/stockmarket/crypto.html'
]

# 市场映射
market_mapping = {
    'A股': '/stock',
    '港股': '/hk', 
    '美股': '/us',
    '加股': '/ca',
    '数字货币': '/crypto'
}

for html_file in html_files:
    if not os.path.exists(html_file):
        continue
        
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修正市场切换链接
    for market_name, market_path in market_mapping.items():
        # 替换相对路径为绝对路径
        pattern = f'<a href="[^"]*{market_name.lower() if "股" in market_name else "crypto"}\\.html"'
        replacement = f'<a href="{market_path}"'
        content = re.sub(pattern, replacement, content)
    
    # 修正返回首页链接 - 指向 www.opendragon.icu
    content = re.sub(r'<a href="\.\./\.\./"', '<a href="https://www.opendragon.icu/"', content)
    content = re.sub(r'← 返回首页', '<img src="https://www.opendragon.icu/logo.png" alt="OpenDragon" style="height:20px; margin-right:8px;"> OpenDragon', content)
    
    # 保存修正后的文件
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 修正完成: {html_file}")

print("✅ 所有HTML文件链接修正完成！")