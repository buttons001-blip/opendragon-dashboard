export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;
    
    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };
    
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }
    
    try {
      if (path === '/api/v1/inventory/create' && request.method === 'POST') {
        return await createInventoryRecord(request, env, corsHeaders);
      }
      if (path === '/api/v1/inventory/update' && request.method === 'POST') {
        return await updateInventoryRecord(request, env, corsHeaders);
      }
      if (path === '/api/v1/tasting/create' && request.method === 'POST') {
        return await createTastingRecord(request, env, corsHeaders);
      }
      if (path === '/api/v1/inventory/list' && request.method === 'GET') {
        return await listInventoryRecords(request, env, corsHeaders);
      }
    } catch (error) {
      console.error('API Error:', error);
      return new Response(JSON.stringify({ 
        success: false, 
        error: error.message 
      }), { 
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }
    
    return new Response('Not found', { 
      status: 404,
      headers: corsHeaders
    });
  }
};

async function createInventoryRecord(request, env, corsHeaders) {
  const data = await request.json();
  const { fields } = data;
  
  // 验证必填字段
  if (!fields.brand || !fields.model || !fields.origin) {
    return new Response(JSON.stringify({ 
      success: false, 
      error: 'Missing required fields: brand, model, origin' 
    }), { 
      status: 400,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
  
  try {
    // 插入到 D1 数据库
    const result = await env.DB.prepare(
      `INSERT INTO cigar_inventory 
       (id, brand, model, origin, quantity, ring_gauge, length, price, 
        storage_location, purchase_location, packaging, specification, year, 
        strength, flavors, tasting_notes, logo)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
    ).bind(
      crypto.randomUUID(),
      fields.brand,
      fields.model,
      fields.origin,
      fields.quantity || 0,
      fields.ringGauge || null,
      fields.length || null,
      fields.price || null,
      fields.storageLocation || '',
      fields.purchaseLocation || '',
      fields.packaging || '',
      fields.specification || '',
      fields.year || null,
      fields.strength || '',
      JSON.stringify(fields.flavors || []),
      fields.tastingNotes || '',
      fields.logo || ''
    ).run();
    
    return new Response(JSON.stringify({ 
      success: true, 
      record_id: result.meta.last_row_id 
    }), { 
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  } catch (error) {
    throw new Error('Failed to create inventory record: ' + error.message);
  }
}

async function updateInventoryRecord(request, env, corsHeaders) {
  const data = await request.json();
  const { record_id, fields } = data;
  
  if (!record_id) {
    return new Response(JSON.stringify({ 
      success: false, 
      error: 'Missing record_id' 
    }), { 
      status: 400,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
  
  try {
    // 构建动态更新语句
    const fieldNames = Object.keys(fields);
    const setClause = fieldNames.map(name => {
      // 转换 JavaScript 字段名到数据库字段名
      const dbField = jsToDbField(name);
      return `${dbField} = ?`;
    }).join(', ');
    
    const values = fieldNames.map(name => {
      const value = fields[name];
      // 处理数组类型（如 flavors）
      if (Array.isArray(value)) {
        return JSON.stringify(value);
      }
      return value;
    });
    
    const sql = `UPDATE cigar_inventory SET ${setClause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?`;
    const allValues = [...values, record_id];
    
    const stmt = env.DB.prepare(sql);
    const boundStmt = allValues.reduce((stmt, value) => stmt.bind(value), stmt);
    await boundStmt.run();
    
    return new Response(JSON.stringify({ 
      success: true 
    }), { 
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  } catch (error) {
    throw new Error('Failed to update inventory record: ' + error.message);
  }
}

async function createTastingRecord(request, env, corsHeaders) {
  const data = await request.json();
  const { fields } = data;
  
  if (!fields.inventory_id || !fields.brand || !fields.model) {
    return new Response(JSON.stringify({ 
      success: false, 
      error: 'Missing required fields: inventory_id, brand, model' 
    }), { 
      status: 400,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
  
  try {
    const result = await env.DB.prepare(
      `INSERT INTO tasting_records 
       (id, inventory_id, brand, model, environment, date_time, notes, photos)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)`
    ).bind(
      crypto.randomUUID(),
      fields.inventory_id,
      fields.brand,
      fields.model,
      fields.environment || '',
      fields.dateTime || new Date().toISOString(),
      fields.notes || '',
      fields.photos || ''
    ).run();
    
    return new Response(JSON.stringify({ 
      success: true, 
      record_id: result.meta.last_row_id 
    }), { 
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  } catch (error) {
    throw new Error('Failed to create tasting record: ' + error.message);
  }
}

async function listInventoryRecords(request, env, corsHeaders) {
  try {
    const { limit = 100, offset = 0 } = Object.fromEntries(new URL(request.url).searchParams);
    const result = await env.DB.prepare(
      `SELECT * FROM cigar_inventory ORDER BY created_at DESC LIMIT ? OFFSET ?`
    ).bind(parseInt(limit), parseInt(offset)).all();
    
    return new Response(JSON.stringify({ 
      success: true, 
      records: result.results 
    }), { 
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  } catch (error) {
    throw new Error('Failed to list inventory records: ' + error.message);
  }
}

// JavaScript 字段名转数据库字段名
function jsToDbField(jsField) {
  return jsField.replace(/([A-Z])/g, '_$1').toLowerCase();
}