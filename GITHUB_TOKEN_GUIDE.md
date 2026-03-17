# GitHub Token 创建详细指南

## 步骤 1：访问 Token 页面
https://github.com/settings/tokens

## 步骤 2：创建 Classic Token

### 点击 "Generate new token"
然后选择 **"Generate new token (classic)"**

⚠️ 注意：不要选 "Generate new token"（新版），要选 **"classic"** 版本！

## 步骤 3：填写信息

- **Note:** `OpenDragon Dashboard`
- **Expiration:** 90 Days（或 No expiration）

## 步骤 4：勾选权限（关键！）

**向下滚动页面**，找到 **Scopes** 部分

### 勾选第一个：✅ repo

勾选 `repo` 后，下面的子选项会自动全选：
- ✅ repo:status
- ✅ repo_deployment
- ✅ public_repo
- ✅ repo:invite
- ✅ security_events

### 如果还是看不到：

**可能是 GitHub 界面更新了**，试试这样：

1. 访问 https://github.com/settings/personal-access-tokens
2. 点击 **Generate new token**
3. 选择 **Classic** 类型
4. 在 **Repository permissions** 部分：
   - 找到 **Contents** → 选择 **Read and write**
   - 或者直接勾选 **Full control**

## 步骤 5：生成并复制

滚动到页面**最底部** → 点击 **Generate token**

**⚠️ 重要：** token 只显示一次！完整复制（以 `ghp_` 开头）

---

## 📸 如果还是找不到

截图发给我，我帮你看看！

或者试试这个直接链接：
https://github.com/settings/tokens/new?scopes=repo&description=OpenDragon

---

**搞定后把 token 发给我！** 🔥
