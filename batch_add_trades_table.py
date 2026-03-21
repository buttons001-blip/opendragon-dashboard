#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量为所有市场页面添加交易记录表格
"""

import re

# 交易记录表格样式
TRADING_STYLE = """
        /* 交易记录表格样式 */
        .trades-table-wrapper {
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }
        .trades-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9em;
            min-width: 600px;
        }
        .trades-table th {
            background: #f5f5f5;
            padding: 12px 10px;
            border: 1px solid #ddd;
            font-weight: bold;
            color: #333;
            white-space: nowrap;
            font-size: 0.95em;
        }
        .trades-table td {
            padding: 12px 10px;
            border: 1px solid #ddd;
            line-height: 1.6;
            vertical-align: top;
        }
        .trades-table .type-cell { font-weight: bold; white-space: nowrap; }
        .trades-table .type-充值 { color: #2e7d32; }
        .trades-table .type-提现 { color: #f57c00; }
        .trades-table .type-买入 { color: #1565c0; }
        .trades-table .type-卖出 { color: #c62828; }
        .trades-table .code-cell { white-space: nowrap; font-family: monospace; font-weight: bold; }
        .trades-table .reason-cell {
            color: #666;
            font-size: 0.9em;
            white-space: normal;
            word-break: break-word;
            min-width: 180px;
        }
        .trades-table tr:nth-child(even) { background: #fafafa; }
        .trades-table tr:hover { background: #f0f0f0; }
        .trades-table tr.deposit-row { background: #e8f5e9 !important; }
        .trades-table tr.sell-row { background: #ffebee !important; }
        
        @media (max-width: 500px) {
            .trades-table {
                font-size: 1.1em;
                min-width: 700px;
            }
            .trades-table th {
                padding: 14px 8px;
                font-size: 1em;
            }
            .trades-table td {
                padding: 14px 8px;
                font-size: 1em;
            }
            .trades-table .reason-cell {
                font-size: 0.95em;
                min-width: 200px;
            }
        }
"""

# 交易记录表格 HTML
TRADING_TABLE_HTML = """
            <div class="card" v-if="transactions.length > 0">
                <div class="card-header">
                    <div class="card-title">交易记录</div>
                </div>
                <div class="trades-table-wrapper">
                    <table class="trades-table">
                        <thead>
                            <tr>
                                <th>日期</th>
                                <th>类型</th>
                                <th>代码</th>
                                <th>名称</th>
                                <th>价格</th>
                                <th>数量</th>
                                <th>金额</th>
                                <th>原因</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="t in transactions" :key="t.id" 
                                :class="{'deposit-row': t.type === '充值', 'sell-row': t.type === '卖出'}">
                                <td>{{ t.date }}</td>
                                <td class="type-cell" :class="'type-' + t.type">{{ t.type }}</td>
                                <td class="code-cell">{{ t.code || '-' }}</td>
                                <td>{{ t.name }}</td>
                                <td>¥{{ t.price }}</td>
                                <td>{{ t.quantity }}</td>
                                <td>¥{{ formatNum(t.amount) }}</td>
                                <td class="reason-cell">{{ t.reason || '-' }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
"""

def add_style(filename, market_name):
    """添加样式到文件"""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已添加
    if 'trades-table-wrapper' in content:
        print(f"✓ {filename}: 样式已存在")
        return False
    
    # 找到</style>标签前插入
    if '</style>' in content:
        content = content.replace('</style>', TRADING_STYLE + '\n    </style>')
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ {filename}: 样式已添加")
        return True
    else:
        print(f"✗ {filename}: 未找到</style>标签")
        return False

def add_table_html(filename, market_name):
    """添加交易记录表格 HTML"""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已添加
    if 'transactions.length' in content:
        print(f"✓ {filename}: 表格已存在")
        return False
    
    # 找到合适的位置插入（在最后一个</div>之前，通常在</div>\n    </div>\n</body>之前）
    # 找到持仓明细的卡片后面
    pattern = r'(</div>\n        </div>\n    </div>\n</body>)'
    if re.search(pattern, content):
        content = re.sub(pattern, TRADING_TABLE_HTML + r'\1', content)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ {filename}: 表格 HTML 已添加")
        return True
    else:
        print(f"✗ {filename}: 未找到插入位置")
        return False

def main():
    pages = [
        ('hk.html', '港股'),
        ('us.html', '美股'),
        ('ca.html', '加股'),
        ('crypto.html', '数字货币')
    ]
    
    print("开始批量添加交易记录表格...\n")
    
    for filename, market in pages:
        print(f"处理 {market} ({filename}):")
        add_style(filename, market)
        add_table_html(filename, market)
        print()
    
    print("完成！")

if __name__ == '__main__':
    main()
