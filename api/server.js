/**
 * OpenClaw 管理 API
 * 运行: node server.js
 * 端口: 3456
 */

const express = require('express');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const https = require('https');
const http = require('http');

const app = express();
const PORT = process.env.PORT || 3456;

// 配置
const CONFIG = {
    workspace: '/home/admin/.openclaw/workspace',
    skillsDir: '/home/admin/.openclaw/workspace/skills',
    agentsDir: '/home/admin/.openclaw/agents',
    cronDir: '/home/admin/.openclaw/cron',
    logFile: '/home/admin/.openclaw/logs/app.log',
    apiKey: process.env.API_KEY || 'opendragon-admin-2026'
};

// 中间件
app.use(express.json());
app.use(express.static('../cloudflare-pages'));

// CORS 配置
const corsOptions = {
    origin: ['https://opendragon.icu', 'http://localhost:3000', 'http://localhost:3456'],
    methods: ['GET', 'POST', 'PUT', 'DELETE'],
    allowedHeaders: ['Content-Type', 'x-api-key']
};
app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', req.headers.origin || '*');
    res.header('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS');
    res.header('Access-Control-Allow-Headers', 'Content-Type, x-api-key');
    if (req.method === 'OPTIONS') {
        return res.sendStatus(200);
    }
    next();
});

// API 认证中间件
const authenticate = (req, res, next) => {
    const key = req.headers['x-api-key'] || req.query.apiKey;
    if (key !== CONFIG.apiKey) {
        return res.status(401).json({ error: 'Unauthorized' });
    }
    next();
};

// ============ 任务1: Agent 配置读取 ============
app.get('/api/agent/config', (req, res) => {
    try {
        const config = {};
        const files = {
            SOUL: 'SOUL.md',
            USER: 'USER.md',
            IDENTITY: 'IDENTITY.md',
            MEMORY: 'MEMORY.md',
            AGENTS: 'AGENTS.md',
            TOOLS: 'TOOLS.md'
        };
        
        for (const [key, filename] of Object.entries(files)) {
            const filepath = path.join(CONFIG.workspace, filename);
            if (fs.existsSync(filepath)) {
                config[key.toLowerCase()] = fs.readFileSync(filepath, 'utf-8').substring(0, 500);
            }
        }
        
        // 读取 agents 目录下的 agent 列表
        const agents = fs.readdirSync(CONFIG.agentsDir).filter(f => {
            return fs.statSync(path.join(CONFIG.agentsDir, f)).isDirectory();
        });
        
        res.json({
            success: true,
            data: {
                files: config,
                agents: agents.map(name => ({
                    name,
                    path: path.join(CONFIG.agentsDir, name)
                }))
            }
        });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// ============ 任务2: 技能列表读取 ============
app.get('/api/skills', (req, res) => {
    try {
        const skills = [];
        
        // 扫描工作空间的 skills 目录
        if (fs.existsSync(CONFIG.skillsDir)) {
            const entries = fs.readdirSync(CONFIG.skillsDir, { withFileTypes: true });
            for (const entry of entries) {
                if (entry.isDirectory() || entry.isSymbolicLink()) {
                    const skillPath = path.join(CONFIG.skillsDir, entry.name);
                    const skillMdPath = path.join(skillPath, 'SKILL.md');
                    
                    let description = '技能描述未知';
                    let status = 'active';
                    
                    if (fs.existsSync(skillMdPath)) {
                        const content = fs.readFileSync(skillMdPath, 'utf-8');
                        const descMatch = content.match(/description["']?\s*[:：]\s*["']?([^"\n]+)/i);
                        if (descMatch) description = descMatch[1].trim();
                    }
                    
                    // 检查是否为符号链接
                    const isLink = fs.lstatSync(skillPath).isSymbolicLink();
                    
                    skills.push({
                        name: entry.name,
                        description: description,
                        status: isLink ? 'linked' : 'local',
                        path: skillPath
                    });
                }
            }
        }
        
        res.json({
            success: true,
            data: {
                count: skills.length,
                skills: skills
            }
        });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// ============ 任务3: 定时任务状态 ============
app.get('/api/tasks', (req, res) => {
    try {
        const tasks = [];
        
        // 读取 cron 目录
        if (fs.existsSync(CONFIG.cronDir)) {
            const entries = fs.readdirSync(CONFIG.cronDir);
            for (const entry of entries) {
                if (entry.endsWith('.json')) {
                    const taskPath = path.join(CONFIG.cronDir, entry);
                    const content = JSON.parse(fs.readFileSync(taskPath, 'utf-8'));
                    tasks.push({
                        name: entry.replace('.json', ''),
                        schedule: content.schedule || 'unknown',
                        enabled: content.enabled !== false,
                        lastRun: content.lastRun || null,
                        nextRun: content.nextRun || null
                    });
                }
            }
        }
        
        // 如果没有 cron 文件，读取 cron_tasks.md
        const cronMdPath = path.join(CONFIG.workspace, 'cron_tasks.md');
        if (tasks.length === 0 && fs.existsSync(cronMdPath)) {
            const content = fs.readFileSync(cronMdPath, 'utf-8');
            const lines = content.split('\n');
            for (const line of lines) {
                if (line.includes('|') && !line.startsWith('|')) {
                    const parts = line.split('|').filter(p => p.trim());
                    if (parts.length >= 3) {
                        tasks.push({
                            name: parts[1].trim(),
                            time: parts[0].trim(),
                            status: parts[2].trim(),
                            enabled: parts[2].includes('✅')
                        });
                    }
                }
            }
        }
        
        res.json({
            success: true,
            data: {
                count: tasks.length,
                tasks: tasks
            }
        });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// ============ 任务4: 系统健康检查 ============
app.get('/api/health', async (req, res) => {
    const services = {
        feishu: { name: '飞书', url: 'https://open.feishu.cn' },
        github: { name: 'GitHub', url: 'https://api.github.com' },
        cloudflare: { name: 'Cloudflare', url: 'https://cloudflare.com' },
        tencent: { name: '腾讯财经', url: 'https://finance.sina.com.cn' }
    };
    
    const results = {};
    
    for (const [key, svc] of Object.entries(services)) {
        const start = Date.now();
        try {
            await checkUrl(svc.url);
            results[key] = {
                name: svc.name,
                status: 'online',
                latency: Date.now() - start + 'ms'
            };
        } catch (error) {
            results[key] = {
                name: svc.name,
                status: 'offline',
                error: error.message
            };
        }
    }
    
    // 检查 OpenClaw 网关
    try {
        exec('pgrep -f "openclaw gateway"', (err, stdout) => {
            results.openclaw = {
                name: 'OpenClaw 网关',
                status: stdout ? 'running' : 'stopped'
            };
            
            res.json({
                success: true,
                data: {
                    timestamp: new Date().toISOString(),
                    services: results
                }
            });
        });
    } catch (error) {
        results.openclaw = {
            name: 'OpenClaw 网关',
            status: 'unknown'
        };
        res.json({ success: true, data: { timestamp: new Date().toISOString(), services: results } });
    }
});

function checkUrl(url) {
    return new Promise((resolve, reject) => {
        const protocol = url.startsWith('https') ? https : http;
        const req = protocol.get(url, { timeout: 5000 }, (res) => {
            resolve(res.statusCode);
        });
        req.on('error', reject);
        req.on('timeout', () => reject(new Error('Timeout')));
    });
}

// ============ 任务5: 日志读取 ============
app.get('/api/logs', (req, res) => {
    try {
        const lines = parseInt(req.query.lines) || 50;
        
        // 尝试多个日志位置
        const logPaths = [
            CONFIG.logFile,
            '/home/admin/.openclaw/logs/gateway.log',
            '/home/admin/.openclaw/workspace/cron.log',
            '/home/admin/.openclaw/workspace/stock-dashboard/data/sync.log'
        ];
        
        let logContent = '';
        for (const logPath of logPaths) {
            if (fs.existsSync(logPath)) {
                logContent = fs.readFileSync(logPath, 'utf-8');
                break;
            }
        }
        
        if (!logContent) {
            return res.json({ success: true, data: { lines: [], source: 'none' } });
        }
        
        const allLines = logContent.split('\n').filter(l => l.trim());
        const recentLines = allLines.slice(-lines);
        
        res.json({
            success: true,
            data: {
                count: recentLines.length,
                lines: recentLines,
                source: logPaths.find(p => fs.existsSync(p)) || 'none'
            }
        });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// ============ 任务6: 远程控制接口 ============

// 重启网关
app.post('/api/system/restart', authenticate, (req, res) => {
    // 方法1: 尝试 openclaw 命令
    exec('openclaw gateway restart 2>&1', (error, stdout, stderr) => {
        if (!error) {
            return res.json({ 
                success: true, 
                method: 'openclaw command',
                message: '网关重启命令已发送', 
                output: stdout || stderr 
            });
        }
        
        // 方法2: 直接 kill 进程（备选）
        exec('pkill -f "openclaw gateway" && sleep 2 && nohup openclaw gateway --port 18789 > /dev/null 2>&1 &', (err2, out2, err3) => {
            if (!err2) {
                return res.json({ 
                    success: true, 
                    method: 'direct process restart',
                    message: '网关已重启', 
                    output: out2 
                });
            }
            res.json({ success: false, error: '重启失败', details: error.message });
        });
    });
});

// 同步股票数据
app.post('/api/sync/stock', authenticate, (req, res) => {
    const script = '/home/admin/.openclaw/workspace/stock-dashboard/scripts/sync_feishu_to_json_v2.py';
    if (!fs.existsSync(script)) {
        return res.status(404).json({ success: false, error: '同步脚本不存在' });
    }
    
    // 后台执行，不阻塞响应
    res.json({ success: true, message: '开始同步股票数据...' });
    
    exec(`python3 ${script} >> /home/admin/.openclaw/workspace/stock-dashboard/data/sync.log 2>&1`, 
        { cwd: path.dirname(script) }, 
        (error, stdout, stderr) => {
            console.log(`[SYNC STOCK] ${error ? 'ERROR: ' + error.message : 'SUCCESS'}`);
        }
    );
});

// 同步雪茄数据
app.post('/api/sync/cigar', authenticate, (req, res) => {
    const script = '/home/admin/.openclaw/workspace/stock-dashboard/scripts/update_missing_logos.py';
    if (!fs.existsSync(script)) {
        return res.status(404).json({ success: false, error: '同步脚本不存在' });
    }
    
    // 后台执行
    res.json({ success: true, message: '开始同步雪茄数据...' });
    
    exec(`python3 ${script} >> /home/admin/.openclaw/workspace/cron.log 2>&1`, 
        { cwd: path.dirname(script) }, 
        (error, stdout, stderr) => {
            console.log(`[SYNC CIGAR] ${error ? 'ERROR: ' + error.message : 'SUCCESS'}`);
        }
    );
});

// ============ 启动服务器 ============
app.listen(PORT, '0.0.0.0', () => {
    console.log(`OpenClaw API Server running on port ${PORT}`);
    console.log(`API Key: ${CONFIG.apiKey}`);
});

// SSE for real-time logs
app.get('/api/logs/stream', (req, res) => {
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    
    const logPath = CONFIG.logFile;
    if (!fs.existsSync(logPath)) {
        res.write('data: {"error": "Log file not found"}\n\n');
        res.end();
        return;
    }
    
    let lastSize = fs.statSync(logPath).size;
    
    const interval = setInterval(() => {
        try {
            const stats = fs.statSync(logPath);
            if (stats.size > lastSize) {
                const stream = fs.createReadStream(logPath, { start: lastSize });
                stream.on('data', (chunk) => {
                    res.write(`data: ${JSON.stringify({ log: chunk.toString() })}\n\n`);
                });
                lastSize = stats.size;
            }
        } catch (e) {
            clearInterval(interval);
            res.end();
        }
    }, 2000);
    
    req.on('close', () => clearInterval(interval));
});

module.exports = app;