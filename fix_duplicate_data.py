#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复重复的 data 属性
"""

# 读取文件
with open('/home/admin/.openclaw/workspace/stock-dashboard/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 删除重复的 data 属性
old_section = """                    apiStatus: '连接中...',
                    lastUpdateTime: null,
                    lastVersion: null,
                    updateToast: { show: false, message: '' },
                    autoRefreshTimer: null,
                    refreshing: false,
                    apiStatusClass: '',
                    lastUpdateTime: null,
                    lastVersion: null,
                    updateToast: { show: false, message: '' },
                    autoRefreshTimer: null,
                    initialCapital: 1000000,"""

new_section = """                    apiStatus: '连接中...',
                    apiStatusClass: '',
                    lastUpdateTime: null,
                    lastVersion: null,
                    updateToast: { show: false, message: '' },
                    autoRefreshTimer: null,
                    refreshing: false,
                    initialCapital: 1000000,"""

content = content.replace(old_section, new_section)

# 写入文件
with open('/home/admin/.openclaw/workspace/stock-dashboard/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 已修复重复的 data 属性")
