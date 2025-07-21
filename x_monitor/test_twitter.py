import yt_dlp
import requests

def test_ytdlp():
    print("測試 yt-dlp 抓取 Twitter...")
    username = "Coldsky0610"
    
    ydl_opts = {
        'quiet': False,
        'no_warnings': False,
        'extract_flat': True,
        'playlist_items': '1-3',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            url = f"https://twitter.com/{username}"
            print(f"抓取 URL: {url}")
            info = ydl.extract_info(url, download=False)
            print(f"結果: {info}")
            
    except Exception as e:
        print(f"yt-dlp 錯誤: {e}")

def test_requests():
    print("\n測試 requests 抓取 Twitter...")
    username = "Coldsky0610"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        url = f"https://twitter.com/{username}"
        print(f"抓取 URL: {url}")
        
        response = requests.get(url, headers=headers, timeout=10)
        print(f"狀態碼: {response.status_code}")
        print(f"回應長度: {len(response.text)} 字元")
        
        if "twitter" in response.text.lower():
            print("頁面包含 Twitter 內容")
        else:
            print("頁面不包含 Twitter 內容")
            
    except Exception as e:
        print(f"requests 錯誤: {e}")

if __name__ == "__main__":
    test_ytdlp()
    test_requests()
