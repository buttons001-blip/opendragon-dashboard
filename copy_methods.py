#!/usr/bin/env python3
"""
直接复制 A 股的刷新方法到其他市场
"""

# 读取 A 股的方法定义
with open('/home/admin/.openclaw/workspace/stock-dashboard/index.html', 'r', encoding='utf-8') as f:
    index_content = f.read()

# 提取方法定义
import re
pattern = r'(                // 检查数据更新\(轮询\)\n                async checkForUpdates\(\) \{.*?showUpdateToast\(message\) \{[^}]+\{[^}]+\}[^}]+\},)'
match = re.search(pattern, index_content, re.DOTALL)

if not match:
    print("❌ 无法提取方法定义")
    exit(1)

methods_template = match.group(1)
print(f"✅ 提取到方法定义，长度：{len(methods_template)}")

# 处理其他市场
markets = {
    'hk.html': 'trades_hk',
    'us.html': 'trades_us',
    'ca.html': 'trades_ca',
    'crypto.html': 'trades_crypto'
}

for html_file, json_name in markets.items():
    print(f"🔧 处理 {html_file}...")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 跳过已有方法的文件
    if 'async checkForUpdates()' in content:
        print(f"  ⏭️  已有方法，跳过")
        continue
    
    # 替换 JSON 文件名
    methods = methods_template.replace('trades_cn', json_name)
    
    # 找到插入位置（loadFeishuDataRealtime 方法后）
    insert_pattern = r'(                        await this\.loadFeishuData\(\);\s*}\s*},\n                )'
    match = re.search(insert_pattern, content)
    
    if match:
        insert_pos = match.end()
        content = content[:insert_pos] + methods + '\n                ' + content[insert_pos:]
        print(f"  ✅ 添加方法定义")
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(content)
    else:
        print(f"  ❌ 找不到插入位置")

print("\n🎉 方法定义添加完成！")
