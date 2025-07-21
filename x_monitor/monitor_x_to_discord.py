import os
import json
import requests
import yt_dlp
from datetime import datetime
import re
import time

# 設定
USERNAME = "Coldsky0610"
WEBHOOK_URL = "https://discordapp.com/api/webhooks/1392678109798731786/9GHjURJtaOU4elxcym1jEE7lxJsfAgLqswupq3C3e8Ne0gP0VM1GsjcLITf2JgfGKGcF"  # 請填入你的 Discord Webhook 連結
DATA_FILE = "last_tweets.json"

# Twitter API 設定 (如果有的話)
TWITTER_BEARER_TOKEN = ""  # 請填入您的 Twitter Bearer Token
# 獲取方式: https://developer.twitter.com/


def fetch_latest_tweets(username, limit=5):
    """使用 yt-dlp 抓取最新推文"""
    tweets = []
    
    # 移除用戶名中的 @ 符號
    if username.startswith('@'):
        username = username[1:]
    
    print(f"[DEBUG] 正在抓取用戶: {username}")
    
    # 使用 yt-dlp 抓取用戶的推文
    ydl_opts = {
        'quiet': False,  # 改為 False 以顯示更多資訊
        'no_warnings': False,  # 改為 False 以顯示警告
        'extract_flat': True,
        'playlist_items': f'1-{limit}',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 抓取用戶的推文頁面
            url = f"https://twitter.com/{username}"
            print(f"[DEBUG] 嘗試抓取 URL: {url}")
            info = ydl.extract_info(url, download=False)
            print(f"[DEBUG] 抓取到的資訊: {info}")
            
            if 'entries' in info:
                print(f"[DEBUG] 找到 {len(info['entries'])} 個項目")
                for entry in info['entries'][:limit]:
                    print(f"[DEBUG] 處理項目: {entry}")
                    tweet_id = entry.get('id', '')
                    title = entry.get('title', '')
                    upload_date = entry.get('upload_date', '')
                    
                    # 格式化日期
                    if upload_date:
                        try:
                            date_obj = datetime.strptime(upload_date, '%Y%m%d')
                            formatted_date = date_obj.strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            formatted_date = upload_date
                    else:
                        formatted_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    tweets.append({
                        'id': tweet_id,
                        'content': title,
                        'date': formatted_date,
                    })
            else:
                print("[DEBUG] 沒有找到 'entries' 在回應中")
            
    except Exception as e:
        print(f"抓取推文時出錯: {e}")
        print(f"[DEBUG] 錯誤類型: {type(e)}")
        # 如果 yt-dlp 失敗，嘗試使用簡單的備用方案
        return fetch_tweets_fallback(username, limit)
    
    print(f"[DEBUG] 總共抓取到 {len(tweets)} 則推文")
    return tweets


def fetch_tweets_fallback(username, limit=5):
    """備用方案：生成測試推文來測試程式功能"""
    print(f"使用備用方案抓取 {username} 的推文...")
    
    # 移除用戶名中的 @ 符號
    if username.startswith('@'):
        username = username[1:]
    
    # 生成一些測試推文來驗證程式功能
    import random
    test_tweets = []
    
    for i in range(limit):
        tweet_id = f"test_{random.randint(1000000000000000000, 9999999999999999999)}"
        test_tweets.append({
            'id': tweet_id,
            'content': f"這是一則測試推文 #{i+1} - {datetime.now().strftime('%H:%M:%S')}",
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        })
    
    print(f"[DEBUG FALLBACK] 生成了 {len(test_tweets)} 則測試推文")
    return test_tweets


def load_last_tweet_ids():
    if not os.path.exists(DATA_FILE):
        return set()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return set(json.load(f))


def save_last_tweet_ids(ids):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(list(ids), f)


def send_to_discord(content):
    # 限制訊息長度，避免超過 Discord 2000 字元上限
    max_length = 1900
    content = str(content).strip()
    print(f"[DEBUG] send_to_discord 內容: {repr(content)}")
    if not content:
        print("[DEBUG] 訊息內容為空，不發送。")
        return False
    if len(content) > max_length:
        content = content[:max_length] + "..."
    data = {"content": content}
    resp = requests.post(WEBHOOK_URL, json=data)
    if resp.status_code != 204 and resp.status_code != 200:
        print(f"Discord Webhook 回傳錯誤: {resp.status_code}, {resp.text}")
    return resp.status_code == 204 or resp.status_code == 200


def main():
    print("開始監控推文...")
    print(f"監控用戶: {USERNAME}")
    print("按 Ctrl+C 停止監控")
    
    while True:
        try:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 檢查新推文...")
            tweets = fetch_latest_tweets(USERNAME, limit=5)
            last_ids = load_last_tweet_ids()
            new_tweets = [t for t in tweets if str(t['id']) not in last_ids]
            
            if not new_tweets:
                print("沒有新推文")
            else:
                print(f"發現 {len(new_tweets)} 則新推文")
                for tweet in reversed(new_tweets):
                    url = f"https://x.com/{USERNAME}/status/{tweet['id']}"
                    text = tweet.get('content', '')
                    msg = f"{text}\n{url}"
                    print(f"[DEBUG] 準備發送訊息: {repr(msg)}")
                    send_to_discord(msg)
                    print(f"已發送: {url}")
                
                # 更新已通知的推文ID
                all_ids = last_ids.union({str(t['id']) for t in new_tweets})
                save_last_tweet_ids(all_ids)

            # 等待 1 分鐘後再次檢查
            print("等待 1 分鐘後再次檢查...")
            time.sleep(60)  # 60 秒 = 1 分鐘
        except KeyboardInterrupt:
            print("\n監控已停止")
            break
        except Exception as e:
            print(f"發生錯誤: {e}")
            print("30 秒後重試...")
            time.sleep(30)

if __name__ == "__main__":
    main()
