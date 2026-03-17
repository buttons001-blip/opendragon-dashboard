# 🐉 OpenDragon 股票仪表盘

> A 股模拟交易系统 · 利弗摩尔原则实践

## 功能特性

- 📜 利弗摩尔十大原则展示
- 📊 持仓实时行情（新浪财经 API）
- 💰 动态盈亏计算
- 📈 资金概览仪表盘
- 📝 操作记录展示
- 🔄 交易日自动刷新（30 分钟）
- 📱 响应式设计（手机/PC 适配）

## 技术栈

- Vue 3（CDN 引入，无需构建）
- ECharts 5（图表库）
- 新浪财经 API（实时行情）
- Cloudflare Pages（免费托管）

## 部署到 Cloudflare Pages

### 步骤 1：上传到 GitHub

```bash
# 初始化 git 仓库
git init
git add .
git commit -m "Initial commit: OpenDragon 股票仪表盘"

# 推送到 GitHub（替换为你的仓库地址）
git remote add origin https://github.com/YOUR_USERNAME/opendragon-dashboard.git
git branch -M main
git push -u origin main
```

### 步骤 2：Cloudflare Pages 部署

1. 登录 https://dash.cloudflare.com
2. 左侧菜单 → **Workers & Pages** → **Create application**
3. 选择 **Pages** 标签 → **Connect to Git**
4. 选择刚才的仓库
5. 配置：
   - **Project name:** `opendragon-dashboard`
   - **Production branch:** `main`
   - **Build command:** (留空)
   - **Build output directory:** `.` (根目录)
6. 点击 **Save and Deploy**

### 步骤 3：绑定自定义域名

1. 进入项目 → **Custom domains**
2. 点击 **Add custom domain**
3. 输入 `www.opendragon.icu`
4. Cloudflare 会自动配置 DNS 和 HTTPS

**完成！** 🎉

---

## 数据更新

### 手动更新
编辑 `data/` 目录下的 JSON 文件，然后 push 到 GitHub，Cloudflare 会自动重新部署。

### 文件说明
- `data/principles.json` - 十大原则
- `data/positions.json` - 持仓数据
- `data/records.json` - 操作记录

---

## 本地开发

```bash
python3 -m http.server 8888
# 访问 http://localhost:8888
```

---

## 许可证

MIT
