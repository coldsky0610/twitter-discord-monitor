import os
import json
import requests
import tweepy
from datetime import datetime
import time

# Twitter API 設定 - 請填入您的 API 金鑰
TWITTER_API_KEY = "7391qUsnANjzCjP5QF4bLhcvK"        # 您的 API Key
TWITTER_API_SECRET = "NeCzAzi10PW2fXkDnN3B3tVtQ6NJYvd5oBeqgbsrkytbCRJ7pj"     # 您的 API Secret Key  
TWITTER_BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAO6q3AEAAAAAvWU%2FwWBb4JcvYJ1GPPFqm2LFmPc%3Da0OmZbbjDPysGjG8rXcR4XPikUntZnPnROamxzwB3XkynAUear"   # 您的 Bearer Token
TWITTER_ACCESS_TOKEN = "1590917119960436739-WI41bgqStWcdTrU1MktocpqN29KxLf"   # 您的 Access Token (如果需要)
TWITTER_ACCESS_SECRET = "DBAt5uNRNMlduTspVjlSXVPw33iuEfiqmrmdbJ9A75RXK"  # 您的 Access Token Secret (如果需要)

# Discord 設定
USERNAME = "0RIka0_doll"
WEBHOOK_URL = "https://discordapp.com/api/webhooks/1392678109798731786/9GHjURJtaOU4elxcym1jEE7lxJsfAgLqswupq3C3e8Ne0gP0VM1GsjcLITf2JgfGKGcF"
DATA_FILE = "last_tweets.json"

class TwitterMonitor:
    def __init__(self):
        self.client = None
        self.setup_twitter_client()
    
    def setup_twitter_client(self):
        """設置 Twitter API 客戶端"""
        if not TWITTER_BEARER_TOKEN:
            print("❌ 請先設置 Twitter Bearer Token")
            return False
        
        try:
            # 使用 Bearer Token 進行認證 (推薦用於只讀操作)
            self.client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
            print("✅ Twitter API 客戶端設置成功")
            return True
        except Exception as e:
            print(f"❌ Twitter API 設置失敗: {e}")
            return False
    
    def get_user_id(self, username):
        """獲取用戶 ID"""
        try:
            if username.startswith('@'):
                username = username[1:]
            
            user = self.client.get_user(username=username)
            if user.data:
                return user.data.id
            return None
        except Exception as e:
            print(f"❌ 獲取用戶 ID 失敗: {e}")
            return None
    
    def fetch_latest_tweets(self, username, limit=5):
        """使用 Twitter API v2 抓取最新推文"""
        if not self.client:
            print("❌ Twitter API 客戶端未設置")
            return []
        
        try:
            # 獲取用戶 ID
            user_id = self.get_user_id(username)
            if not user_id:
                print(f"❌ 無法找到用戶: {username}")
                return []
            
            print(f"✅ 找到用戶 ID: {user_id}")
            
            # 確保 max_results 在有效範圍內 (5-100)
            max_results = max(5, min(100, limit))
            
            # 獲取用戶推文
            tweets = self.client.get_users_tweets(
                id=user_id,
                max_results=max_results,
                tweet_fields=['created_at', 'public_metrics', 'context_annotations'],
                exclude=['retweets', 'replies']  # 排除轉推和回覆
            )
            
            if not tweets.data:
                print("沒有找到推文")
                return []
            
            tweet_list = []
            for tweet in tweets.data[:limit]:  # 只取需要的數量
                tweet_list.append({
                    'id': str(tweet.id),
                    'content': tweet.text,
                    'date': tweet.created_at.strftime('%Y-%m-%d %H:%M:%S') if tweet.created_at else datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'url': f"https://x.com/{username}/status/{tweet.id}"
                })
            
            print(f"✅ 成功抓取 {len(tweet_list)} 則推文")
            return tweet_list
            
        except tweepy.TooManyRequests:
            print("❌ API 速率限制已達上限")
            print("⏱️ 請等待 15 分鐘後再試，或考慮升級 API 方案")
            return []
        except tweepy.Unauthorized:
            print("❌ API 認證失敗，請檢查 Token 是否正確")
            return []
        except Exception as e:
            if "429" in str(e):
                print("❌ API 速率限制已達上限")
                print("⏱️ 請等待 15 分鐘後再試")
                print("💡 建議：將監控間隔設為 15 分鐘以上")
            else:
                print(f"❌ 抓取推文失敗: {e}")
            return []

def load_last_tweet_ids():
    """載入已發送的推文 ID"""
    if not os.path.exists(DATA_FILE):
        return set()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return set(json.load(f))

def save_last_tweet_ids(ids):
    """保存已發送的推文 ID"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(list(ids), f, ensure_ascii=False, indent=2)

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

def test_api_connection():
    """測試 API 連接"""
    print("\n=== 測試 Twitter API 連接 ===")
    
    if not TWITTER_BEARER_TOKEN:
        print("❌ 請先在代碼中設置 TWITTER_BEARER_TOKEN")
        print("\n設置步驟：")
        print("1. 在代碼頂部找到 TWITTER_BEARER_TOKEN = \"\"")
        print("2. 將您的 Bearer Token 填入雙引號中")
        print("3. 保存檔案後重新運行")
        return False
    
    monitor = TwitterMonitor()
    if monitor.client:
        # 測試獲取用戶資訊
        user_id = monitor.get_user_id(USERNAME)
        if user_id:
            print(f"✅ API 連接成功！用戶 {USERNAME} 的 ID: {user_id}")
            return True
        else:
            print("❌ 無法獲取用戶資訊")
            return False
    else:
        print("❌ API 連接失敗")
        return False

def run_monitor():
    """運行監控程式"""
    print("🚀 開始運行 Twitter 監控...")
    
    if not TWITTER_BEARER_TOKEN:
        print("❌ 請先設置 Twitter API Token")
        return
    
    monitor = TwitterMonitor()
    if not monitor.client:
        print("❌ Twitter API 設置失敗")
        return
    
    print(f"監控用戶: @{USERNAME}")
    print("按 Ctrl+C 停止監控\n")
    
    while True:
        try:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 檢查新推文...")
            
            # 獲取推文
            tweets = monitor.fetch_latest_tweets(USERNAME, limit=5)
            last_ids = load_last_tweet_ids()
            new_tweets = [t for t in tweets if t['id'] not in last_ids]
            
            if not new_tweets:
                print("沒有新推文")
            else:
                print(f"🎉 發現 {len(new_tweets)} 則新推文！")
                
                for tweet in reversed(new_tweets):  # 按時間順序發送
                    msg = f"{tweet['content']}\n{tweet['url']}"
                    print(f"\n發送推文: {tweet['id']}")
                    
                    if send_to_discord(msg):
                        print("✅ 已發送到 Discord")
                    else:
                        print("❌ 發送失敗")
                
                # 更新已發送的推文 ID
                all_ids = last_ids.union({t['id'] for t in new_tweets})
                save_last_tweet_ids(all_ids)
            
            print("⏱️ 等待 15 分鐘後再次檢查...")
            time.sleep(900)  # 15 分鐘 = 900 秒
            
        except KeyboardInterrupt:
            print("\n⏹️ 監控已停止")
            break
        except Exception as e:
            print(f"❌ 發生錯誤: {e}")
            print("30 秒後重試...")
            time.sleep(30)

def main_menu():
    """主選單"""
    while True:
        print("\n" + "="*60)
        print("🐦 Twitter API 監控程式")
        print("="*60)
        print("1. 測試 Twitter API 連接")
        print("2. 測試 Discord Webhook") 
        print("3. 手動獲取推文測試")
        print("4. 開始自動監控")
        print("5. 顯示設定說明")
        print("6. 退出")
        print("-"*60)
        
        choice = input("請選擇操作 (1-6): ").strip()
        
        if choice == '1':
            test_api_connection()
        elif choice == '2':
            test_discord()
        elif choice == '3':
            manual_test()
        elif choice == '4':
            run_monitor()
        elif choice == '5':
            show_setup_guide()
        elif choice == '6':
            print("程式結束")
            break
        else:
            print("❌ 無效選擇，請重試")

def test_discord():
    """測試 Discord Webhook"""
    print("\n=== 測試 Discord Webhook ===")
    test_msg = f"🔔 Webhook 測試 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    if send_to_discord(test_msg):
        print("✅ Discord Webhook 正常工作!")
    else:
        print("❌ Discord Webhook 測試失敗")

def manual_test():
    """手動測試獲取推文"""
    print("\n=== 手動獲取推文測試 ===")
    
    if not TWITTER_BEARER_TOKEN:
        print("❌ 請先設置 Twitter Bearer Token")
        return
    
    monitor = TwitterMonitor()
    if not monitor.client:
        return
    
    tweets = monitor.fetch_latest_tweets(USERNAME, limit=5)  # 改為 5，符合 API 要求
    
    if tweets:
        print(f"\n📋 最新 {len(tweets)} 則推文:")
        for i, tweet in enumerate(tweets, 1):
            print(f"\n{i}. 推文 ID: {tweet['id']}")
            print(f"   時間: {tweet['date']}")
            print(f"   內容: {tweet['content'][:100]}...")
            print(f"   網址: {tweet['url']}")
    else:
        print("沒有獲取到推文")

def show_setup_guide():
    """顯示設置說明"""
    print("\n" + "="*60)
    print("📋 Twitter API 設置說明")
    print("="*60)
    print("""
1. 申請 Twitter Developer 帳戶:
   https://developer.twitter.com/

2. 創建新的 App 並獲取以下資訊:
   - Bearer Token (必須)
   - API Key (選用)
   - API Secret (選用)

3. 在代碼中設置 Token:
   找到代碼頂部的:
   TWITTER_BEARER_TOKEN = ""
   
   將您的 Bearer Token 填入雙引號中:
   TWITTER_BEARER_TOKEN = "your_token_here"

4. 保存檔案並重新運行程式

5. 使用選項 1 測試 API 連接是否成功
""")
    print("="*60)

if __name__ == "__main__":
    main_menu()
