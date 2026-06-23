# 🍎 個人教學網站 (Apple Style Portfolio & Lessons)

這是一個為老師/教學者量身打造的個人教學網站專案。整體視覺設計借鑑了 **Apple 官網** 的簡約美學（如毛玻璃效果導覽列、圓角卡片與陰影、高質感排版），並且提供「寫筆記就能自動建置網站」的自動化流程。

---

## 📂 專案目錄結構說明

網站的內容（文字與資料）與前端的程式碼是分開的，您可以透過修改以下資料夾中的 **Markdown (.md)** 檔案來管理您的網站：

* `about/`：放您的個人介紹與學經歷。編輯裡面的 `profile.md`。
* `projects/`：放您以前設計的網頁作品或專案。在裡面新增 Markdown 檔即會自動生成作品卡片。
* `lessons/`：放您的教學紀錄與文章。在裡面新增 Markdown 檔即會自動生成文章頁面與首頁列表。
* `resources/`：放您推薦給學生的學習資源與工具。
* `student_works/`：放您的學生優秀作品展示與課後評價。
* `assets/`：靜態資源（CSS、字體、圖片等）。請把您的照片、作品截圖等放進 `assets/images/` 資料夾。

---

## 🚀 如何新增教學文章與內容（方案 A）

本專案採用 **Markdown 格式**，編輯就像寫一般筆記一樣簡單。

### 步驟 1：在 `lessons/` 下新增檔案
檔案名稱建議為「日期-標題.md」（例如 `2026-06-21-canva-tips.md`）。

### 步驟 2：在檔案最上方加入 YAML 設定（Front Matter）
每篇 Markdown 檔案最頂端，都必須用三個減號 `---` 包住這篇文章的元數據（Meta-data）。
例如：
```yaml
---
title: "Canva 製作精美網頁的 5 個視覺心法"
date: "2026-06-21"
category: "網頁設計"
tags: ["Canva", "配色", "美學"]
summary: "本篇文章介紹如何用 Canva 規劃出具有現代感的網頁排版，並學會和諧的配色心法。"
---

# 這裡開始是文章標題（h1）
您可以在這裡使用一般的 Markdown 語法撰寫內容：
* 這是清單
* 這是**粗體**
> 這是引言
```

---

## 🛠️ 如何編譯並生成網站

每次您新增或修改了 Markdown 檔案後，請執行自動化建置腳本，它會自動將 Markdown 轉換成 HTML 網頁：

### 準備工作
請確保本機已安裝 Python 3.8+ 與 Markdown 解析套件：
```bash
pip install markdown
```

### 執行建置
在您的終端機（Terminal）中，將工作目錄切換到 `03_個人教學網站` 下，執行：
```bash
python build.py
```
* **腳本會自動做什麼？**
  1. 解析您所有的 Markdown 檔案。
  2. 套用 Apple 風格的 HTML 範本與 `assets/css/style.css`。
  3. 自動將所有教學文章生成為獨立網頁。
  4. 自動將這些文章、作品卡片與個人經歷動態渲染到首頁 `index.html`。

---

## 🌐 如何發布至 GitHub Pages (免費託管)

1. 在 GitHub 上建立一個新的公開儲存庫（Repository），例如命名為 `my-teaching-site`。
2. 在本機將此資料夾初始化為 Git 儲存庫，並提交（Commit）程式碼：
   ```bash
   git init
   git add .
   git commit -m "Initialize teacher portfolio website"
   ```
3. 連結遠端 GitHub 儲存庫並推上去（將 `your-username` 換成您的 GitHub 帳號）：
   ```bash
   git remote add origin https://github.com/your-username/my-teaching-site.git
   git branch -M main
   git push -u origin main
   ```
4. 進入您的 GitHub 儲存庫頁面，點擊 **Settings** -> **Pages**。
5. 在 **Branch** 區塊，選擇 `main` 分支與 `/ (root)` 資料夾，點擊 **Save**。
6. 等待約 1 到 2 分鐘，您的網站就發布成功了！網址通常為：
   `https://your-username.github.io/my-teaching-site/`
