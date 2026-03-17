# 🚀 OpenDragon 股票仪表盘 - 部署指南

## 方案选择

### 方案 A：Cloudflare Pages（推荐 ⭐）
**优点：** 免费、HTTPS 自动、全球 CDN、无需服务器
**缺点：** 需要手动在 Cloudflare 控制台操作

### 方案 B：VPS + Cloudflare Tunnel
**优点：** 完全控制、可运行后端逻辑
**缺点：** 需要维护服务器

---

## 方案 A：Cloudflare Pages 部署（5 分钟搞定）

### 步骤 1：登录 Cloudflare
1. 访问 https://dash.cloudflare.com
2. 登录你的账户
3. 确保 `opendragon.icu` 已添加到 Cloudflare（DNS 已托管）

### 步骤 2：创建 Pages 项目
1. 左侧菜单 → **Workers & Pages** → **Create application**
2. 选择 **Pages** 标签 → **Connect to Git**
3. 选择 GitHub 仓库（或上传 ZIP）

### 步骤 3：配置构建
- **Project name:** `opendragon-dashboard`
- **Production branch:** `main`
- **Build command:** (留空，静态页面无需构建)
- **Build output directory:** `stock-dashboard`

### 步骤 4：部署
点击 **Save and Deploy**，Cloudflare 会自动分配一个 `*.pages.dev` 域名

### 步骤 5：绑定自定义域名
1. 进入项目 → **Custom domains**
2. 点击 **Add custom domain**
3. 输入 `www.opendragon.icu`
4. Cloudflare 会自动配置 DNS 和 HTTPS

**完成！** 访问 https://www.opendragon.icu 即可

---

## 方案 B：VPS 部署（使用 Cloudflare Tunnel）

### 步骤 1：安装 cloudflared
```bash
# 下载
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared

# 验证
cloudflared --version
```

### 步骤 2：登录 Cloudflare
```bash
cloudflared tunnel login
```
会打开浏览器让你授权，完成后返回终端

### 步骤 3：创建 Tunnel
```bash
cloudflared tunnel create opendragon
```
记下返回的 TUNNEL_ID

### 步骤 4：配置 Tunnel
创建配置文件：
```bash
mkdir -p ~/.cloudflared
cat > ~/.cloudflared/config.yml << EOF
tunnel: opendragon
credentials-file: /home/admin/.cloudflared/opendragon.json

ingress:
  - hostname: www.opendragon.icu
    service: http://localhost:8888
  - service: http_status:404
EOF
```

### 步骤 5：路由 DNS
```bash
cloudflared tunnel route dns opendragon www.opendragon.icu
```

### 步骤 6：启动服务
```bash
# 安装 Nginx（可选，用于反向代理）
sudo apt install nginx -y

# 配置 Nginx
sudo cat > /etc/nginx/sites-available/opendragon << 'EOF'
server {
    listen 8888;
    server_name localhost;
    
    root /home/admin/.openclaw/workspace/stock-dashboard;
    index index.html;
    
    location / {
        try_files $uri $uri/ =404;
    }
    
    # 启用 CORS（允许跨域获取股票数据）
    add_header Access-Control-Allow-Origin *;
}
EOF

sudo ln -s /etc/nginx/sites-available/opendragon /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 启动 Cloudflare Tunnel
cloudflared tunnel run opendragon
```

### 步骤 7：设置开机自启（可选）
```bash
sudo cat > /etc/systemd/system/cloudflared.service << EOF
[Unit]
Description=Cloudflare Tunnel
After=network.target

[Service]
Type=simple
User=admin
ExecStart=/usr/local/bin/cloudflared tunnel run opendragon
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
```

---

## 本地测试

访问：http://localhost:8888

---

## 数据更新

### 手动更新持仓
编辑 `data/positions.json`，然后重新部署

### 自动更新（未来扩展）
可以添加一个 Python 后端脚本，定时：
1. 从飞书 Bitable 读取持仓
2. 调用股票 API 获取实时价格
3. 更新数据文件

---

## 功能清单

✅ 利弗摩尔十大原则展示
✅ 持仓实时行情（新浪财经 API）
✅ 动态盈亏计算
✅ 资金概览仪表盘
✅ 操作记录展示
✅ 交易日自动刷新（30 分钟）
✅ 响应式设计（手机/PC 适配）

---

## 下一步优化建议

1. **添加大盘指数** - 上证指数、深证成指、创业板指
2. **K 线图表** - 每只股票的走势 K 线
3. **盈亏趋势图** - 历史收益曲线
4. **预警通知** - 止损/止盈触发时飞书通知
5. **移动端优化** - 更好的手机体验
