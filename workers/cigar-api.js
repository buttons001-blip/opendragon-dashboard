var __defProp = Object.defineProperty;
var __name = (target, value) => __defProp(target, "name", { value, configurable: true });

var corsHeaders = {
 "Access-Control-Allow-Origin": "*",
 "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
 "Access-Control-Allow-Headers": "Content-Type, Authorization",
 "Content-Type": "application/json"
};

var FIELD_MAPPING = {
 "storageLocation": "storage_location",
 "purchaseLocation": "purchase_location",
 "ringGauge": "ring_gauge",
 "tastingNotes": "tasting_notes",
 "remainingQuantity": "remaining_quantity"
};

function jsToDbField(jsField) {
 if (FIELD_MAPPING[jsField]) {
 return FIELD_MAPPING[jsField];
 }
 return jsField.replace(/([A-Z])/g, "_$1").toLowerCase();
}
__name(jsToDbField, "jsToDbField");

var cigar_api_default = {
 async fetch(request, env) {
 if (request.method === "OPTIONS") {
 return new Response(null, { headers: corsHeaders });
 }
 const url = new URL(request.url);
 const path = url.pathname;

 try {
 // === 库存 API ===
 // 适配完整路径 /cigar-api/api/v1/...
 if (path === "/cigar-api/api/v1/inventory/create" && request.method === "POST") {
 return await createInventoryRecord(request, env.DB);
 }
 if (path === "/cigar-api/api/v1/inventory/update" && request.method === "POST") {
 return await updateInventoryRecord(request, env.DB);
 }
 if (path === "/cigar-api/api/v1/inventory/list" && request.method === "GET") {
 return await listInventoryRecords(request, env.DB);
 }

 // === 品尝记录 API ===
 if (path === "/cigar-api/api/v1/tasting/create" && request.method === "POST") {
 return await createTastingRecord(request, env.DB);
 }

 // === 品牌/型号查询API ===
 if (path === "/cigar-api/api/v1/brands" && request.method === "GET") {
 return await listBrands(env.DB);
 }
 if (path.startsWith("/cigar-api/api/v1/brands/") && path.endsWith("/models") && request.method === "GET") {
 const brand = decodeURIComponent(path.split("/")[5]);
 return await listModelsByBrand(brand, env.DB);
 }
 if (path.startsWith("/cigar-api/api/v1/brands/") && request.method === "GET" && path.split("/").length === 7) {
 const parts = path.split("/");
 const brand = decodeURIComponent(parts[5]);
 const model = decodeURIComponent(parts[6]);
 return await getModelDetail(brand, model, env.DB);
 }

 return new Response("Not found: " + path, { status: 404, headers: corsHeaders });
 } catch (error) {
 console.error("API Error:", error);
 return new Response(JSON.stringify({
 success: false,
 error: error.message
 }), { status: 500, headers: corsHeaders });
 }
 }
};

// === 新增：获取品牌列表（含logo）===
async function listBrands(db) {
 try {
 const result = await db.prepare(
 "SELECT DISTINCT brand, logo, origin FROM cigar_inventory WHERE brand IS NOT NULL AND brand != '' ORDER BY brand"
 ).all();

 const brandMap = new Map();
 for (const row of (result.results || [])) {
 if (!brandMap.has(row.brand)) {
 brandMap.set(row.brand, {
 name: row.brand,
 logo: row.logo || "",
 origin: row.origin || ""
 });
 }
 }

 return new Response(JSON.stringify({
 success: true,
 brands: Array.from(brandMap.values())
 }), { headers: corsHeaders });
 } catch (error) {
 throw new Error("List brands failed: " + error.message);
 }
}
__name(listBrands, "listBrands");

// === 新增：获取某品牌下的型号列表 ===
async function listModelsByBrand(brand, db) {
 try {
 const result = await db.prepare(
 "SELECT DISTINCT model, ring_gauge, length, origin, strength, flavors, logo FROM cigar_inventory WHERE brand = ? AND model IS NOT NULL AND model != '' ORDER BY model"
 ).bind(brand).all();

 const modelMap = new Map();
 for (const row of (result.results || [])) {
 if (!modelMap.has(row.model)) {
 let flavors = [];
 try {
 flavors = row.flavors ? JSON.parse(row.flavors) : [];
 } catch(e) { flavors = []; }

 modelMap.set(row.model, {
 name: row.model,
 ringGauge: row.ring_gauge,
 length: row.length,
 origin: row.origin,
 strength: row.strength,
 flavors: flavors,
 logo: row.logo || ""
 });
 }
 }

 return new Response(JSON.stringify({
 success: true,
 brand: brand,
 models: Array.from(modelMap.values())
 }), { headers: corsHeaders });
 } catch (error) {
 throw new Error("List models failed: " + error.message);
 }
}
__name(listModelsByBrand, "listModelsByBrand");

// === 新增：获取型号详细信息 ===
async function getModelDetail(brand, model, db) {
 try {
 const result = await db.prepare(
 "SELECT * FROM cigar_inventory WHERE brand = ? AND model = ? ORDER BY created_at DESC LIMIT 1"
 ).bind(brand, model).first();

 if (!result) {
 return new Response(JSON.stringify({
 success: false,
 error: "Model not found"
 }), { status: 404, headers: corsHeaders });
 }

 let flavors = [];
 try {
 flavors = result.flavors ? JSON.parse(result.flavors) : [];
 } catch(e) { flavors = []; }

 return new Response(JSON.stringify({
 success: true,
 detail: {
 brand: result.brand,
 model: result.model,
 origin: result.origin,
 ringGauge: result.ring_gauge,
 length: result.length,
 strength: result.strength,
 flavors: flavors,
 logo: result.logo || ""
 }
 }), { headers: corsHeaders });
 } catch (error) {
 throw new Error("Get model detail failed: " + error.message);
 }
}
__name(getModelDetail, "getModelDetail");

// === 创建库存记录（支持logo base64）===
async function createInventoryRecord(request, db) {
 const data = await request.json();
 const { fields } = data;
 if (!fields.brand || !fields.model || !fields.origin) {
 return new Response(JSON.stringify({
 success: false,
 error: "Missing required fields: brand, model, origin"
 }), { status: 400, headers: corsHeaders });
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
 fields.storageLocation || "",
 fields.purchaseLocation || "",
 fields.packaging || "",
 fields.specification || "",
 fields.year || null,
 fields.strength || "",
 JSON.stringify(fields.flavors || []),
 fields.tastingNotes || "",
 fields.logo || "",
 fields.remainingQuantity || fields.quantity || 0
 ).run();
 return new Response(JSON.stringify({
 success: true,
 record_id: newId
 }), { headers: corsHeaders });
 } catch (error) {
 throw new Error("Create failed: " + error.message);
 }
}
__name(createInventoryRecord, "createInventoryRecord");

// === 更新库存记录（支持logo base64）===
async function updateInventoryRecord(request, db) {
 const data = await request.json();
 const { record_id, fields } = data;
 if (!record_id) {
 return new Response(JSON.stringify({
 success: false,
 error: "Missing record_id"
 }), { status: 400, headers: corsHeaders });
 }
 try {
 const fieldNames = Object.keys(fields);
 const allowedFields = [
 "brand", "model", "origin", "quantity", "ring_gauge", "length",
 "price", "storage_location", "purchase_location", "packaging",
 "specification", "year", "strength", "flavors", "tasting_notes",
 "logo", "remaining_quantity"
 ];
 const setClause = fieldNames.map((name) => {
 const dbField = jsToDbField(name);
 if (!allowedFields.includes(dbField)) {
 throw new Error("Invalid field: " + name);
 }
 return `${dbField} = ?`;
 }).join(", ");
 const values = fieldNames.map((name) => {
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
 }), { headers: corsHeaders });
 } catch (error) {
 throw new Error("Update failed: " + error.message);
 }
}
__name(updateInventoryRecord, "updateInventoryRecord");

async function createTastingRecord(request, db) {
 const data = await request.json();
 const { fields } = data;
 if (!fields.inventory_id || !fields.brand || !fields.model) {
 return new Response(JSON.stringify({
 success: false,
 error: "Missing required fields"
 }), { status: 400, headers: corsHeaders });
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
 fields.environment || "",
 fields.dateTime || new Date().toISOString(),
 fields.notes || "",
 fields.photos || ""
 ).run();
 return new Response(JSON.stringify({
 success: true,
 record_id: newId
 }), { headers: corsHeaders });
 } catch (error) {
 throw new Error("Tasting create failed: " + error.message);
 }
}
__name(createTastingRecord, "createTastingRecord");

async function listInventoryRecords(request, db) {
 try {
 const url = new URL(request.url);
 const limit = parseInt(url.searchParams.get("limit")) || 100;
 const offset = parseInt(url.searchParams.get("offset")) || 0;
 const result = await db.prepare(
 "SELECT * FROM cigar_inventory ORDER BY created_at DESC LIMIT ? OFFSET ?"
 ).bind(limit, offset).all();
 return new Response(JSON.stringify({
 success: true,
 records: result.results || []
 }), { headers: corsHeaders });
 } catch (error) {
 throw new Error("List failed: " + error.message);
 }
}
__name(listInventoryRecords, "listInventoryRecords");

export { cigar_api_default as default };
