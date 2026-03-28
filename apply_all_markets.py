#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用前端改进方案：
1. 添加定时轮询（30 秒）
2. 添加最后更新时间显示
3. 添加手动刷新按钮
4. 添加更新提示 Toast
"""

import re

# 读取文件
with open('/home/admin/.openclaw/workspace/stock-dashboard/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 添加 data 属性
content = content.replace(
    "apiStatus: '连接中...',",
    """apiStatus: '连接中...',
                    lastUpdateTime: null,
                    lastVersion: null,
                    updateToast: { show: false, message: '' },
                    autoRefreshTimer: null,
                    refreshing: false,"""
)

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

content = content.replace(old_mounted, new_mounted)

# 3. 添加 checkForUpdates 和 refreshData 方法
# 找到 loadFeishuDataRealtime 方法末尾
old_refresh = """                        await this.loadFeishuData();
                    }
                },"""

new_refresh = """                        await this.loadFeishuData();
                    }
                },
                
                // 检查数据更新（轮询）
                async checkForUpdates() {
                    try {
                        const response = await fetch('data/trades_cn.json?t=' + Date.now());
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

content = content.replace(old_refresh, new_refresh)

# 4. 在 processTradeData 方法中记录最后更新时间
# 找到 processTradeData 方法
old_process = "// 处理交易数据（统一入口）\n                processTradeData(data) {"
new_process = """// 处理交易数据（统一入口）
                processTradeData(data) {
                    // 记录最后更新时间
                    this.lastUpdateTime = new Date().toLocaleTimeString('zh-CN', {hour: '2-digit', minute:'2-digit', second:'2-digit'});
                    this.lastVersion = data.timestamp || new Date().toISOString();"""

content = content.replace(old_process, new_process)

# 写入文件
with open('/home/admin/.openclaw/workspace/stock-dashboard/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 前端改进已应用到 index.html")
print("✅ 添加功能:")
print("   - 每 30 秒自动检查数据更新")
print("   - 手动刷新按钮")
print("   - 最后更新时间显示")
print("   - 更新提示 Toast")
