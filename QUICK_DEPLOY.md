# 🚀 Cloudflare Pages 部署指南 - 5 分钟上线

## 第一步：创建 GitHub 仓库（2 分钟）

### 1.1 登录 GitHub
访问 https://github.com 并登录

### 1.2 创建新仓库
1. 点击右上角 **+** → **New repository**
2. 填写：
   - **Repository name:** `opendragon-dashboard`
   - **Description:** OpenDragon 股票仪表盘
   - **Visibility:** Public 或 Private（随便你）
   - **不要勾选** "Add a README file"
3. 点击 **Create repository**

### 1.3 推送代码
复制页面显示的命令，或者运行：

```bash
cd /home/admin/.openclaw/workspace/stock-dashboard

# 重命名分支为 main
git branch -M main

# 添加远程仓库（替换 YOUR_USERNAME 为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/opendragon-dashboard.git

# 推送
git push -u origin main
```

**✅ 完成！现在你的代码已经在 GitHub 上了！**

---

## 第二步：Cloudflare Pages 部署（3 分钟）

### 2.1 登录 Cloudflare
访问 https://dash.cloudflare.com 并登录

### 2.2 创建 Pages 项目
1. 左侧菜单 → **Workers & Pages**
2. 点击 **Create application**
3. 选择 **Pages** 标签
4. 点击 **Connect to Git**

### 2.3 连接 GitHub
1. 如果第一次使用，会提示授权 GitHub → 点击 **Authorize Cloudflare**
2. 选择刚才创建的 `opendragon-dashboard` 仓库
3. 点击 **Begin setup**

### 2.4 配置项目
填写：
- **Project name:** `opendragon-dashboard`（默认即可）
- **Production branch:** `main`
- **Build command:** (留空，不要填)
- **Build output directory:** `.` (一个点，表示根目录)
- **Environment variables:** (留空)

### 2.5 部署
点击 **Save and Deploy**

Cloudflare 会开始构建，大约 30 秒后完成。

完成后会显示一个 `*.pages.dev` 的预览链接，点击可以访问！

---

## 第三步：绑定自定义域名（1 分钟）

### 3.1 添加域名
1. 在项目页面 → 顶部标签 **Custom domains**
2. 点击 **Add custom domain**
3. 输入：`www.opendragon.icu`
4. 点击 **Add domain**

### 3.2 自动配置 DNS
Cloudflare 会自动添加 DNS 记录，大约 1-2 分钟生效。

如果提示需要手动配置 DNS，请复制显示的 CNAME 记录，然后：
1. 左侧菜单 → **DNS** → **DNS management**
2. 点击 **Add record**
3. 类型：**CNAME**
4. Name: `www`
5. Target: (复制 Cloudflare 给你的地址)
6. Proxy status: **Proxied** (橙色云朵)
7. 点击 **Save**

### 3.3 等待 HTTPS 证书
Cloudflare 会自动申请 HTTPS 证书，大约 5-10 分钟。

---

## ✅ 完成！

访问 https://www.opendragon.icu 即可看到你的股票仪表盘！

---

## 后续更新

以后每次修改代码后：

```bash
cd /home/admin/.openclaw/workspace/stock-dashboard
git add .
git commit -m "更新说明"
git push
```

Cloudflare 会自动重新部署，大约 1 分钟后生效！

---

## 更新数据文件

### 方法 1：直接编辑 JSON
编辑 `data/positions.json`、`data/principles.json`、`data/records.json`，然后 push

### 方法 2：飞书集成（未来）
可以写一个脚本从飞书 Bitable 自动同步数据

---

## 遇到问题？

### 问题 1：DNS 不生效
- 检查域名是否已转移到 Cloudflare
- 等待 5-10 分钟
- 清除浏览器缓存

### 问题 2：页面空白
- 打开浏览器控制台（F12）查看错误
- 检查 CORS 问题（股票 API 可能有限制）

### 问题 3：股票数据不刷新
- 新浪财经 API 在交易日才更新
- 检查浏览器控制台是否有 API 错误

---

**需要帮助？随时问我！** 🚀
