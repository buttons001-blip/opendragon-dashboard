#!/usr/bin/env python3
import os

# 导航栏HTML模板
nav_template = '''    <!-- OpenDragon Logo 导航栏 -->
    <div style="background: linear-gradient(135deg, #1a3c5c 0%, #0d2b3b 100%); padding: 12px 20px; border-bottom: 1px solid #334155;">
        <a href="https://www.opendragon.icu/" style="color: #e2e8f0; text-decoration: none; display: flex; align-items: center; gap: 12px; font-size: 1.1em; font-weight: bold;">
            <span style="font-size: 1.4em;">🐉</span>
            OpenDragon
        </a>
    </div>'''

html_files = [
    'test/stockmarket/stock.html',
    'test/stockmarket/hk.html', 
    'test/stockmarket/us.html',
    'test/stockmarket/ca.html',
    'test/stockmarket/crypto.html'
]

for html_file in html_files:
    if not os.path.exists(html_file):
        continue
        
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 在body标签后插入导航栏
    if '<body>' in content and '<!-- OpenDragon Logo 导航栏 -->' not in content:
        content = content.replace('<body>', '<body>\n' + nav_template)
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"✅ 添加Logo导航栏: {html_file}")
    else:
        print(f"⚠️  已存在或无法处理: {html_file}")

print("✅ 所有页面Logo导航栏添加完成！")