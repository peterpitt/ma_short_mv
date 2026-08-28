# YouTube 一鍵發布設定指南

本專案提供一個 GitHub Actions 工作流，讓您可以從 GitHub Actions 的 **Run workflow** 按鈕手動觸發影片上傳。工作流不會在沒有授權的情況下自動公開影片；預設可見性是 `unlisted`，您可以在觸發時選擇 `public`、`unlisted` 或 `private`。

## 工作流支援的輸入

| 欄位 | 說明 |
|---|---|
| `video_file` | 已提交到此倉庫的 MP4 相對路徑；與 `video_url` 二選一 |
| `video_url` | 可由 GitHub Actions 取得的 HTTPS MP4 URL；與 `video_file` 二選一 |
| `title` | YouTube 標題，必填 |
| `description` | YouTube 說明欄，可選 |
| `tags` | 逗號分隔的標籤或 hashtag，可選 |
| `playlist_id` | 可選的 YouTube 播放清單 ID |
| `privacy_status` | `public`、`unlisted` 或 `private`，預設為 `unlisted` |

> `video_url` 必須是可由 GitHub runner 直接下載的 HTTPS URL。若影片只存在於本機，請使用 `video_file`，或先把影片放到您信任的儲存服務。

## 一次性設定 OAuth

### 1. 建立 Google Cloud 專案

前往 [Google Cloud Console](https://console.cloud.google.com/)，建立或選擇一個專案，啟用 **YouTube Data API v3**，並設定 OAuth consent screen。若應用程式仍在測試狀態，請將自己的 Google 帳號加入 Test users。

### 2. 建立 OAuth Client

建立 OAuth 2.0 Client ID，類型選擇 **Desktop app**，下載 JSON 檔並保存為本機的 `client_secret.json`。此檔案只用於本機授權，**不要提交到 Git**。

### 3. 在本機取得 refresh token

先安裝依賴：

```bash
python3 -m pip install --upgrade google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

第一次執行會開啟瀏覽器，請用要發布影片的 YouTube 頻道所屬 Google 帳號授權：

```bash
python animated-shorts-generator/scripts/upload_to_youtube.py \
  --client-secret client_secret.json \
  --token .youtube-token.json \
  --print-refresh-token
```

將終端機輸出的 refresh token 複製到 GitHub Repository 的 **Settings → Secrets and variables → Actions**。不要把 token 貼在 issue、commit、workflow log 或聊天訊息中。

### 4. 建立 GitHub Actions Secrets

建立下列三個 Repository secrets：

| Secret | 值 |
|---|---|
| `YOUTUBE_CLIENT_ID` | OAuth Client JSON 中的 `client_id` |
| `YOUTUBE_CLIENT_SECRET` | OAuth Client JSON 中的 `client_secret` |
| `YOUTUBE_REFRESH_TOKEN` | 上一步產生的 refresh token |

CI 使用 refresh token 進行非互動式授權，因此工作流**不會**嘗試在 runner 上開啟瀏覽器，也不會把 token 寫回倉庫。

## 一鍵發布操作

1. 將 MP4 提交至倉庫，例如 `output/panda_final.mp4`；或準備一個可由 runner 下載的 HTTPS MP4 URL。
2. 開啟倉庫的 **Actions** 分頁。
3. 選擇 **Publish to YouTube**。
4. 點選 **Run workflow**。
5. 填入 `video_file` 或 `video_url`、標題、說明、標籤與可見性。
6. 按下 **Run workflow**，在工作流完成後於 Summary 查看實際 YouTube 影片網址。

為避免誤公開，建議第一次使用 `unlisted` 驗證標題、說明、影片尺寸與頻道是否正確；確認無誤後再選 `public`。

## 本機上傳

本機可直接使用同一支腳本：

```bash
python animated-shorts-generator/scripts/upload_to_youtube.py \
  output/panda_final.mp4 \
  "Q版貓熊竹林嬉戲：大口吃竹子超可愛！" \
  --description "許多可愛的貓熊在竹林裡嬉戲，大口吃竹子。" \
  --tags "shorts,panda,cute,animation,chibi" \
  --privacy unlisted
```

本機第一次執行會使用瀏覽器完成授權，之後會把快取 token 寫入 `.youtube-token.json`。該檔案同樣不得提交到倉庫。

## 常見問題

### 工作流顯示缺少 Secrets

確認三個 Secrets 的名稱完全一致，並確認 workflow 是在同一個 Repository 執行。Secrets 的實際值不會顯示在 workflow log 中。

### `invalid_grant` 或 refresh token 失效

重新在本機執行 `--print-refresh-token` 完成授權，再更新 `YOUTUBE_REFRESH_TOKEN`。如果 OAuth consent screen 仍在測試狀態，請確認授權帳號仍列在 Test users 中。

### `quotaExceeded`

YouTube Data API 受 Google Cloud quota 限制。請查看 Google Cloud Console 的 API quota 與使用量，不要透過重試迴圈反覆提交同一個影片。

### 上傳後網址

成功上傳後，影片網址會由 API 回傳的真實 `video_id` 組成：

```text
https://www.youtube.com/watch?v=VIDEO_ID
```

它與頻道主頁 `https://www.youtube.com/@asusu-w3l` 不同；影片公開後才會在頻道內容中顯示。

## 安全注意事項

請立即撤銷任何曾經貼在聊天、issue、commit 或 log 中的 GitHub PAT，並以新的最小權限 token 重新設定 Git 認證。OAuth client secret 與 YouTube refresh token 也只能放在 GitHub Secrets 或本機受保護的檔案中。
