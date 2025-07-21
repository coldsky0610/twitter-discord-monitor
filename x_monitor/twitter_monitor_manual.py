import os
import json
import requests
from datetime import datetime
import time

# 設定
USERNAME = "Coldsky0610"
WEBHOOK_URL = "https://discordapp.com/api/webhooks/1392678109798731786/9GHjURJtaOU4elxcym1jEE7lxJsfAgLqswupq3C3e8Ne0gP0VM1GsjcLITf2JgfGKGcF"
DATA_FILE = "last_tweets.json"

def send_to_discord(content):
    """發送訊息到 Discord"""
    max_length = 1900
    content = str(content).strip()
    
    if not content:
        print("[DEBUG] 訊息內容為空，不發送。")
        return False
        
    if len(content) > max_length:
        content = content[:max_length] + "..."
        
    data = {"content": content}
    
    try:
        resp = requests.post(WEBHOOK_URL, json=data)
        if resp.status_code in [200, 204]:
            print("✅ 訊息發送成功")
            return True
        else:
            print(f"❌ Discord 錯誤: {resp.status_code}")
            return False
    except Exception as e:
        print(f"❌ 發送失敗: {e}")
        return False

def manual_add_tweet():
    """手動添加推文進行測試"""
    print("\n=== 手動添加推文測試 ===")
    tweet_id = input("請輸入推文 ID (或按 Enter 使用測試 ID): ").strip()
    
    if not tweet_id:
        tweet_id = f"test_{int(datetime.now().timestamp())}"
    
    content = input("請輸入推文內容 (或按 Enter 使用測試內容): ").strip()
    
    if not content:
        content = f"測試推文內容 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    # 建立推文 URL
    url = f"https://x.com/{USERNAME}/status/{tweet_id}"
    msg = f"{content}\n{url}"
    
    print(f"\n準備發送:")
    print(f"推文 ID: {tweet_id}")
    print(f"內容: {content}")
    print(f"URL: {url}")
    
    confirm = input("\n確認發送? (y/N): ").strip().lower()
    
    if confirm == 'y':
        success = send_to_discord(msg)
        if success:
            print("✅ 推文已發送到 Discord!")
        else:
            print("❌ 發送失敗")
    else:
        print("取消發送")

def test_webhook():
    """測試 Discord Webhook"""
    print("\n=== 測試 Discord Webhook ===")
    test_msg = f"🔔 Webhook 測試訊息 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    print(f"發送測試訊息: {test_msg}")
    success = send_to_discord(test_msg)
    
    if success:
        print("✅ Webhook 正常工作!")
    else:
        print("❌ Webhook 測試失敗，請檢查 URL")

def main_menu():
    """主選單"""
    while True:
        print("\n" + "="*50)
        print("📱 Twitter to Discord 監控程式")
        print("="*50)
        print("1. 測試 Discord Webhook")
        print("2. 手動添加推文")
        print("3. 顯示設定資訊")
        print("4. 退出")
        print("-"*50)
        
        choice = input("請選擇操作 (1-4): ").strip()
        
        if choice == '1':
            test_webhook()
        elif choice == '2':
            manual_add_tweet()
        elif choice == '3':
            show_config()
        elif choice == '4':
            print("程式結束")
            break
        else:
            print("❌ 無效選擇，請重試")

def show_config():
    """顯示設定資訊"""
    print("\n=== 設定資訊 ===")
    print(f"監控用戶: {USERNAME}")
    print(f"Webhook URL: {WEBHOOK_URL[:50]}...")
    print(f"資料檔案: {DATA_FILE}")

if __name__ == "__main__":
    main_menu()
