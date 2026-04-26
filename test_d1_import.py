#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地测试 D1 数据导入逻辑
"""

import json
import sqlite3
from pathlib import Path

def create_local_db():
    """创建本地 SQLite 数据库模拟 D1"""
    db_path = Path("test_cigar_inventory.db")
    if db_path.exists():
        db_path.unlink()
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # 创建表结构（与 D1 相同）
    cursor.execute('''
    CREATE TABLE cigar_inventory (
        id TEXT PRIMARY KEY,
        brand TEXT NOT NULL,
        model TEXT NOT NULL,
        origin TEXT,
        quantity REAL,
        ring_gauge REAL,
        length REAL,
        price REAL,
        storage_location TEXT,
        purchase_location TEXT,
        packaging TEXT,
        specification TEXT,
        year REAL,
        strength TEXT,
        flavors TEXT,
        tasting_notes TEXT,
        logo TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE tasting_records (
        id TEXT PRIMARY KEY,
        inventory_id TEXT,
        brand TEXT,
        model TEXT,
        environment TEXT,
        date_time TIMESTAMP,
        notes TEXT,
        photos TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (inventory_id) REFERENCES cigar_inventory(id)
    )
    ''')
    
    conn.commit()
    return conn

def load_test_data():
    """加载测试数据"""
    with open('data/cigar_inventory.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['cigars']

def import_test_records(conn):
    """导入测试记录"""
    cursor = conn.cursor()
    
    # 选择2条测试记录
    test_records = []
    for cigar in load_test_data():
        if cigar['brand'] == 'Punch' and cigar['model'] == 'Coronas A/T':
            test_records.append(cigar)
            break
    
    for cigar in load_test_data():
        if cigar['brand'] == 'My Father':
            test_records.append(cigar)
            break
    
    print(f"找到 {len(test_records)} 条测试记录")
    
    for record in test_records:
        cursor.execute('''
        INSERT INTO cigar_inventory 
        (id, brand, model, origin, quantity, ring_gauge, length, price, 
         storage_location, purchase_location, packaging, specification, year, 
         strength, flavors, tasting_notes, logo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            record.get('id', ''),
            record['brand'],
            record['model'],
            record['origin'],
            record.get('quantity', 0),
            record.get('ringGauge'),
            record.get('length'),
            record.get('price'),
            record.get('storageLocation', ''),
            record.get('purchaseLocation', ''),
            record.get('packaging', ''),
            record.get('specification', ''),
            record.get('year'),
            record.get('strength', ''),
            json.dumps(record.get('flavors', [])),
            record.get('tastingNotes', ''),
            record.get('logo', '')
        ))
    
    conn.commit()
    print("✅ 测试记录导入成功！")

def verify_import(conn):
    """验证导入结果"""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM cigar_inventory")
    count = cursor.fetchone()[0]
    print(f"数据库中总记录数: {count}")
    
    cursor.execute("SELECT brand, model, origin, strength FROM cigar_inventory LIMIT 5")
    records = cursor.fetchall()
    print("\n前5条记录:")
    for record in records:
        print(f"- {record[0]} {record[1]} ({record[2]}) - 强度: {record[3]}")

def main():
    print("🧪 本地 D1 导入测试")
    print("=" * 40)
    
    conn = create_local_db()
    import_test_records(conn)
    verify_import(conn)
    
    conn.close()
    print("\n✅ 本地测试完成！")

if __name__ == '__main__':
    main()