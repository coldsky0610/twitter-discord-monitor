import os
import json
import requests
import tweepy
from datetime import datetime
import time
import logging

# 設置日誌記錄
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 從環境變數獲取設定 (用於雲端部署)
TWITTER_BEARER_TOKEN = os.environ.get('TWITTER_BEARER_TOKEN', '')
TWITTER_API_KEY = os.environ.get('TWITTER_API_KEY', '')
TWITTER_API_SECRET = os.environ.get('TWITTER_API_SECRET', '')
TWITTER_ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN', '')
TWITTER_ACCESS_SECRET = os.environ.get('TWITTER_ACCESS_SECRET', '')

# Discord 設定
USERNAME = os.environ.get('TWITTER_USERNAME', '0RIka0_doll')
WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL', '')
DATA_FILE = "last_tweets.json"

# 監控間隔 (分鐘)
CHECK_INTERVAL = int(os.environ.get('CHECK_INTERVAL', '15'))

class CloudTwitterMonitor:
    def __init__(self):
        self.client = None
        self.setup_twitter_client()
    
    def setup_twitter_client(self):
        """設置 Twitter API 客戶端"""
        if not TWITTER_BEARER_TOKEN:
            logger.error("❌ TWITTER_BEARER_TOKEN 環境變數未設置")
            return False
        
        try:
            self.client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
            logger.info("✅ Twitter API 客戶端設置成功")
            return True
        except Exception as e:
            logger.error(f"❌ Twitter API 設置失敗: {e}")
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
            logger.error(f"❌ 獲取用戶 ID 失敗: {e}")
            return None
    
    def fetch_latest_tweets(self, username, limit=5):
        """使用 Twitter API v2 抓取最新推文"""
        if not self.client:
            logger.error("❌ Twitter API 客戶端未設置")
            return []
        
        try:
            user_id = self.get_user_id(username)
            if not user_id:
                logger.error(f"❌ 無法找到用戶: {username}")
                return []
            
            logger.info(f"✅ 找到用戶 ID: {user_id}")
            
            max_results = max(5, min(100, limit))
            
            tweets = self.client.get_users_tweets(
                id=user_id,
                max_results=max_results,
                tweet_fields=['created_at', 'public_metrics'],
                exclude=['retweets', 'replies']
            )
            
            if not tweets.data:
                logger.info("沒有找到推文")
                return []
            
            tweet_list = []
            for tweet in tweets.data[:limit]:
                tweet_list.append({
                    'id': str(tweet.id),
                    'content': tweet.text,
                    'date': tweet.created_at.strftime('%Y-%m-%d %H:%M:%S') if tweet.created_at else datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'url': f"https://x.com/{username}/status/{tweet.id}"
                })
            
            logger.info(f"✅ 成功抓取 {len(tweet_list)} 則推文")
            return tweet_list
            
        except tweepy.TooManyRequests:
            logger.warning("❌ API 速率限制已達上限，等待下次檢查")
            return []
        except tweepy.Unauthorized:
            logger.error("❌ API 認證失敗，請檢查 Token")
            return []
        except Exception as e:
            if "429" in str(e):
                logger.warning("❌ API 速率限制，等待下次檢查")
            else:
                logger.error(f"❌ 抓取推文失敗: {e}")
            return []

def load_last_tweet_ids():
    """載入已發送的推文 ID"""
    try:
        if not os.path.exists(DATA_FILE):
            return set()
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except Exception as e:
        logger.error(f"載入推文 ID 失敗: {e}")
        return set()

def save_last_tweet_ids(ids):
    """保存已發送的推文 ID"""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(list(ids), f, ensure_ascii=False, indent=2)
        logger.info(f"已保存 {len(ids)} 個推文 ID")
    except Exception as e:
        logger.error(f"保存推文 ID 失敗: {e}")

def send_to_discord(content):
    """發送訊息到 Discord"""
    if not WEBHOOK_URL:
        logger.error("❌ Discord Webhook URL 未設置")
        return False
    
    max_length = 1900
    content = str(content).strip()
    
    if not content:
        logger.warning("訊息內容為空，不發送")
        return False
        
    if len(content) > max_length:
        content = content[:max_length] + "..."
        
    data = {"content": content}
    
    try:
        resp = requests.post(WEBHOOK_URL, json=data, timeout=10)
        if resp.status_code in [200, 204]:
            logger.info("✅ 訊息發送成功")
            return True
        else:
            logger.error(f"❌ Discord 錯誤: {resp.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ 發送失敗: {e}")
        return False

def health_check():
    """健康檢查"""
    logger.info("🏥 執行健康檢查...")
    
    checks = {
        'twitter_token': bool(TWITTER_BEARER_TOKEN),
        'discord_webhook': bool(WEBHOOK_URL),
        'username': bool(USERNAME)
    }
    
    for check, status in checks.items():
        if status:
            logger.info(f"✅ {check}: OK")
        else:
            logger.error(f"❌ {check}: FAIL")
    
    return all(checks.values())

def run_monitor():
    """運行監控程式 - 雲端版本"""
    logger.info("🚀 啟動雲端 Twitter 監控程式")
    logger.info(f"監控用戶: @{USERNAME}")
    logger.info(f"檢查間隔: {CHECK_INTERVAL} 分鐘")
    
    if not health_check():
        logger.error("❌ 健康檢查失敗，程式退出")
        return
    
    monitor = CloudTwitterMonitor()
    if not monitor.client:
        logger.error("❌ Twitter API 設置失敗")
        return
    
    consecutive_errors = 0
    max_errors = 5
    
    while True:
        try:
            logger.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔍 檢查新推文...")
            
            # 獲取推文
            tweets = monitor.fetch_latest_tweets(USERNAME, limit=5)
            last_ids = load_last_tweet_ids()
            new_tweets = [t for t in tweets if t['id'] not in last_ids]
            
            if not new_tweets:
                logger.info("沒有新推文")
            else:
                logger.info(f"🎉 發現 {len(new_tweets)} 則新推文！")
                
                for tweet in reversed(new_tweets):
                    msg = f"{tweet['content']}\n{tweet['url']}"
                    logger.info(f"發送推文: {tweet['id']}")
                    
                    if send_to_discord(msg):
                        logger.info("✅ 已發送到 Discord")
                    else:
                        logger.error("❌ 發送失敗")
                
                # 更新已發送的推文 ID
                all_ids = last_ids.union({t['id'] for t in new_tweets})
                save_last_tweet_ids(all_ids)
            
            # 重置錯誤計數
            consecutive_errors = 0
            
            # 等待下次檢查
            sleep_seconds = CHECK_INTERVAL * 60
            logger.info(f"⏱️ 等待 {CHECK_INTERVAL} 分鐘後再次檢查...")
            time.sleep(sleep_seconds)
            
        except KeyboardInterrupt:
            logger.info("⏹️ 收到停止信號，程式退出")
            break
        except Exception as e:
            consecutive_errors += 1
            logger.error(f"❌ 發生錯誤 ({consecutive_errors}/{max_errors}): {e}")
            
            if consecutive_errors >= max_errors:
                logger.error("❌ 連續錯誤次數過多，程式退出")
                break
            
            logger.info("30 秒後重試...")
            time.sleep(30)

if __name__ == "__main__":
    # 檢查是否在本地環境
    if not TWITTER_BEARER_TOKEN or not WEBHOOK_URL:
        print("⚠️ 這是雲端部署版本")
        print("請設置以下環境變數：")
        print("- TWITTER_BEARER_TOKEN")
        print("- DISCORD_WEBHOOK_URL")
        print("- TWITTER_USERNAME (可選)")
        print("- CHECK_INTERVAL (可選，預設 15 分鐘)")
    else:
        run_monitor()
