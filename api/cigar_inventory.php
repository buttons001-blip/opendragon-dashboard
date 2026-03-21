<?php
/**
 * 雪茄库存数据API
 * 从飞书多维表格实时读取数据
 */

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');

// Feishu Config
$appToken = 'EvEyb9B0VaHcV9sl5WbcrLZYn7d';
$tableId = 'tbl1oOymZ0nv8rp2';
$appId = 'cli_a93fa577bff89bc2';
$appSecret = '2Fi2KePv87sLiTmZSPUcdeWa5Ty2MxQF';

// Get access token from Feishu
function getFeishuToken($appId, $appSecret) {
    $url = 'https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal';
    
    $postData = json_encode([
        'app_id' => $appId,
        'app_secret' => $appSecret
    ]);
    
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $postData);
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Content-Type: application/json'
    ]);
    curl_setopt($ch, CURLOPT_TIMEOUT, 30);
    
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    if ($httpCode !== 200) {
        return null;
    }
    
    $data = json_decode($response, true);
    return $data['app_access_token'] ?? null;
}

// Get token
$token = getFeishuToken($appId, $appSecret);

if (!$token) {
    http_response_code(500);
    echo json_encode(['error' => 'Failed to get Feishu access token']);
    exit;
}

// Fetch all records from Feishu
$allRecords = [];
$pageToken = null;
$maxPages = 10;
$pageCount = 0;

do {
    $url = "https://open.feishu.cn/open-apis/bitable/v1/apps/{$appToken}/tables/{$tableId}/records?page_size=500";
    if ($pageToken) {
        $url .= "&page_token=" . urlencode($pageToken);
    }
    
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        "Authorization: Bearer {$token}",
        "Content-Type: application/json"
    ]);
    curl_setopt($ch, CURLOPT_TIMEOUT, 30);
    
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    if ($httpCode !== 200) {
        http_response_code(500);
        echo json_encode(['error' => 'Failed to fetch from Feishu', 'httpCode' => $httpCode]);
        exit;
    }
    
    $data = json_decode($response, true);
    
    if ($data['code'] !== 0) {
        http_response_code(500);
        echo json_encode(['error' => 'Feishu API error', 'msg' => $data['msg'] ?? 'Unknown error']);
        exit;
    }
    
    $items = $data['data']['items'] ?? [];
    $allRecords = array_merge($allRecords, $items);
    
    $hasMore = $data['data']['has_more'] ?? false;
    $pageToken = $data['data']['page_token'] ?? null;
    $pageCount++;
    
} while ($hasMore && $pageToken && $pageCount < $maxPages);

// Process records
$inventory = [];
$brands = [];

foreach ($allRecords as $record) {
    $fields = $record['fields'] ?? [];
    
    // Extract brand (SingleSelect)
    $brand = $fields['品牌'] ?? '';
    if (is_array($brand) && isset($brand['text'])) {
        $brand = $brand['text'];
    }
    
    // Extract model (Text)
    $model = $fields['型号'] ?? '';
    
    if ($brand && $model) {
        $inventory[] = [
            'brand' => $brand,
            'model' => $model,
            'quantity' => $fields['数量'] ?? '',
            'ringGauge' => $fields['环径'] ?? '',
            'length' => $fields['长度'] ?? '',
            'location' => $fields['地点'] ?? '',
            'arrived' => $fields['到货'] ?? '',
            'price' => $fields['现单价'] ?? '',
            'totalValue' => $fields['预估总价'] ?? ''
        ];
        
        $brands[] = $brand;
    }
}

// Get unique brands
$brands = array_unique($brands);
sort($brands);

// Output
$result = [
    'success' => true,
    'brands' => $brands,
    'inventory' => $inventory,
    'totalRecords' => count($inventory),
    'lastUpdated' => date('Y-m-d H:i:s')
];

echo json_encode($result, JSON_UNESCAPED_UNICODE);
