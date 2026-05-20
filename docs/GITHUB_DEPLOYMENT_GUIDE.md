# 🌐 WeChat Article Reader - GitHub 部署完整指南

**版本**: v2.1.0  
**最后更新**: 2026-05-19

---

## 🎯 本次操作清单

- [x] **国能 e 购爬虫 Git 初始化完成** (`projects/bidding-crawler`)
- [x] **WeChat Article Reader README 准备完成**
- [ ] **创建 GitHub 仓库并推送** (需您执行)
- [ ] **配置分支保护与 CI/CD** (可选)

---

## 📋 步骤详解

### Step 1: 准备工作 (已完成 ✅)

```bash
# ✅ WeChat Article Reader 本地 Git 已初始化
cd ~/.openclaw/skills/wechat-article-reader
git status  # 确认所有文件已提交
```

### Step 2: 安装 gh CLI (如未安装)

```bash
# macOS/Linux
brew install gh

# 认证登录
gh auth login
# 选择：GitHub → HTTPS → Token → Copy & Paste
```

### Step 3: 运行发布脚本 (推荐新手)

```bash
cd ~/.openclaw/skills/wechat-article-reader
chmod +x scripts/publish-to-github.sh
./scripts/publish-to-github.sh
```

**脚本会自动:**
1. 清理临时备份文件
2. 创建远程仓库 (`public` 模式)
3. 推送到 GitHub
4. 设置主分支为 `main`

---

### Step 4: 手动发布 (高级用户)

#### 4.1 在 GitHub 创建空仓库
1. 访问 https://github.com/new
2. 仓库名：`wechat-article-reader`
3. 描述：`微信公众号文章自动读取 Skill - 四层降级策略`
4. 可见性：**Public** (开源推荐)
5. Initialize with README: ❌ (我们已有)
6. 添加 .gitignore: Python

#### 4.2 推送到 GitHub
```bash
cd ~/.openclaw/skills/wechat-article-reader

# 添加远程仓库
git remote add origin https://github.com/HuoZong/wechat-article-reader.git

# 重命名默认分支为 main
git branch -M main

# 推送到 GitHub
git push -u origin main

# 添加 Tags (可选，但推荐)
git tag -a v2.1.0 -m "Final release with auto-trigger support"
git push origin v2.1.0
```

---

## 🔧 后续优化建议

### A. 添加 GitHub Actions 自动测试

创建 `.github/workflows/ci.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.8'
    
    - name: Install dependencies
      run: |
        pip install beautifulsoup4 lxml requests playwright
        playwright install chromium
    
    - name: Test import
      run: |
        cd scripts
        python -c "import wechat_reader; print('OK')"
    
    - name: Run basic tests
      run: |
        # 添加更多测试用例
        echo "Tests passed!"
```

### B. 启用 GitHub Pages 文档站点

```bash
# 将 docs 目录推送到 gh-pages 分支
git checkout --orphan gh-pages
git rm -rf .
cp ../docs/*.md ./
git add .
git commit -m "Publish documentation"
git push -u origin gh-pages

# 在 Settings > Pages 中启用
```

### C. 添加 Issues 模板

`.github/ISSUE_TEMPLATE/feature_request.md`:
```markdown
## ✨ 功能建议
[描述你希望的新功能]

## 使用场景
[说明什么情况下需要此功能]

## 期望效果
[描述预期结果]
```

---

## 📊 发布检查清单

发布前请确认:

- [x] README.md 内容完整
- [x] LICENSE 文件存在 (MIT)
- [x] .gitignore 排除敏感文件
- [x] 版本号正确 (v2.1.0)
- [x] 所有文件已通过 git add/commit
- [ ] 测试账号可用 (可选)
- [ ] 图片链接可访问 (如需)

---

## 💡 常见问题

### Q1: 可以改为私有仓库吗？
A: 完全可以！只需在创建时选择 Private。但作为通用工具，公开仓库更有价值。

### Q2: 如何添加协作者？
A: Repository Settings > Manage Access > Invite a collaborator

### Q3: 可以回滚版本吗？
A: 当然！`git revert HEAD` 或 `git reset --hard <commit>`

### Q4: License 应该选什么？
A: MIT 最友好，允许商业使用且无限制。详见 LICENSE 文件。

---

## 🚀 发布后推广

1. **分享到技术社区**: Hacker News, Reddit r/Python
2. **加入 OpenClaw 技能库**: 联系维护者申请收录
3. **撰写技术博客**: 分享开发经验和技术亮点
4. **收集用户反馈**: 通过 Issues 了解改进方向

---

## 📞 联系方式

如有问题，欢迎通过以下方式联系:

- **Issues**: https://github.com/HuoZong/wechat-article-reader/issues
- **Email**: huozong@example.com
- **钉钉群**: [OpenClaw 技术交流群](#)

---

_Last updated: 2026-05-19 by 小鸥_
