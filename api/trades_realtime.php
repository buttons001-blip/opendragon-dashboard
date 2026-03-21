<?php
/**
 * 股票交易数据实时API
 * 直接从飞书读取最新数据
 */

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');

// Feishu Config
$appToken = 'R9u7b3UTeagvfrsQEiGcgG7snBc';
$tableId = 'tblYYndqV1vTDg8I';
$appId = 'cli_a93fa577bff89bc2';
$appSecret = '2Fi2KePv87sLiTmZSPUcdeWa5Ty2MxQF';

// Get access token
function getToken($appId, $appSecret) {
    $url = 'https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal';
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode(['app_id' => $appId, 'app_secret' => $appSecret]));
    curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
    curl_setopt($ch, CURLOPT_TIMEOUT, 30);
    $response = curl_exec($ch);
    curl_close($ch);
    $data = json_decode($response, true);
    return $data['app_access_token'] ?? null;
}

// Fetch records from Feishu
function fetchRecords($appToken, $tableId, $token) {
    $records = [];
    $pageToken = null;
    
    do {
        $url = "https://open.feishu.cn/open-apis/bitable/v1/apps/{$appToken}/tables/{$tableId}/records?page_size=500";
        if ($pageToken) $url .= "&page_token=" . urlencode($pageToken);
        
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, ["Authorization: Bearer {$token}"]);
        curl_setopt($ch, CURLOPT_TIMEOUT, 30);
        $response = curl_exec($ch);
        curl_close($ch);
        
        $data = json_decode($response, true);
        if ($data['code'] !== 0) break;
        
        $records = array_merge($records, $data['data']['items'] ?? []);
        $hasMore = $data['data']['has_more'] ?? false;
        $pageToken = $data['data']['page_token'] ?? null;
    } while ($hasMore && $pageToken);
    
    return $records;
}

// Process records
function processRecords($records) {
    $trades = [];
    
    foreach ($records as $record) {
        $fields = $record['fields'] ?? [];
        
        // Map Feishu fields to trade format
        $market = $fields['市场'] ?? '';
        if (is_array($market)) $market = $market['text'] ?? '';
        
        $type = $fields['交易类型'] ?? '';
        if (is_array($type)) $type = $type['text'] ?? '';
        
        $status = $fields['状态'] ?? '';
        if (is_array($status)) $status = $status['text'] ?? '';
        
        $trades[] = [
            'type' => $type,
            'market' => $market,
            'code' => $fields['代码'] ?? '',
            'name' => $fields['名称'] ?? '',
            'price' => $fields['成交价'] ?? 0,
            'quantity' => $fields['数量'] ?? 0,
            'amount' => $fields['成交金额'] ?? 0,
            'date' => $fields['交易日期'] ?? '',
            'status' => $status,
            'reason' => $fields['备注'] ?? ''
        ];
    }
    
    return $trades;
}

// Main
$token = getToken($appId, $appSecret);
if (!$token) {
    http_response_code(500);
    echo json_encode(['error' => 'Failed to get token']);
    exit;
}

$records = fetchRecords($appToken, $tableId, $token);
$trades = processRecords($records);

// Return in same format as JSON file
$result = [
    'success' => true,
    'market' => 'A股',
    'trades' => $trades,
    'totalRecords' => count($trades),
    'source' => 'feishu_realtime',
    'lastUpdated' => date('Y-m-d H:i:s')
];

echo json_encode($result, JSON_UNESCAPED_UNICODE);
