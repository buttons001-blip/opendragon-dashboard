#!/usr/bin/env node

/**
 * 测试飞书 API 数据读取
 * 验证字段名映射和数据结构
 */

const fetch = require('node-fetch');

// 飞书配置
const FEISHU_CONFIG = {
    appToken: 'R9u7b3UTeagvfrsQEiGcgG7snBc',
    tableId: 'tblYYndqV1vTDg8I'
};

async function testFeishuAPI() {
    console.log('🔍 测试飞书 API 数据读取...\n');
    
    try {
        // 1. 获取字段列表
        console.log('📋 获取字段列表...');
        const fieldsResp = await fetch(`https://open.feishu.cn/open-apis/bitable/v1/apps/${FEISHU_CONFIG.appToken}/tables/${FEISHU_CONFIG.tableId}/fields`, {
            headers: {
                'Authorization': 'Bearer feishu_token_here' // 需要替换为实际 token
            }
        });
        
        if (fieldsResp.ok) {
            const fieldsData = await fieldsResp.json();
            console.log('字段列表:', JSON.stringify(fieldsData.data.fields.map(f => f.field_name), null, 2));
        }
        
        // 2. 获取记录数据
        console.log('\n📊 获取记录数据...');
        const recordsResp = await fetch(`https://open.feishu.cn/open-apis/bitable/v1/apps/${FEISHU_CONFIG.appToken}/tables/${FEISHU_CONFIG.tableId}/records?page_size=10`, {
            headers: {
                'Authorization': 'Bearer feishu_token_here'
            }
        });
        
        if (recordsResp.ok) {
            const recordsData = await recordsResp.json();
            console.log('记录数:', recordsData.data.items.length);
            
            // 打印第一条有数据的记录
            const firstRecord = recordsData.data.items.find(r => Object.keys(r.fields).length > 0);
            if (firstRecord) {
                console.log('\n第一条记录字段:');
                console.log(JSON.stringify(firstRecord.fields, null, 2));
            }
        }
        
    } catch (e) {
        console.error('❌ 错误:', e.message);
    }
}

testFeishuAPI();
