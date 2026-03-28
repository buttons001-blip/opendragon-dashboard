#!/usr/bin/env python3
"""
股票交易数据实时API服务器
"""

import http.server
import socketserver
import json
import os
import sys
import urllib.parse

# Import from api directory
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api'))
from trades_realtime import fetch_records, process_records

PORT = 8889

class APIHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse URL
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)
        
        if path == '/api/trades_realtime':
            # Get market parameter and decode
            market = query.get('market', ['A股'])[0]
            # Handle URL encoding
            market = urllib.parse.unquote(market)
            # Handle byte string issue
            if isinstance(market, bytes):
                market = market.decode('utf-8')
            # Fix common encoding issues
            market = market.replace('Aè\x82¡', 'A股').replace('AÃ¨', 'A股')
            
            # Fetch data
            records = fetch_records()
            if records:
                result = process_records(records, market)
                result['success'] = True
                result['market'] = market
                result['totalRecords'] = len(result['trades'])
                result['source'] = 'feishu_realtime'
                from datetime import datetime
                result['lastUpdated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            else:
                result = {'error': 'Failed to fetch records'}
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        print(f"[API] {format % args}")

def main():
    with socketserver.TCPServer(('', PORT), APIHandler) as httpd:
        print(f'API服务器运行在端口 {PORT}')
        print(f'测试: http://localhost:{PORT}/api/trades_realtime?market=A股')
        httpd.serve_forever()

if __name__ == '__main__':
    main()
