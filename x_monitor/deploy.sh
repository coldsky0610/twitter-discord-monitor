#!/bin/bash

# Railway 部署腳本
echo "🚀 準備部署到 Railway..."

# 1. 檢查必要檔案
echo "📋 檢查必要檔案..."
files=("cloud_monitor.py" "requirements.txt" "Procfile")
for file in "${files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ 缺少檔案: $file"
        exit 1
    else
        echo "✅ 找到檔案: $file"
    fi
done

# 2. 初始化 Git (如果還沒有)
if [ ! -d ".git" ]; then
    echo "📁 初始化 Git 倉庫..."
    git init
    git add .
    git commit -m "Initial commit for Railway deployment"
fi

# 3. 設置環境變數提醒
echo ""
echo "📝 部署後請在 Railway 設置以下環境變數："
echo "TWITTER_BEARER_TOKEN=你的Twitter Bearer Token"
echo "DISCORD_WEBHOOK_URL=你的Discord Webhook URL"
echo "TWITTER_USERNAME=監控的用戶名 (例如: 0RIka0_doll)"
echo "CHECK_INTERVAL=檢查間隔分鐘數 (預設: 15)"
echo ""
echo "🌐 前往 railway.app 完成部署"
