#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为所有市场页面添加刷新功能
"""

import re
import sys

def add_refresh_feature(html_file, market_name):
    print(f"🔧 处理 {market_name} ({html_file})...")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 添加 data 属性
    if 'lastUpdateTime:' not in content:
        content = content.replace(
            "apiStatus: '连接中...',",
            """apiStatus: '连接中...',
                    lastUpdateTime: null,
                    lastVersion: null,
                    updateToast: { show: false, message: '' },
                    autoRefreshTimer: null,
                    refreshing: false,"""
        )
        print(f"  ✅ 添加 data 属性")
    
    # 2. 修改 mounted 方法，添加自动轮询
    old_mounted = """async mounted() {
                // 从飞书读取交易记录
                await this.loadFeishuData();
                
                this.updateTime();
                this.fetchPrices();
                
                // 每秒更新时间
                setInterval(() => this.updateTime(), 1000);
                
                // 每 30 秒刷新价格（交易时间）
                setInterval(() => {
                    if (this.isTradingTime) {
                        this.fetchPrices();
                    }
                }, 30000);
            },"""
    
    new_mounted = """async mounted() {
                // 从飞书读取交易记录
                await this.loadFeishuData();
                
                this.updateTime();
                this.fetchPrices();
                
                // 每秒更新时间
                setInterval(() => this.updateTime(), 1000);
                
                // 每 30 秒刷新价格（交易时间）
                setInterval(() => {
                    if (this.isTradingTime) {
                        this.fetchPrices();
                    }
                }, 30000);
                
                // 每 30 秒自动检查数据更新
                this.autoRefreshTimer = setInterval(() => {
                    this.checkForUpdates();
                }, 30000);
            },
            
            beforeDestroy() {
                // 清理定时器
                if (this.autoRefreshTimer) {
                    clearInterval(this.autoRefreshTimer);
                }
            },"""
    
    if old_mounted in content:
        content = content.replace(old_mounted, new_mounted)
        print(f"  ✅ 添加 mounted 轮询")
    
    # 3. 添加 checkForUpdates 和 refreshData 方法
    old_refresh = """                        await this.loadFeishuData();
                    }
                },"""
    
    new_refresh = """                        await this.loadFeishuData();
                    }
                },
                
                // 检查数据更新（轮询）
                async checkForUpdates() {
                    try {
                        const response = await fetch('data/trades_"""+html_file.replace('.html', '').split('/')[-1]+""".json?t=' + Date.now());
                        const data = await response.json();
                        
                        // 对比时间戳
                        if (data.timestamp !== this.lastVersion) {
                            await this.loadFeishuData();
                            this.showUpdateToast('📊 数据已更新');
                        }
                    } catch (e) {
                        console.log('轮询检查失败:', e);
                    }
                },
                
                // 手动刷新数据
                async refreshData() {
                    if (this.refreshing) return;
                    
                    this.refreshing = true;
                    try {
                        // 先尝试实时 API
                        const response = await fetch('api/trades_realtime.php?t=' + Date.now());
                        const data = await response.json();
                        
                        if (data.success) {
                            this.processTradeData(data);
                            this.apiStatus = '飞书实时数据 ✓ ' + new Date().toLocaleTimeString();
                            this.apiStatusClass = 'success';
                            this.showUpdateToast('✅ 数据已刷新');
                        } else {
                            throw new Error(data.error || 'API error');
                        }
                    } catch (e) {
                        console.error('实时刷新失败:', e);
                        // 降级到本地 JSON
                        await this.loadFeishuData();
                        this.showUpdateToast('📊 已加载本地数据');
                    }
                    this.refreshing = false;
                },
                
                // 显示更新提示
                showUpdateToast(message) {
                    this.updateToast = { show: true, message: message };
                    setTimeout(() => {
                        this.updateToast.show = false;
                    }, 3000);
                },"""
    
    if 'checkForUpdates' not in content and old_refresh in content:
        content = content.replace(old_refresh, new_refresh)
        print(f"  ✅ 添加刷新方法")
    
    # 4. 在 processTradeData 方法中记录最后更新时间
    old_process = "// 处理交易数据（统一入口）\n                processTradeData(data) {"
    new_process = """// 处理交易数据（统一入口）
                processTradeData(data) {
                    // 记录最后更新时间
                    this.lastUpdateTime = new Date().toLocaleTimeString('zh-CN', {hour: '2-digit', minute:'2-digit', second:'2-digit'});
                    this.lastVersion = data.timestamp || new Date().toISOString();"""
    
    if old_process in content and 'lastUpdateTime' not in content:
        content = content.replace(old_process, new_process)
        print(f"  ✅ 添加更新时间记录")
    
    # 5. 添加 UI 元素（在 api-status 后）
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
    
    if old_ui in content and 'update-info' not in content:
        content = content.replace(old_ui, new_ui)
        print(f"  ✅ 添加 UI 元素")
    
    # 写入文件
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✅ {market_name} 完成\n")

# 处理所有市场页面
pages = [
    ('hk.html', '港股'),
    ('us.html', '美股'),
    ('ca.html', '加股'),
    ('crypto.html', '数字货币')
]

for html_file, market_name in pages:
    add_refresh_feature(f'/home/admin/.openclaw/workspace/stock-dashboard/{html_file}', market_name)

print("🎉 所有市场页面刷新功能添加完成！")
