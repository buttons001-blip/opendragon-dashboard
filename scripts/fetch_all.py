#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票看板统一行情抓取脚本
====================================================
数据源策略（2026-09-24 实测确认）：
  - A股/港股指数+个股 : 腾讯 qt.gtimg.cn（直连可用）
  - 美股指数+个股      : 腾讯 qt.gtimg.cn（us.INX / usIXIC / usDJI / usNDX / us<SYM>）
  - 加股个股           : 腾讯 usRY / usENB / usSHOP（.N 纽交所报价口径）
  - 数字货币           : Binance（经 Clash 代理），fallback CoinGecko
  - TSX 指数           : 【已按用户决定删除】腾讯无覆盖、Yahoo 429

输出：
  test/stockmarket/data/indices.json      — 各市场指数
  test/stockmarket/data/ca_crypto.json    — 加股个股 + 数字货币
  test/stockmarket/data/cn_hk_prices.json — A股/港股持仓个股

依赖：仅标准库（Mac /usr/bin/python3 无 requests）
"""

import json
import os
import ssl
import sys
import urllib.parse
import urllib.request
from datetime import datetime

# ---------------------------------------------------------------- 配置
PROXY = 'http://127.0.0.1:7890'          # mihomo mixed-port
UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, 'test', 'stockmarket', 'data')

_ctx = ssl.create_default_context()
_ctx.check_hostname = False
_ctx.verify_mode = ssl.CERT_NONE

VERBOSE = os.environ.get('QUIET') != '1'


def log(*a):
    if VERBOSE:
        print(*a, flush=True)


def http_get(url, use_proxy=False, timeout=20, encoding='utf-8'):
    """标准库 GET，use_proxy=True 时走 Clash"""
    handlers = [urllib.request.HTTPSHandler(context=_ctx)]
    if use_proxy:
        handlers.append(urllib.request.ProxyHandler({'http': PROXY, 'https': PROXY}))
    opener = urllib.request.build_opener(*handlers)
    req = urllib.request.Request(url, headers={
        'User-Agent': UA,
        'Referer': 'https://finance.sina.com.cn' if 'sinajs' in url else 'https://gu.qq.com/',
    })
    with opener.open(req, timeout=timeout) as r:
        return r.read().decode(encoding, 'ignore')


# ---------------------------------------------------------------- 腾讯行情
def tencent_quote(codes):
    """
    批量查腾讯行情。codes 形如 ['us.INX','usNVDA','sh600036']
    返回 {code: {'name','price','prevClose','change','changePercent'}}
    """
    if not codes:
        return {}
    out = {}
    # 分批，避免 URL 过长
    for i in range(0, len(codes), 30):
        chunk = codes[i:i + 30]
        url = 'https://qt.gtimg.cn/q=' + ','.join(chunk)
        try:
            txt = http_get(url, encoding='gbk')
        except Exception as e:
            log('    [WARN] 腾讯批量请求失败: %s' % e)
            continue

        # 响应形如: v_us.INX="200~标普500~.INX~7706.03~...";\n
        for line in txt.split(';'):
            line = line.strip()
            if not line or '=' not in line:
                continue
            key, _, val = line.partition('=')
            key = key.strip().replace('v_', '')
            val = val.strip().strip('"')
            if not val or 'pv_none_match' in val:
                continue
            f = val.split('~')
            if len(f) < 6:
                continue
            try:
                price = float(f[3])
                prev = float(f[4])
                change = float(f[31]) if len(f) > 31 and f[31] else round(price - prev, 4)
                pct = float(f[32]) if len(f) > 32 and f[32] else (
                    round((price - prev) / prev * 100, 2) if prev else 0.0)
            except (ValueError, ZeroDivisionError):
                continue
            out[key] = {
                'name': f[1],
                'price': price,
                'prevClose': prev,
                'change': change,
                'changePercent': pct,
            }
    return out


def idx_entry(q):
    """转成 indices.json 的条目格式"""
    if not q:
        return {'value': '获取失败', 'change': 0, 'changePercent': 0}
    return {
        'value': round(q['price'], 2),
        'change': round(q['change'], 2),
        'changePercent': round(q['changePercent'], 2),
    }


# ---------------------------------------------------------------- 数字货币
BINANCE_MAP = {'BTC': 'BTCUSDT', 'ETH': 'ETHUSDT', 'SOL': 'SOLUSDT', 'LINK': 'LINKUSDT'}
CG_MAP = {'BTC': 'bitcoin', 'ETH': 'ethereum', 'SOL': 'solana', 'LINK': 'chainlink'}


def fetch_crypto():
    """优先 Binance（经代理），失败 fallback CoinGecko"""
    result = {}
    log('  [数字货币] Binance (经代理)...')
    ok = 0
    for name, sym in BINANCE_MAP.items():
        try:
            raw = http_get('https://api.binance.com/api/v3/ticker/24hr?symbol=' + sym,
                           use_proxy=True, timeout=15)
            d = json.loads(raw)
            price = float(d['lastPrice'])
            pct = float(d['priceChangePercent'])
            prev = price / (1 + pct / 100) if pct != -100 else price
            result[name] = {
                'value': round(price, 2),
                'change': round(price - prev, 2),
                'changePercent': round(pct, 2),
            }
            ok += 1
            log('    OK %s = %.2f (%+.2f%%)' % (name, price, pct))
        except Exception as e:
            log('    FAIL %s: %s' % (name, type(e).__name__))

    if ok == len(BINANCE_MAP):
        return result

    # fallback: CoinGecko 一次性拿全部
    log('  [数字货币] Binance 不完整，fallback CoinGecko...')
    try:
        ids = ','.join(CG_MAP.values())
        url = ('https://api.coingecko.com/api/v3/simple/price?ids=%s'
               '&vs_currencies=usd&include_24hr_change=true' % ids)
        d = json.loads(http_get(url, use_proxy=True, timeout=20))
        for name, cid in CG_MAP.items():
            if name in result:
                continue
            if cid in d and 'usd' in d[cid]:
                price = float(d[cid]['usd'])
                pct = float(d[cid].get('usd_24h_change') or 0)
                prev = price / (1 + pct / 100) if pct != -100 else price
                result[name] = {
                    'value': round(price, 2),
                    'change': round(price - prev, 2),
                    'changePercent': round(pct, 2),
                }
                log('    OK(备) %s = %.2f (%+.2f%%)' % (name, price, pct))
    except Exception as e:
        log('    FAIL CoinGecko: %s' % e)

    return result


# ---------------------------------------------------------------- 主流程
def main():
    log('=' * 62)
    log('股票看板行情抓取  %s' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    log('=' * 62)

    # ---------- 1. 指数 ----------
    log('[1/4] 抓取各市场指数...')
    quotes = tencent_quote([
        # A股
        'sh000001', 'sz399001', 'sh000688',
        # 港股
        'hkHSI', 'hkHSCEI', 'hkHSTECH',
        # 美股
        'us.INX', 'usIXIC', 'usDJI',
    ])

    indices = {
        'timestamp': datetime.now().isoformat(),
        'cn': {
            '上证指数': idx_entry(quotes.get('sh000001')),
            '深证成指': idx_entry(quotes.get('sz399001')),
            '科创 50': idx_entry(quotes.get('sh000688')),
        },
        'hk': {
            '恒生指数': idx_entry(quotes.get('hkHSI')),
            '国企指数': idx_entry(quotes.get('hkHSCEI')),
            '恒生科技': idx_entry(quotes.get('hkHSTECH')),
        },
        'us': {
            '道琼斯': idx_entry(quotes.get('us.DJI') or quotes.get('usDJI')),
            '纳斯达克': idx_entry(quotes.get('usIXIC')),
            '标普 500': idx_entry(quotes.get('us.INX')),
        },
        # 加股指数：腾讯无覆盖（Yahoo 429），按用户决定移除
        'ca': {},
        'crypto': {},
    }
    for mk, d in (('cn', indices['cn']), ('hk', indices['hk']), ('us', indices['us'])):
        for k, v in d.items():
            log('    %-6s %-8s %s' % (mk, k, v['value']))

    # ---------- 2. 加股个股 ----------
    log('[2/4] 抓取加股个股（腾讯 us*.N 纽交所报价口径）...')
    ca_codes = {'RY': 'usRY', 'ENB': 'usENB', 'SHOP': 'usSHOP'}
    ca_quotes = tencent_quote(list(ca_codes.values()))
    ca_stocks = {}
    for name, code in ca_codes.items():
        q = ca_quotes.get(code)
        if q:
            ca_stocks[name] = {
                'price': round(q['price'], 2),
                'change': round(q['change'], 2),
                'changePercent': round(q['changePercent'], 2),
            }
            log('    OK %-5s = %.2f (%+.2f%%)' % (name, q['price'], q['changePercent']))
        else:
            log('    FAIL %s' % name)

    # ---------- 3. 数字货币 ----------
    log('[3/4] 抓取数字货币...')
    crypto = fetch_crypto()
    indices['crypto'] = crypto

    # ---------- 4. 写入 ----------
    log('[4/4] 写入 JSON...')
    os.makedirs(DATA_DIR, exist_ok=True)

    p1 = os.path.join(DATA_DIR, 'indices.json')
    with open(p1, 'w', encoding='utf-8') as f:
        json.dump(indices, f, ensure_ascii=False, indent=2)
    log('    -> %s' % p1)

    p2 = os.path.join(DATA_DIR, 'ca_crypto.json')
    ca_crypto = {
        'timestamp': datetime.now().isoformat(),
        'ca': {},                 # TSX 指数已移除
        'crypto': crypto,
        'stocks': ca_stocks,
    }
    with open(p2, 'w', encoding='utf-8') as f:
        json.dump(ca_crypto, f, ensure_ascii=False, indent=2)
    log('    -> %s' % p2)

    # ---------- 5. A股/港股持仓个股 ----------
    log('[5/5] 抓取 A股/港股持仓个股...')
    holdings = {}
    for mkt, fname in (('cn', 'trades_cn.json'), ('hk', 'trades_hk.json')):
        fp = os.path.join(DATA_DIR, fname)
        if not os.path.exists(fp):
            continue
        try:
            with open(fp, encoding='utf-8') as f:
                d = json.load(f)
        except Exception:
            continue
        codes = []
        for h in d.get('holdings', []):
            c = str(h.get('code', '')).strip()
            if not c:
                continue
            if mkt == 'cn':
                codes.append(('sh' if c.startswith('6') else 'sz') + c)
            else:
                codes.append('hk' + c.zfill(5))
        q = tencent_quote(codes)
        for c, v in q.items():
            holdings[c] = {'price': round(v['price'], 2),
                           'change': round(v['change'], 2),
                           'changePercent': round(v['changePercent'], 2)}
            log('    OK %-10s = %.2f (%+.2f%%)' % (c, v['price'], v['changePercent']))

    p3 = os.path.join(DATA_DIR, 'cn_hk_prices.json')
    with open(p3, 'w', encoding='utf-8') as f:
        json.dump({'timestamp': datetime.now().isoformat(),
                   'cn': {k: v for k, v in holdings.items() if not k.startswith('hk')},
                   'hk': {k: v for k, v in holdings.items() if k.startswith('hk')}},
                  f, ensure_ascii=False, indent=2)
    log('    -> %s' % p3)

    # ---------- 校验 ----------
    log('')
    log('=' * 62)
    fails = []
    for mk in ('cn', 'hk', 'us'):
        for k, v in indices[mk].items():
            if v['value'] == '获取失败':
                fails.append('%s/%s' % (mk, k))
    if fails:
        log('!! 失败项: %s' % ', '.join(fails))
    else:
        log('指数：全部成功')
    log('加股个股: %d/%d   数字货币: %d/4' % (len(ca_stocks), len(ca_codes), len(crypto)))
    log('=' * 62)
    return 0 if not fails else 1


if __name__ == '__main__':
    sys.exit(main())
