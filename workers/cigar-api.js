// ✅ ES Module 格式 - 完全支持 D1 绑定
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

export default {
 async fetch(request, env) {
 if (request.method === 'OPTIONS') {
 return new Response(null, { headers: corsHeaders });
 }
 
 const url = new URL(request.url);
 const path = url.pathname;

 try {
 // ✅ ES Module 格式：通过 env.DB 访问 D1
 if (path === '/cigar-api/api/v1/inventory/create' && request.method === 'POST') {
 return await createInventoryRecord(request, env.DB);
 }
 if (path === '/cigar-api/api/v1/inventory/update' && request.method === 'POST') {
 return await updateInventoryRecord(request, env.DB);
 }
 if (path === '/cigar-api/api/v1/tasting/create' && request.method === 'POST') {
 return await createTastingRecord(request, env.DB);
 }
 if (path === '/cigar-api/api/v1/inventory/list' && request.method === 'GET') {
 return await listInventoryRecords(request, env.DB);
 }

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
};

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
 const newId = crypto.randomUUID();
 await db.prepare(
 "INSERT INTO cigar_inventory (id, brand, model, origin, quantity, ring_gauge, length, price, storage_location, purchase_location, packaging, specification, year, strength, flavors, tasting_notes, logo, remaining_quantity) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
 ).bind(
 newId,
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
 record_id: newId
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
 return `${dbField} = ?`;
 }).join(', ');

 const values = fieldNames.map(name => {
 const value = fields[name];
 if (Array.isArray(value)) {
 return JSON.stringify(value);
 }
 return value;
 });

 const sql = `UPDATE cigar_inventory SET ${setClause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?`;
 const allValues = [...values, record_id];

 await db.prepare(sql).bind(...allValues).run();

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
 const newId = crypto.randomUUID();
 await db.prepare(
 "INSERT INTO tasting_records (id, inventory_id, brand, model, environment, date_time, notes, photos) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
 ).bind(
 newId,
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
 record_id: newId
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