#!/bin/bash
# WeChat Article Reader - GitHub 仓库初始化脚本
# 运行前请确保已登录 GitHub (gh auth login)

set -e

SKILL_DIR="$HOME/.openclaw/skills/wechat-article-reader"
REPO_NAME="wechat-article-reader"
OWNER="HuoZong"  # 请替换为您的 GitHub 用户名

echo "🚀 Starting GitHub repository setup for WeChat Article Reader v2.1..."

cd "$SKILL_DIR"

# Step 1: 初始化 Git 仓库
if [ ! -d ".git" ]; then
    git init
    echo "✅ Git repository initialized"
else
    echo "ℹ️  Git repository already exists"
fi

# Step 2: 配置 Git
git config user.email "huozong@example.com"
git config user.name "霍天哲"

# Step 3: 添加文件
git add .
git commit -m "v2.1.0: Final release with auto-trigger support and四层降级策略"

# Step 4: 创建远程仓库（请手动替换 OWNER）
# 方法 A: 如果 gh CLI 已安装
if command -v gh &> /dev/null; then
    echo "⚠️  GH CLI detected. Please replace 'HuoZong' with your GitHub username below:"
    read -p "Enter your GitHub username: GITHUB_USERNAME" -r
    
    echo "📦 Creating remote repository..."
    gh repo create "$GITHUB_USERNAME/$REPO_NAME" --public --description "微信公众号文章自动读取 Skill - 四层降级策略" --source=. --remote=origin --push
    
    echo "✅ Repository created at https://github.com/$GITHUB_USERNAME/$REPO_NAME"
    
# 方法 B: 手动创建（推荐新手）
else
    echo "ℹ️  GH CLI not found."
    echo "📋 Please follow these steps manually:"
    echo ""
    echo "1. Go to https://github.com/new"
    echo "2. Repository name: $REPO_NAME"
    echo "3. Description: 微信公众号文章自动读取 Skill - 四层降级策略"
    echo "4. Visibility: Public (recommended for open source)"
    echo "5. Initialize with README: YES"
    echo ""
    echo "6. After creation, run the following commands:"
    echo "   cd $SKILL_DIR"
    echo "   git remote add origin https://github.com/$OWNER/$REPO_NAME.git"
    echo "   git branch -M main"
    echo "   git push -u origin main"
    echo ""
    echo "🔒 Remember to set up .env file separately if needed!"
fi

echo "🎉 Setup complete!"
