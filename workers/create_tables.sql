-- 库存记录表
CREATE TABLE IF NOT EXISTS cigar_inventory (
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
);

-- 品吸记录表
CREATE TABLE IF NOT EXISTS tasting_records (
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
);

-- 通用品牌表  
CREATE TABLE IF NOT EXISTS brand_universe (
    brand_name TEXT PRIMARY KEY,
    brand_type TEXT,
    origin_country TEXT,
    story TEXT,
    logo_url TEXT,
    models TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_cigar_brand ON cigar_inventory(brand);
CREATE INDEX IF NOT EXISTS idx_cigar_model ON cigar_inventory(model);
CREATE INDEX IF NOT EXISTS idx_tasting_inventory ON tasting_records(inventory_id);
CREATE INDEX IF NOT EXISTS idx_brand_name ON brand_universe(brand_name);