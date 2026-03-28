#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加 UI 元素：
1. 最后更新时间显示
2. 手动刷新按钮
3. 更新提示 Toast
"""

# 读取文件
with open('/home/admin/.openclaw/workspace/stock-dashboard/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 在 api-status 后添加更新信息
old_ui = """                        <div class="api-status" :class="apiStatusClass" @click="loadFeishuDataRealtime" style="cursor: pointer;" title="点击从飞书实时刷新">
                            数据源：{{ apiStatus }} 🔄
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="card">"""

new_ui = """                        <div class="api-status" :class="apiStatusClass" @click="loadFeishuDataRealtime" style="cursor: pointer;" title="点击从飞书实时刷新">
                            数据源：{{ apiStatus }} 🔄
                        </div>
                        <div class="update-info" style="text-align: center; margin-top: 8px; font-size: 0.75em; color: #888;">
                            <span v-if="lastUpdateTime">最后更新：{{ lastUpdateTime }}</span>
                            <span v-else>加载中...</span>
                            <button @click="refreshData" style="margin-left: 8px; padding: 2px 8px; font-size: 0.9em; background: #1a5c1a; color: white; border: none; border-radius: 4px; cursor: pointer;" :disabled="refreshing">
                                {{ refreshing ? '刷新中...' : '🔄 刷新' }}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 更新提示 Toast -->
            <div v-if="updateToast.show" class="update-toast" style="position: fixed; top: 20px; left: 50%; transform: translateX(-50%); background: #1a5c1a; color: white; padding: 12px 24px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); z-index: 9999; animation: slideDown 0.3s ease;">
                {{ updateToast.message }}
            </div>
            
            <style>
                @keyframes slideDown {
                    from { opacity: 0; transform: translate(-50%, -20px); }
                    to { opacity: 1; transform: translate(-50%, 0); }
                }
            </style>
            
            <div class="card">"""

content = content.replace(old_ui, new_ui)

# 写入文件
with open('/home/admin/.openclaw/workspace/stock-dashboard/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ UI 元素已添加到 index.html")
print("✅ 添加:")
print("   - 最后更新时间显示")
print("   - 手动刷新按钮")
print("   - 更新提示 Toast")
print("   - 动画效果")
