# NTUB 課表系統

這是 Django 期中專案，將學校的開課資料整理成可以自己調整的課表。學生可以找課、匯入班級課表、加入個人行程；校方可以查看班級課表與管理開課名額。管理後台使用 SimpleUI。

## 在學校電腦開啟

下載 [Classroom.bat](Classroom.bat)，帶到 Windows 電腦後雙擊，選單和連接埠都直接按 Enter 就能開始。

它會下載專案、安裝套件、建立 SQLite 資料庫、匯入課程和建立展示帳號，最後開啟網站。第一次需要網路；沒有 Python 時會嘗試安裝 Python 3.12，學校電腦需要允許安裝。

選單也可以更新程式、另建管理員，或連接已有的 Cloudflare Tunnel。下次再開啟時會保留原本的資料和密碼。

## 自己下載專案

建議使用 Python 3.12。在終端機執行：

```sh
git clone https://github.com/NTUB-Django/Mid.git
cd Mid
python run.py
```

Windows 也可以用 `py -3 run.py`，或雙擊專案內的 `start.bat`。macOS、Linux 使用 `python3 run.py`。

啟動後開啟 http://127.0.0.1:8000/，後台在 http://127.0.0.1:8000/admin/。執行中的視窗要保持開啟，按 Ctrl+C 停止。

## 展示帳號

| 身分 | 帳號 | 密碼 |
| --- | --- | --- |
| 管理員 | admin | admin1234 |
| 校方 | school | school123 |
| 學生 | student | student123 |

登入時要輸入畫面的驗證碼。這些是本機展示用的帳號；如果改過密碼，重新啟動不會改回預設值。

## 常用指令

| 要做什麼 | 指令 |
| --- | --- |
| 啟動網站 | `python run.py` |
| 只安裝、建立資料庫和帳號 | `python run.py setup` |
| 另外建立管理員 | `python run.py admin` |
| 改用 8001 連接埠 | `python run.py --port 8001` |
| 套件安裝失敗後重裝 | `python run.py setup --reinstall` |

忘記管理員密碼時，Windows 執行：

```bat
.venv\Scripts\python.exe manage.py changepassword admin
```

macOS、Linux 將前面的 Python 路徑換成 `.venv/bin/python`。

## 資料放在哪裡

課程資料來自學校公開查詢頁，附在 `data/ntub/courses_raw.jsonl`，第一次啟動時匯入資料庫，不需要重新爬取。

直接下載專案時，資料庫是專案內的 `db.sqlite3`。使用 `Classroom.bat` 時，專案會放在 `%LOCALAPPDATA%\NTUB-Django-Mid`。更新前可以先備份資料庫，離開公用電腦前記得移除自己的操作資料。

資料庫、環境檔和金鑰不放進 GitHub。這份期中版不需要 Docker 或外部 API。

## Cloudflare 連線

需要從外部開啟時，選 `Classroom.bat` 的選項 2。先在 Cloudflare 將既有 Tunnel 的網域指向 `http://localhost:8000`，再依畫面輸入網域和 token；更換連接埠時，Cloudflare 那邊也要一起改。

token 不會寫入批次檔或檔案。連線後從公開的 HTTPS 網址登入，按 Ctrl+C 結束網站與這次的 Tunnel。批次檔不會自動建立 DNS 或公開路由。
