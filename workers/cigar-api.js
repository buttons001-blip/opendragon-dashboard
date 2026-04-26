// ✅ 最终修复版 - 路径匹配包含 /cigar-api 前缀
const corsHeaders = {
 'Access-Control-Allow-Origin': '*',
 'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
 'Access-Control-Allow-Headers': 'Content-Type, Authorization',
 'Content-Type': 'application/json'
};

// 字段映射表
const FIELD_MAPPING = {
 'storageLocation': 'storage_location',
 'purchaseLocation': 'purchase_location',
 'ringGauge': 'ring_gauge',
 'tastingNotes': 'tasting_notes',
 'remainingQuantity': 'remaining_quantity'
};

function jsToDbField(jsField) {
 if (FIELD_MAPPING[jsField]) {
 return FIELD_MAPPING[jsField];
 }
 return jsField.replace(/([A-Z])/g, '_$1').toLowerCase();
}

function handleOptions(request) {
 return new Response(null, { headers: corsHeaders });
}

async function handleRequest(request) {
 // ✅ 关键：在 Service Worker 格式中，DB 是全局绑定变量
 const db = DB;
  
 const url = new URL(request.url);
 const path = url.pathname;

 // 调试日志
 console.log('Received path:', path);
 
 try {
 // ✅ 关键修正：匹配完整路径 /cigar-api/api/v1/...
 if (path === '/cigar-api/api/v1/inventory/create' && request.method === 'POST') {
 return await createInventoryRecord(request, db);
 }
 if (path === '/cigar-api/api/v1/inventory/update' && request.method === 'POST') {
 return await updateInventoryRecord(request, db);
 }
 if (path === '/cigar-api/api/v1/tasting/create' && request.method === 'POST') {
 return await createTastingRecord(request, db);
 }
 if (path === '/cigar-api/api/v1/inventory/list' && request.method === 'GET') {
 return await listInventoryRecords(request, db);
 }

 console.log('Path not matched:', path);
 return new Response('Not found', {
 status: 404,
 headers: corsHeaders
 });
 } catch (error) {
 console.error('API Error:', error);
 return new Response(JSON.stringify({
 success: false,
 error: error.message
 }), {
 status: 500,
 headers: corsHeaders
 });
 }
}

async function createInventoryRecord(request, db) {
 const data = await request.json();
 const { fields } = data;

 if (!fields.brand || !fields.model || !fields.origin) {
 return new Response(JSON.stringify({
 success: false,
 error: 'Missing required fields'
 }), {
 status: 400,
 headers: corsHeaders
 });
 }

 try {
 const result = await db.prepare(
 "INSERT INTO cigar_inventory (id, brand, model, origin, quantity, ring_gauge, length, price, storage_location, purchase_location, packaging, specification, year, strength, flavors, tasting_notes, logo, remaining_quantity) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
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
 fields.logo || '',
 fields.remainingQuantity || fields.quantity || 0
 ).run();

 return new Response(JSON.stringify({
 success: true,
 record_id: result.meta.last_row_id
 }), {
 headers: corsHeaders
 });
 } catch (error) {
 throw new Error('Create failed: ' + error.message);
 }
}

async function updateInventoryRecord(request, db) {
 const data = await request.json();
 const { record_id, fields } = data;

 if (!record_id) {
 return new Response(JSON.stringify({
 success: false,
 error: 'Missing record_id'
 }), {
 status: 400,
 headers: corsHeaders
 });
 }

 try {
 const fieldNames = Object.keys(fields);
 const allowedFields = [
 'brand', 'model', 'origin', 'quantity', 'ring_gauge', 'length', 'price',
 'storage_location', 'purchase_location', 'packaging', 'specification',
 'year', 'strength', 'flavors', 'tasting_notes', 'logo', 'remaining_quantity'
 ];

 const setClause = fieldNames.map(name => {
 const dbField = jsToDbField(name);
 if (!allowedFields.includes(dbField)) {
 throw new Error('Invalid field: ' + name);
 }
 return `${dbField} = ?`; // ✅ 修正：添加反引号
 }).join(', ');

 const values = fieldNames.map(name => {
 const value = fields[name];
 if (Array.isArray(value)) {
 return JSON.stringify(value);
 }
 return value;
 });

 const sql = `UPDATE cigar_inventory SET ${setClause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?`; // ✅ 修正：添加反引号
 const allValues = [...values, record_id];

 let stmt = db.prepare(sql);
 for (const value of allValues) {
 stmt = stmt.bind(value);
 }
 await stmt.run();

 return new Response(JSON.stringify({
 success: true
 }), {
 headers: corsHeaders
 });
 } catch (error) {
 throw new Error('Update failed: ' + error.message);
 }
}

async function createTastingRecord(request, db) {
 const data = await request.json();
 const { fields } = data;

 if (!fields.inventory_id || !fields.brand || !fields.model) {
 return new Response(JSON.stringify({
 success: false,
 error: 'Missing required fields'
 }), {
 status: 400,
 headers: corsHeaders
 });
 }

 try {
 const result = await db.prepare(
 "INSERT INTO tasting_records (id, inventory_id, brand, model, environment, date_time, notes, photos) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
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
 headers: corsHeaders
 });
 } catch (error) {
 throw new Error('Tasting create failed: ' + error.message);
 }
}

async function listInventoryRecords(request, db) {
 try {
 const url = new URL(request.url);
 const limit = parseInt(url.searchParams.get('limit')) || 100;
 const offset = parseInt(url.searchParams.get('offset')) || 0;

 const result = await db.prepare(
 "SELECT * FROM cigar_inventory ORDER BY created_at DESC LIMIT ? OFFSET ?"
 ).bind(limit, offset).all();

 return new Response(JSON.stringify({
 success: true,
 records: result.results || []
 }), {
 headers: corsHeaders
 });
 } catch (error) {
 throw new Error('List failed: ' + error.message);
 }
}

// ✅ 修正：Service Worker 格式下直接使用全局 DB 变量
addEventListener('fetch', event => {
 const request = event.request;
 if (request.method === 'OPTIONS') {
 event.respondWith(handleOptions(request));
 return;
 }
 event.respondWith(handleRequest(request)); // 不再传递 env 参数
});