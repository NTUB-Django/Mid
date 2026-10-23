# NTUB Django｜期中版

學生個人課表與校方教務管理系統。這份版本供電腦教室下載與期中展示，使用 SQLite；不需 Docker、Node.js、PostgreSQL 或 API Key 即可操作核心功能。

## 電腦教室快速開始

準備 Python 3.10 以上版本（建議 3.12）及網路連線。Windows 安裝 Python 時勾選 Add Python to PATH。第一次安裝套件需要網路，安裝完成後查課及課表功能不會呼叫外部 API。

```sh
git clone https://github.com/NTUB-Django/Mid.git
cd Mid
python run.py
```

Windows 若找不到 python，可使用 `py -3 run.py`，或直接雙擊 `start.bat`。沒有 Git 也可在 GitHub 選 Code → Download ZIP，解壓縮後在專案資料夾執行相同指令。macOS / Linux 使用 `python3 run.py`。

啟動器會自動建立 `.venv`、安裝固定版本套件、執行資料庫 Migration、匯入附帶課程資料及建立展示帳號。**不用先啟用虛擬環境，也不用手動複製環境檔。** 下次仍執行相同指令，既有課程、密碼及課表會保留。

- 網站：http://127.0.0.1:8000/
- SimpleUI 後台：http://127.0.0.1:8000/admin/
- 按 Ctrl+C 停止。若 8000 已被占用，使用 `python run.py --port 8001`，再開啟 http://127.0.0.1:8001/。

## Windows 單檔啟動

另提供 `Classroom.bat`，可以只把這個檔案帶到學校電腦，雙擊後不需 Git，會下載公開期中版並準備 Python 環境、SQLite、課程及三種展示帳號。若沒有 Python，會嘗試透過 winget 以目前使用者身分安裝 Python 3.12；電腦教室仍須允許下載、安裝及執行 Python。

選單：1 本機啟動（預設）；2 本機加既有 Cloudflare Tunnel；3 更新程式後啟動；4 另建管理員。連接埠預設 8000，也可自行輸入。`Classroom.bat prepare` 只下載與初始化，不開啟網站。

檔案放在 Windows 目前使用者的 `%LOCALAPPDATA%\NTUB-Django-Mid`，更新會保留資料庫與帳號，但會覆蓋程式檔。使用公用電腦完畢後，請自行移除該資料夾內的個人操作資料。

Cloudflare 為選用啟動器功能，不會加入期中業務功能或自動發布 DNS。需先在 Cloudflare 設定既有 Tunnel 網域指向 `http://localhost:8000`（若更換連接埠也要一併調整），啟動時輸入網域及 token。token 不寫入批次檔、磁碟或公開 GitHub，僅交給本次 cloudflared 子程序。程式會下載官方 cloudflared 並核對官方 SHA256。此模式關閉 Django DEBUG、使用 HTTPS Cookie，須從設定的公開 HTTPS 網址登入。關閉時按 Ctrl+C，會停止本次網站與 Tunnel；不會安裝背景常駐服務。

Cloudflare 說明：[Tunnel 執行參數](https://developers.cloudflare.com/tunnel/reference/run-parameters/)。這是課堂暫時展示，不是正式主機部署。

## 展示帳號

| 身分 | 帳號 | 密碼 | 功能 |
| --- | --- | --- | --- |
| 管理員 | admin | admin1234 | SimpleUI 後台、資料與帳號管理 |
| 校方教務 | school | school123 | 全校班級課表、課程名額與學生課表巡查 |
| 學生 | student | student123 | 搜尋課程、排課、自訂行程、列印 |

以上均為程式新建的合成展示帳號與公開展示密碼，不包含任何真實帳戶。登入時依畫面的圖片驗證碼輸入。網站預設只監聽本機，不適合直接以展示帳號對外提供正式服務。

## 常用指令

在專案根目錄執行：

| 用途 | 指令 |
| --- | --- |
| 安裝、初始化並啟動 | `python run.py` |
| 只安裝與初始化 | `python run.py setup` |
| 建立自己的管理員 | `python run.py admin` |
| 初始化並檢查 Django 設定 | `python run.py check` |
| 重新安裝套件 | `python run.py setup --reinstall` |
| 更換本機連接埠 | `python run.py --port 8001` |

以下進階管理指令請使用專案虛擬環境的 Python，Windows 為 `.venv\Scripts\python.exe`，macOS / Linux 為 `.venv/bin/python`：

```sh
.venv\Scripts\python.exe manage.py createsuperuser
.venv\Scripts\python.exe manage.py changepassword admin
.venv\Scripts\python.exe manage.py import_courses --if-empty
```

建立自己的管理員會互動詢問名稱及密碼；不需在程式碼寫入密碼。初始化帳號指令不會重設已存在帳號的密碼。

## 展示順序

1. 用 student 登入，搜尋課名、查看老師與時段，將課程加入「我的課表」。
2. 試著加入衝堂課程，觀察阻擋訊息；再新增自訂行程、匯入班級課表或列印。
3. 登出後用 school 登入，查看全校班級課表與開課名額管理。
4. 到 `/admin/` 用 admin 登入，展示課程、班級、時段與帳號的新增、查詢、修改與刪除。

學生與校方請使用不同瀏覽器設定檔或無痕視窗，避免同一個登入 Session 互相覆蓋。

## 版本區分

- 本倉庫 `NTUB-Django/Mid`：獨立期中快照、SQLite、一個指令完成本機準備。
- 期末／完整版 `nasircy/Django_Thu`：持續開發版，保留 Agent、MCP、Google Calendar、Docker、PostgreSQL 與部署設定。

期中版僅包含帳號、課程、班級、課表與教務管理，已移除 Agent、MCP、Google Calendar 及其套件與入口。所有展示功能均可直接在本機操作，不需申請任何 API 金鑰。

## 資料與檔案

`data/ntub/courses_raw.jsonl` 為附帶的課程初始化資料，來源為臺北商大公開課程查詢結果，並非私人學生選課紀錄。這是資料快照，不保證與當學期即時開課完全相同。執行 `import_courses` 後，頁面讀取的是 SQLite 的 Course、Offering、OfferingSlot 與 StudentClass 資料表。

本機資料庫 `db.sqlite3`、自動產生的 `.local-secret`、`.env`、上傳檔案與虛擬環境均不會納入版本控制。備份個人操作資料時，停止網站後自行保存本機資料庫即可。

程式中的說明註解已清除；第三方授權聲明集中在 `THIRD_PARTY_NOTICES.txt`，保留必要的著作權與授權條款。SimpleUI 使用套件原本的管理介面。

## 常見問題

- 找不到 Python：安裝 Python 後重開終端機；Windows 也可用 `py -3`。
- 安裝套件失敗：確認網路可連到 PyPI，使用 Python 3.12，再執行 `python run.py setup --reinstall`。
- 無法開啟網站：保持執行指令的視窗開啟，依終端顯示的網址進入。
- `admin` 已存在：使用展示帳號密碼登入；若曾修改，使用 `manage.py changepassword admin` 設定新密碼。
- 更新程式後畫面仍舊：強制重新整理，或在瀏覽器開發工具移除舊 Service Worker 後重開網頁。

## 公開內容檢查

`python tools/check_public.py` 會檢查 Git 追蹤檔案，阻擋本機資料庫、環境檔、私人文件、常見金鑰格式與程式註解。這是輔助檢查，新增檔案前仍應確認內容適合公開。GitHub Actions 另會在 Windows、macOS 與 Linux 以 Python 3.12 執行同一套安裝及初始化指令。
