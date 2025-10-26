# AI-Web-Explorer


此專案包含三個主要腳本：

- `main.py`：互動式問答介面，連接 Google Generative AI（Gemini）。會從 `.env` 讀取 `GOOGLE_API_KEY`，並建立一個 `GenerativeModel` 來回應使用者輸入。
- `list_models.py`：列出你帳號可存取的 Generative AI 模型（使用 `google.generativeai.list_models()`）。會從 `.env` 讀取 `GOOGLE_API_KEY`。
- `search.py`：獨立的網路搜尋測試工具，使用 Google Custom Search JSON API，會從 `.env` 讀取 `GOOGLE_CSE_API_KEY` 與 `GOOGLE_CSE_CX`，接收使用者輸入關鍵字並印出原始搜尋結果（標題、連結、摘要）。

本 README 會帶你完成環境建立、設定、執行範例、常見問題與後續建議。

## 先決條件

- 已安裝 Python（建議 3.11+）。
- 建議使用虛擬環境 (`venv`) 來隔離相依套件。

## 建立與啟用虛擬環境（Windows / PowerShell）

在專案根目錄執行：

```powershell
# 建立 venv
python -m venv .venv

# 啟用 venv
.\.venv\Scripts\Activate.ps1

# 更新 pip 並安裝 requirements
.\.venv\Scripts\python -m pip install --upgrade pip setuptools wheel
.\.venv\Scripts\python -m pip install -r .\requirements.txt
```

提示：若你不想啟用 Activate，可直接用 `.venv\Scripts\python` 呼叫腳本與 pip。

## 必要的環境變數（ `.env` ）

請在專案根目錄建立一個 `.env`，至少包含以下兩組變數（依你要執行的腳本而定）：

```
# 用於 Gemini / generativeai
GOOGLE_API_KEY=你的_Google_Generative_API_Key

# 用於 Custom Search (search.py)
GOOGLE_CSE_API_KEY=你的_Google_API_Key_for_Custom_Search
GOOGLE_CSE_CX=你的_Custom_Search_Engine_ID
```

（範例：專案中觀察到你使用過 `GOOGLE_CSE_API_KEY` 和 `GOOGLE_CSE_CX`，`main.py` 和 `list_models.py` 使用 `GOOGLE_API_KEY`。）

注意：不要把 `.env` 推上公開儲存庫。建議新增 `.env.example`（僅列出變數名稱）並把 `.env` 加入 `.gitignore`。

## 執行三個主要腳本

1) 互動式 AI（`main.py`）

```powershell
.\.venv\Scripts\python .\main.py
```

- 此腳本會：
  - 讀取 `.env` 的 `GOOGLE_API_KEY`。
  - 使用 `google.generativeai` 設定 API 金鑰，建立 `GenerativeModel('gemini-1.0')`（可自行變更為 `gemini-2.5-pro` 等）。
  - 以迴圈方式讀取使用者輸入並呼叫 `model.generate_content()`，印出回應文字。
  - 若沒有找到 `GOOGLE_API_KEY`，會印出錯誤並結束：

```
🔴 Error: GOOGLE_API_KEY not found. Please set it in your .env file.
```

2) 列出可用模型（`list_models.py`）

```powershell
.\.venv\Scripts\python .\list_models.py
```

- 用於查看帳號可使用的模型名稱（方便在 `main.py` 中指定 model）。

3) 網路搜尋測試（`search.py`）

```powershell
.\.venv\Scripts\python .\search.py
```

- `search.py`（你已將 `simple_search_tool.py` 重新命名）會：
  - 從 `.env` 讀取 `GOOGLE_CSE_API_KEY` 與 `GOOGLE_CSE_CX`。
  - 接收使用者輸入關鍵字並呼叫 Google Custom Search JSON API。
  - 印出每條結果的標題（title）、連結（link）與摘要（snippet）。

非互動式測試（PowerShell here-string）

```powershell
@"
Python requests library
exit
"@ | .\.venv\Scripts\python .\search.py
```

## 範例輸出（來自 `search.py`）

```
✅ 簡易搜尋工具已就緒！輸入 'quit' 或 'exit' 來離開。

請輸入要搜尋的關鍵字:
⚡ 正在為 'Python requests library' 執行網路搜尋...

--- 原始搜尋結果 ---

[1] 標題: requests · PyPI
    連結: https://pypi.org/project/requests/
    摘要: Installing Requests and Supported Versions ...
...
```

## 啟用 Google Custom Search 與 API 權限（快速檢查）

- 在 Google Cloud Console 中確認：
  - 已為你的專案啟用 **Custom Search JSON API**。
  - 若使用某些模型或 GCP 服務，也要確認對應 API 已啟用與計費設定（billing）。
- Custom Search Engine（CSE）設定：
  - 登入 https://cse.google.com/ 並建立一個搜尋引擎，取得 `cx`（即 `GOOGLE_CSE_CX`）。
  - 若要搜尋整個網路，CSE 的設定中請選擇“搜尋整個網路”（可能需要額外步驟/設定）。

## 常見問題與除錯

- ModuleNotFoundError: No module named 'google' 或 'dotenv'
  - 原因：使用的 `python` 不是安裝相依套件的環境。請用：

```powershell
python -c "import sys; print(sys.executable)"
```

  - 若結果不是 `.venv\Scripts\python.exe`，請改用該可執行檔安裝或執行：

```powershell
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python .\search.py
```

- HTTP 401 / 403 錯誤
  - 常見原因：API key 無效、未啟用 Custom Search JSON API、或該 key 不允許呼叫該 API。
  - 解法：確認 `GOOGLE_CSE_API_KEY` 對應正確的 GCP 專案，並在 Cloud Console 啟用 Custom Search JSON API、檢查 API 限制（如 IP 或 referrer 限制）。

- 找不到 `items`（沒有搜尋結果）
  - 可能是搜尋引擎設為僅搜尋特定網站，或 CSE 尚未正確設定為搜尋整個網路。

## 安全建議

- 永遠把 `.env` 加入 `.gitignore`，不要將真實 API key 提交到公開版本控制。建議加入 `.env.example`（只包含變數名與說明）。

## 後續改進建議（你可以指派我實作）

- 把 `search.py` 的結果同時輸出為 JSON（例如 `results.json`），方便程式化處理。 
- 將 `main.py` 改為接受 CLI 引數或設定檔來指定 model name、temperature、max tokens 等參數。
- 把 `list_models.py` 的輸出匯出為 JSON，以及新增小工具選擇支援 `generateContent` 的模型。

---

如果你要，我可以立刻：

- 新增 `.env.example` 與更新 `.gitignore`（把 `.env` 忽略），
- 把 `search.py` 改為同時輸出 JSON 檔（例如 `results.json`），並在 README 裡加入範例，或
- 把 `main.py` 改成可從 CLI 指定 model name（並新增小型單元測試）。

請告訴我你要我做哪一件，我會立刻著手實作。
# AI-Web-Explorer

說明：這份 README 說明如何在 Windows (PowerShell) 建立虛擬環境、安裝相依套件，並執行 `main.py`。

## 前置條件
- Python 3.11+ 建議（確認你的系統已安裝 Python）。

## 建立虛擬環境（在專案根目錄）
在專案根目錄（包含 `main.py` 與 `requirements.txt`）執行：
# AI-Web-Explorer

完整說明（繁體中文） — 這份 README 會帶你從環境建立到執行範例，並清楚說明專案中兩個主要程式的用途：`main.py`（互動式問答介面）與 `list_models.py`（列出可用模型）。

## 專案概覽
- `main.py`：互動式 CLI，載入 `.env` 的 `GOOGLE_API_KEY`，設定 `google.generativeai`，建立一個 `GenerativeModel` 並在迴圈中讀取使用者輸入，呼叫模型產生回應後印出（使用者可輸入 `exit` 或 `quit` 離開）。
- `list_models.py`：載入 `.env` 的 `GOOGLE_API_KEY` 並呼叫 `google.generativeai.list_models()`，列出帳號可用的模型清單（方便你選擇要在 `main.py` 中使用的 model name）。

程式設計重點：兩個程式都使用 `python-dotenv` 讀取 `.env`（選擇性）與 `google-generativeai` 套件去連到 Google 的 Generative AI 服務。

> 安全提醒：不要把真實的 API key 推上公開版控（例如 GitHub）。把 `.env` 加入 `.gitignore`，並用 `.env.example` 提供變數範例。

## 目標平台
- Windows（PowerShell） — README 中的命令以 PowerShell 為主，其他 shell 也適用但語法略有不同。

## 前置需求
- 已安裝 Python（建議 3.11+）。
- 建議使用虛擬環境（`venv`）來隔離套件。

## 快速開始（建立 venv、安裝套件）
在專案根目錄（包含 `main.py`、`list_models.py`、`requirements.txt`）執行：

```powershell
# 建立虛擬環境
python -m venv .venv

# 更新 pip 並安裝 requirements
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r .\requirements.txt
```

備註：若系統 `python` 指向其他安裝（例如 Inkscape 或其他程式隨附的 Python），請改用該環境的完整路徑或使用剛建立的 `.venv\Scripts\python`。

## 設定 API Key（`.env`）
在專案根目錄建立 `.env` 檔案，內容格式如下（不要加到版本控制）：

```
GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY_HERE
```

或在 PowerShell 暫時設環境變數（只在該 shell 有效）：

```powershell
$env:GOOGLE_API_KEY = 'YOUR_GOOGLE_API_KEY_HERE'
```

## 執行 `main.py`（互動式問答）
建議先啟用 venv（非必要）：

```powershell
.\.venv\Scripts\Activate.ps1
# 提示符變成 (.venv) 後
python .\main.py
```

或直接以 venv 的 python 執行（不改變 shell 的執行政策）：

```powershell
.\.venv\Scripts\python .\main.py
```

使用說明（`main.py` 的行為）
- 啟動時會嘗試讀取 `.env`（使用 `python-dotenv`）。
- 會找 `GOOGLE_API_KEY`：若找不到，程式會印出錯誤並結束：

```
🔴 Error: GOOGLE_API_KEY not found. Please set it in your .env file.
```
- 若有 key，程式會呼叫 `genai.configure(api_key=...)`，然後建立 `GenerativeModel('gemini-1.0')`。
- 進入互動迴圈：每行輸入視為 prompt，呼叫 `model.generate_content(question)`，並印出 `response.text`。
- 輸入 `exit` 或 `quit` 結束程式。

範例互動（示意）

```text
🧠 Your AI Brain is ready. Ask me anything!
------------------------------------------
You: Hello
AI: Hello! 怎麼了？
You: exit
🤖 Goodbye!
```

注意：實際回應內容會依你使用的模型與 API 回傳為準，並會產生 API 使用費用（請依你的帳號計費政策注意成本）。

## 執行 `list_models.py`（列出可用模型）
你可以先在 venv 下執行：

```powershell
.\.venv\Scripts\python .\list_models.py
```

此程式會：
- 載入 `.env` 中的 `GOOGLE_API_KEY`（或使用環境變數）。
- 呼叫 `genai.configure(api_key=...)`。
- 呼叫 `genai.list_models()` 並把結果印出來（每個 model 物件包含 name、display_name、token limit、supported_generation_methods 等屬性）。

範例輸出（節錄自執行結果）

```
Available models:
Model(name='models/gemini-2.5-pro', display_name='Gemini 2.5 Pro', input_token_limit=1048576, output_token_limit=65536, ...)
Model(name='models/gemini-2.5-flash', display_name='Gemini 2.5 Flash', input_token_limit=1048576, ...)
Model(name='models/embedding-001', display_name='Embedding 001', input_token_limit=2048, ...)
...
```

建議：從 `list_models.py` 結果中選擇一個支援 `generateContent` 的 `model.name`，並在 `main.py` 裡將 `GenerativeModel('gemini-1.0')` 替換為該 model 名稱（或改寫程式以從設定讀取 model name）。

## 非互動測試（PowerShell here-string）
快速在 script 或 CI 中測試 `main.py` 的自動輸入：

```powershell
@"
Hello
exit
"@ | .\.venv\Scripts\python .\main.py
```

這個範例會把兩行輸入（Hello 與 exit）傳給 `main.py`，程式會接收 `Hello` 呼叫模型、輸出後再接收 `exit` 並結束。

## 常見問題與除錯
- ModuleNotFoundError: No module named 'google'
	- 原因：你執行的 `python` 不是安裝 `google-generativeai` 的環境。
	- 檢查當前 python 路徑：

```powershell
python -c "import sys; print(sys.executable)"
```

	- 若不是 `.venv\Scripts\python.exe`，請使用 `.venv\Scripts\python -m pip install -r requirements.txt` 安裝套件或直接以 `.venv\Scripts\python` 執行程式。

- PowerShell 啟用 venv 時出現權限錯誤
	- 若 Activate.ps1 被封鎖，可用：

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

	- 或直接用 `.venv\Scripts\python main.py` 跳過 Activate。

- API 呼叫錯誤或權限/計費問題
	- 若 `list_models.py` 或 `main.py` 回報與 API 權限或計費相關的錯誤，請確認你在 Google Cloud / Generative AI 平臺已啟用相關 API、並在該帳號上完成必要的 billing 設定。

## 安全與最佳實務
- 千萬不要把 `.env` 裡的 `GOOGLE_API_KEY` 推上公開儲存庫。
- 在 repo 中新增 `.env.example`（只包含變數名稱）並在 `.gitignore` 裡排除 `.env`。

## 建議的後續改進（可選）
- 把 `main.py` 改成可從 CLI 參數或設定檔指定 model name（現在程式寫死使用 `gemini-1.0`）。
- 新增一個 `config.py` 或 `settings.toml`，用來管理 model、temperature、max_tokens 等參數。
- 把 `list_models.py` 輸出改成 JSON，方便自動化處理或產生 model 選單。

---

如果你要，我可以：

- 幫你新增 `.env.example` 與更新 `.gitignore`（把 `.env` 忽略），
- 或把 `main.py` 改成可以從命令列參數指定 model name（並加入小型測試），
- 或把 `list_models.py` 輸出寫成 JSON 檔。

告訴我你要哪一個，我會繼續實作。

Hello
exit
"@ | .\.venv\Scripts\python .\main.py
```

執行後你會看到程式印出啟動訊息、模型回應（若有設定 `GOOGLE_API_KEY` 並能成功呼叫 API），最後程式結束。

範例：若沒有設定 `GOOGLE_API_KEY` 的話，啟動會印出：

```
🔴 Error: GOOGLE_API_KEY not found. Please set it in your .env file.
```


## 範例 `.env.example`
```
# 請複製為 .env 並填入你的金鑰
GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY_HERE
```

## 安全提示
- 請勿將 `.env`（含 API 金鑰）提交到公開的版本控制系統。把 `.env` 加入 `.gitignore`（如尚未加入）。

## 其他備註
- 若你要在 CI 或遠端伺服器上執行，請在該環境使用相同步驟建立虛擬環境或使用容器化方式。 

---

若要我把一個 `.env.example` 檔案與 `.gitignore` 更新加入專案，我也可以替你新增。告訴我你要我幫忙的細節（例如預設 .gitignore 項目）。
