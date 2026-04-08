#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw Monitor API - 简单的 HTTP API 包装器
提供健康检查和状态查询接口
"""

import json
import subprocess
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

# API Key 认证
API_KEY = os.getenv('OPENCLAW_MONITOR_API_KEY', 'opendragon2026')

class MonitorAPIHandler(BaseHTTPRequestHandler):
    def check_auth(self):
        """验证 API Key"""
        api_key = self.headers.get('x-api-key', '')
        return api_key == API_KEY
    
    def send_json(self, data, status=200):
        """发送 JSON 响应"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'x-api-key, Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
    
    def send_error_json(self, message, status=400):
        """发送错误响应"""
        self.send_json({'error': message}, status)
    
    def run_command(self, cmd):
        """运行 OpenClaw CLI 命令"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                # 尝试解析 JSON 输出
                try:
                    return json.loads(result.stdout)
                except:
                    return {'output': result.stdout}
            else:
                return {'error': result.stderr or f'Exit code: {result.returncode}'}
        except subprocess.TimeoutExpired:
            return {'error': 'Command timeout'}
        except Exception as e:
            return {'error': str(e)}
    
    def do_OPTIONS(self):
        """处理 CORS preflight 请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'x-api-key, Content-Type')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.end_headers()
    
    def do_GET(self):
        """处理 GET 请求"""
        # 健康检查端点（不需要认证）
        if self.path == '/health':
            self.send_json({
                'status': 'ok',
                'timestamp': datetime.now().isoformat(),
                'service': 'openclaw-monitor-api'
            })
            return
        
        # 其他端点需要认证
        if not self.check_auth():
            self.send_error_json('Unauthorized', 401)
            return
        
        # 路由处理
        if self.path == '/api/health':
            data = self.run_command('openclaw health --json')
            self.send_json(data)
        
        elif self.path == '/api/status':
            data = self.run_command('openclaw status --json')
            self.send_json(data)
        
        elif self.path == '/api/agent/config':
            data = self.run_command('openclaw agent status --json')
            self.send_json(data)
        
        elif self.path == '/api/skills':
            data = self.run_command('openclaw skills list --json')
            self.send_json(data)
        
        elif self.path == '/api/tasks':
            data = self.run_command('openclaw tasks list --json')
            self.send_json(data)
        
        elif self.path.startswith('/api/logs'):
            lines = 30
            if 'lines=' in self.path:
                try:
                    lines = int(self.path.split('lines=')[1].split('&')[0])
                except:
                    pass
            data = self.run_command(f'openclaw logs --json --lines {lines}')
            self.send_json(data)
        
        elif self.path == '/api/sessions':
            data = self.run_command('openclaw sessions list --json')
            self.send_json(data)
        
        elif self.path == '/api/channels':
            data = self.run_command('openclaw channels status --json')
            self.send_json(data)
        
        elif self.path == '/api/models':
            data = self.run_command('openclaw models status --json')
            self.send_json(data)
        
        elif self.path == '/api/rss':
            # RSS 监控数据
            rss_file = '/home/admin/.openclaw/workspace/memory/rss_state.json'
            try:
                with open(rss_file, 'r') as f:
                    data = json.load(f)
                self.send_json({'feeds': data.get('feeds', [])})
            except:
                self.send_json({'feeds': []})
        
        else:
            self.send_error_json('Not Found', 404)
    
    def do_POST(self):
        """处理 POST 请求"""
        if not self.check_auth():
            self.send_error_json('Unauthorized', 401)
            return
        
        # 读取请求体
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode() if content_length > 0 else '{}'
        
        try:
            params = json.loads(body)
        except:
            params = {}
        
        # 路由处理
        if self.path == '/api/sync/stock':
            data = self.run_command('python3 /home/admin/.openclaw/workspace/stock-dashboard/scripts/sync_openclaw_to_json.py')
            self.send_json(data)
        
        elif self.path == '/api/sync/cigar':
            data = self.run_command('python3 /home/admin/.openclaw/workspace/stock-dashboard/scripts/sync_cigar_feishu.py')
            self.send_json(data)
        
        elif self.path == '/api/system/restart':
            data = self.run_command('openclaw gateway restart')
            self.send_json(data)
        
        else:
            self.send_error_json('Not Found', 404)
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[{datetime.now().isoformat()}] {self.address_string()} - {format % args}")

def main():
    port = int(os.getenv('OPENCLAW_MONITOR_PORT', '8765'))
    server = HTTPServer(('0.0.0.0', port), MonitorAPIHandler)
    print(f"🚀 OpenClaw Monitor API 启动在端口 {port}")
    print(f"🔐 API Key: {API_KEY}")
    print(f"📊 健康检查：http://localhost:{port}/health")
    server.serve_forever()

if __name__ == '__main__':
    main()
