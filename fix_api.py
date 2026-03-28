#!/usr/bin/env python3
import re

DOMAIN = "www.opendragon.icu"

markets = {
    'index.html': ('cn', 'A股'),
    'hk.html': ('hk', '港股'),
    'us.html': ('us', '美股'),
    'ca.html': ('ca', '加股'),
    'crypto.html': ('crypto', '数字货币')
}

for filename, (code, market_cn) in markets.items():
    filepath = f'/home/admin/.openclaw/workspace/stock-dashboard/{filename}'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 简单替换
    old_str = f"'data/trades_{code}.json?t=' + Date.now()"
    new_str = f"'http://{DOMAIN}:8889/api/trades_realtime?market={market_cn}&t=' + Date.now()"
    
    content_new = content.replace(old_str, new_str)
    
    # 处理带cache参数的情况
    old_str2 = f"'data/trades_{code}.json?t=' + Date.now(), {{ cache: 'no-store' }}"
    new_str2 = f"'http://{DOMAIN}:8889/api/trades_realtime?market={market_cn}&t=' + Date.now()"
    content_new = content_new.replace(old_str2, new_str2)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content_new)
    
    # 验证
    if f'{DOMAIN}:8889' in content_new:
        print(f'✓ {filename}: 已更新')
    else:
        print(f'✗ {filename}: 需要检查')
