# Twitter 監控雲端部署指南

## 🌐 免費雲端平台選擇

### 1. **Heroku (推薦新手)**
- 免費額度：每月 550-1000 小時
- 優點：部署簡單，支援 Python
- 缺點：免費版會休眠

### 2. **Railway**
- 免費額度：每月 $5 額度
- 優點：不會休眠，部署簡單
- 支援：Python, 自動部署

### 3. **Render**
- 免費額度：每月 750 小時
- 優點：不會休眠，現代化介面
- 支援：Python, 自動部署

### 4. **Google Cloud Platform (GCP)**
- 免費額度：每月 $300 試用額度
- 優點：強大功能，不會休眠
- 適合：進階用戶

### 5. **Amazon Web Services (AWS)**
- 免費額度：EC2 t2.micro 免費一年
- 優點：業界標準，功能完整
- 適合：進階用戶

## 🚀 **推薦方案：Railway 部署**

Railway 是最適合初學者的平台，不會休眠且部署簡單。

### 部署步驟：

1. **準備代碼**
   - 將程式上傳到 GitHub
   - 添加 requirements.txt
   - 添加 Procfile

2. **連接 Railway**
   - 前往 railway.app
   - 使用 GitHub 登入
   - 連接您的專案

3. **設定環境變數**
   - 設定 Twitter API 金鑰
   - 設定 Discord Webhook URL

4. **部署並運行**
   - 自動部署
   - 24/7 運行

## 💰 **成本估算**

### Railway (推薦)
- 免費額度：$5/月
- 小型程式：通常在免費額度內
- 付費：$5/月起

### Heroku
- 免費版：有限制
- Hobby：$7/月 (24/7 運行)

### 其他選擇
- VPS (Vultr/DigitalOcean)：$5-10/月
- 樹莓派：一次性購買約 $100
