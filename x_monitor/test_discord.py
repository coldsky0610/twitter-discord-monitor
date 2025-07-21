import os
import json
import requests
from datetime import datetime

# 設定
USERNAME = "Coldsky0610"
WEBHOOK_URL = "https://discordapp.com/api/webhooks/1392678109798731786/9GHjURJtaOU4elxcym1jEE7lxJsfAgLqswupq3C3e8Ne0gP0VM1GsjcLITf2JgfGKGcF"

def send_to_discord(content):
    print(f"準備發送到 Discord: {content}")
    data = {"content": content}
    try:
        resp = requests.post(WEBHOOK_URL, json=data)
        print(f"Discord 回應: {resp.status_code}")
        return resp.status_code in [200, 204]
    except Exception as e:
        print(f"發送失敗: {e}")
        return False

def main():
    print("測試 Discord Webhook...")
    
    # 生成測試推文
    test_tweet = {
        'id': '1234567890',
        'content': f'測試推文 - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # 發送測試訊息
    url = f"https://x.com/{USERNAME}/status/{test_tweet['id']}"
    msg = f"{test_tweet['content']}\n{url}"
    
    success = send_to_discord(msg)
    if success:
        print("✅ 測試成功！Discord Webhook 正常工作")
    else:
        print("❌ 測試失敗！請檢查 Webhook URL")

if __name__ == "__main__":
    main()
