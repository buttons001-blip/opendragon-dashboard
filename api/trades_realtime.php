<?php
/**
 * 股票交易数据实时API
 * 直接从飞书 openclaw 表格读取最新数据并计算
 */

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');

// Feishu Config - openclaw 表格
$appToken = 'GA4ibckhcahr6asxah0cOFZmn4b';
$tableId = 'tbl1tSS4VOOCDywu';
$appId = 'cli_a923ab8033781cc6';
$appSecret = '6znpJICLLDKf30qQE0usGmdgS4kFkt7S';

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

// Process records and calculate holdings
function processRecords($records, $marketFilter) {
    $trades = [];
    $holdings = [];
    $initialCapital = 0;
    $realizedProfit = 0;
    $cashBalance = 0;
    
    foreach ($records as $record) {
        $fields = $record['fields'] ?? [];
        
        // Get market
        $market = $fields['市场'] ?? '';
        if (is_array($market)) $market = $market['text'] ?? '';
        
        // Filter by market
        if ($market !== $marketFilter) continue;
        
        // Get other fields
        $type = $fields['操作类型'] ?? '';
        if (is_array($type)) $type = $type['text'] ?? '';
        
        $code = $fields['代码'] ?? '';
        $name = $fields['名称'] ?? '';
        $price = floatval($fields['价格'] ?? 0);
        $quantity = floatval($fields['数量'] ?? 0);
        $amount = floatval($fields['成交金额'] ?? 0);
        $reason = $fields['操作原因'] ?? '';
        $status = $fields['状态'] ?? '';
        
        // Process date
        $dateVal = $fields['日期'] ?? '';
        if (is_numeric($dateVal)) {
            $date = date('Y-m-d', $dateVal / 1000);
            // Fix year 2024 -> 2026
            if (strpos($date, '2024') === 0) $date = '2026' . substr($date, 4);
        } else {
            $date = $dateVal;
        }
        
        // Add to trades
        $trades[] = [
            'type' => $type,
            'code' => $code,
            'name' => $name,
            'price' => $price,
            'quantity' => $quantity,
            'amount' => $amount,
            'date' => $date,
            'status' => $status,
            'reason' => $reason
        ];
        
        // Calculate holdings and profit
        if ($type === '充值') {
            $initialCapital += $amount;
            $cashBalance += $amount;
        } elseif ($type === '提现') {
            $cashBalance -= $amount;
        } elseif ($type === '买入' && $code) {
            $cashBalance -= $amount;
            if (!isset($holdings[$code])) {
                $holdings[$code] = ['name' => $name, 'qty' => 0, 'cost' => 0, 'total_cost' => 0];
            }
            $holdings[$code]['qty'] += $quantity;
            $holdings[$code]['total_cost'] += $amount;
            if ($holdings[$code]['qty'] > 0) {
                $holdings[$code]['cost'] = $holdings[$code]['total_cost'] / $holdings[$code]['qty'];
            }
        } elseif ($type === '卖出' && $code) {
            $cashBalance += $amount;
            if (isset($holdings[$code]) && $holdings[$code]['qty'] > 0) {
                $avgCost = $holdings[$code]['cost'];
                $profit = ($price - $avgCost) * $quantity;
                $realizedProfit += $profit;
                $holdings[$code]['qty'] -= $quantity;
                $holdings[$code]['total_cost'] = $holdings[$code]['qty'] * $avgCost;
            }
        }
    }
    
    // Build holdings list
    $holdingsList = [];
    foreach ($holdings as $code => $h) {
        if ($h['qty'] > 0) {
            $holdingsList[] = [
                'code' => $code,
                'name' => $h['name'],
                'costPrice' => round($h['cost'], 2),
                'quantity' => $h['qty'],
                'totalCost' => round($h['total_cost'], 2)
            ];
        }
    }
    
    return [
        'trades' => $trades,
        'holdings' => $holdingsList,
        'initialCapital' => $initialCapital,
        'realizedProfit' => round($realizedProfit, 2),
        'availableCapital' => round($cashBalance, 2)
    ];
}

// Main
$token = getToken($appId, $appSecret);
if (!$token) {
    http_response_code(500);
    echo json_encode(['error' => 'Failed to get token']);
    exit;
}

// Get market from query parameter
$market = $_GET['market'] ?? 'A股';

$records = fetchRecords($appToken, $tableId, $token);
$result = processRecords($records, $market);

// Return data
$result['success'] = true;
$result['market'] = $market;
$result['totalRecords'] = count($result['trades']);
$result['source'] = 'feishu_realtime';
$result['lastUpdated'] = date('Y-m-d H:i:s');

echo json_encode($result, JSON_UNESCAPED_UNICODE);
