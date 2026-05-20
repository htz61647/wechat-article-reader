#!/bin/bash
# WeChat Article Reader - 发布到 GitHub 完整脚本
# 运行前请确保已安装 gh CLI: brew install gh && gh auth login

set -e

SKILL_DIR="$HOME/.openclaw/skills/wechat-article-reader"
REPO_NAME="wechat-article-reader"

echo "🚀 开始发布 WeChat Article Reader v2.1 到 GitHub..."

cd "$SKILL_DIR"

# Step 1: 检查 gh CLI
if ! command -v gh &> /dev/null; then
    echo "❌ GH CLI not installed!"
    echo "📋 Please install it first:"
    echo "   brew install gh"
    echo "   gh auth login"
    exit 1
fi

# Step 2: 清理备份文件
echo "🧹 清理临时文件..."
rm -f SKILL.md.bak_*

# Step 3: Git 提交更新
git add .
git commit -m "v2.1.0: Final release for public distribution"

# Step 4: 创建仓库并推送
echo "📦 Creating GitHub repository..."

# 获取当前用户名
GITHUB_USER=$(gh whoami 2>/dev/null || echo "HuoZong")

# 确认仓库名
read -p "Enter repository name (default: $REPO_NAME): " REPO_NAME_INPUT
[ -n "$REPO_NAME_INPUT" ] && REPO_NAME="$REPO_NAME_INPUT"

# 选择可见性
read -p "Repository visibility (public/private) [public]: " VISIBILITY
VISIBILITY=${VISIBILITY:-public}

echo "🎯 Creating repository: $GITHUB_USER/$REPO_NAME ($VISIBILITY)"

# 创建远程仓库
gh repo create "$GITHUB_USER/$REPO_NAME" \
  --$VISIBILITY \
  --description "微信公众号文章自动读取 Skill - 四层降级策略" \
  --source=. \
  --remote=origin \
  --push

# Step 5: 设置默认分支
git branch -M main
git push -u origin main

echo ""
echo "✅ Success!"
echo "🔗 Repository: https://github.com/$GITHUB_USER/$REPO_NAME"
echo ""
echo "📝 Next steps:"
echo "1. Visit the repository to verify content"
echo "2. Add collaborators if needed"
echo "3. Enable Issues for community feedback"
echo "4. Consider adding a GitHub Action for CI/CD"
