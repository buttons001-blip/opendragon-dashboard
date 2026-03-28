#!/usr/bin/env python3
"""
为其他市场页面添加完整的刷新功能
使用正则表达式匹配，更可靠
"""

import re

def add_features(html_file, market_name, json_name):
    print(f"🔧 处理 {market_name}...")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 检查是否已有刷新功能
    if 'checkForUpdates' in content:
        print(f"  ⏭️  已有刷新功能，跳过")
        return
    
    # 2. 添加 beforeDestroy
    if 'beforeDestroy' not in content and 'async mounted' in content:
        content = content.replace(
            '}, 30000);\n            },',
            '''}, 30000);
                
                // 每 30 秒自动检查数据更新
                this.autoRefreshTimer = setInterval(() => {
                    this.checkForUpdates();
                }, 30000);
            },
            
            beforeDestroy() {
                if (this.autoRefreshTimer) {
                    clearInterval(this.autoRefreshTimer);
                }
            },'''
        )
        print(f"  ✅ 添加轮询定时器")
    
    # 3. 添加刷新方法（在 loadFeishuDataRealtime 后）
    if 'loadFeishuDataRealtime' in content and 'checkForUpdates' not in content:
        # 找到 loadFeishuDataRealtime 的结束位置
        pattern = r'(await this\.loadFeishuData\(\);\s*}\s*},)'
        match = re.search(pattern, content)
        if match:
            insert_pos = match.end()
            new_methods = f'''
                
                // 检查数据更新（轮询）
                async checkForUpdates() {{
                    try {{
                        const response = await fetch('data/{json_name}.json?t=' + Date.now());
                        const data = await response.json();
                        
                        if (data.timestamp !== this.lastVersion) {{
                            await this.loadFeishuData();
                            this.showUpdateToast('📊 数据已更新');
                        }}
                    }} catch (e) {{
                        console.log('轮询检查失败:', e);
                    }}
                }},
                
                // 手动刷新数据
                async refreshData() {{
                    if (this.refreshing) return;
                    
                    this.refreshing = true;
                    try {{
                        const response = await fetch('api/trades_realtime.php?t=' + Date.now());
                        const data = await response.json();
                        
                        if (data.success) {{
                            this.processTradeData(data);
                            this.apiStatus = '飞书实时数据 ✓ ' + new Date().toLocaleTimeString();
                            this.apiStatusClass = 'success';
                            this.showUpdateToast('✅ 数据已刷新');
                        }} else {{
                            throw new Error(data.error || 'API error');
                        }}
                    }} catch (e) {{
                        console.error('实时刷新失败:', e);
                        await this.loadFeishuData();
                        this.showUpdateToast('📊 已加载本地数据');
                    }}
                    this.refreshing = false;
                }},
                
                // 显示更新提示
                showUpdateToast(message) {{
                    this.updateToast = {{ show: true, message: message }};
                    setTimeout(() => {{
                        this.updateToast.show = false;
                    }}, 3000);
                }},'''
            content = content[:insert_pos] + new_methods + content[insert_pos:]
            print(f"  ✅ 添加刷新方法")
    
    # 4. 在 processTradeData 中添加更新时间记录
    if 'processTradeData(data)' in content and 'lastUpdateTime' not in content:
        content = content.replace(
            'processTradeData(data) {',
            '''processTradeData(data) {
                    // 记录最后更新时间
                    this.lastUpdateTime = new Date().toLocaleTimeString('zh-CN', {hour: '2-digit', minute:'2-digit', second:'2-digit'});
                    this.lastVersion = data.timestamp || new Date().toISOString();'''
        )
        print(f"  ✅ 添加更新时间记录")
    
    # 5. 添加 UI 元素
    if 'api-status' in content and 'update-info' not in content:
        # 找到 api-status 的结束标签
        pattern = r'(<div class="api-status"[^>]*>.*?</div>\s*</div>\s*</div>\s*</div>)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            old_ui = match.group(1)
            new_ui = old_ui + '''
                        <div class="update-info" style="text-align: center; margin-top: 8px; font-size: 0.75em; color: #888;">
                            <span v-if="lastUpdateTime">最后更新：{{ lastUpdateTime }}</span>
                            <span v-else>加载中...</span>
                            <button @click="refreshData" style="margin-left: 8px; padding: 2px 8px; font-size: 0.9em; background: #1a5c1a; color: white; border: none; border-radius: 4px; cursor: pointer;" :disabled="refreshing">
                                {{ refreshing ? '刷新中...' : '🔄 刷新' }}
                            </button>
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
            </style>'''
            content = content.replace(old_ui, new_ui)
            print(f"  ✅ 添加 UI 元素")
    
    # 写入文件
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✅ {market_name} 完成\n")

# 处理所有市场
add_features('/home/admin/.openclaw/workspace/stock-dashboard/hk.html', '港股', 'trades_hk')
add_features('/home/admin/.openclaw/workspace/stock-dashboard/us.html', '美股', 'trades_us')
add_features('/home/admin/.openclaw/workspace/stock-dashboard/ca.html', '加股', 'trades_ca')
add_features('/home/admin/.openclaw/workspace/stock-dashboard/crypto.html', '数字货币', 'trades_crypto')

print("🎉 所有市场页面刷新功能添加完成！")
