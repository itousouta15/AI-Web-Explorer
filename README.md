# AI-Web-Explorer

一個簡易的原型專案，展示如何把 LLM（Google Generative AI / Gemini）與網頁搜尋工具整合成一個可執行的代理（Agent）。

本專案目前包含：

- `main.py` — 互動式問答，直接呼叫 `google.generativeai` 的 model（示範基本的 Gemini 用法）。
- `list_models.py` — 列出帳號可用的模型（方便選擇）。
- `search.py` — 原本的 simple_search_tool，現提供程式化函式 `fetch_search_results()` 與 CLI，使用 Google Custom Search JSON API。
- `agent.py` — 代理（orchestrator），由 LLM 決策是否要搜尋；若需要，呼叫 `search.fetch_search_results()`，把結果交回 LLM 以產生最終摘要。

README 會說明如何建立環境、配置 API keys、執行每個腳本，以及常見除錯與後續建議。

---

## 快速準備（Windows / PowerShell）

1. 建立並啟用虛擬環境

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. 更新安裝工具並安裝相依

```powershell
.\.venv\Scripts\python -m pip install --upgrade pip setuptools wheel
.\.venv\Scripts\python -m pip install -r .\requirements.txt
```

（如果你的系統 Python 版本是 3.12/3.13 並在安裝時遇到 pydantic-core 或需編譯的套件失敗，請改安裝 Python 3.11 並用它建立 venv，或安裝 Rust toolchain；建議使用 Python 3.11）

---

## 必要環境變數（`.env`）

在專案根目錄建立 `.env`（不要把真實金鑰推上 public repo）：

```
# 用於 Gemini / google-generativeai
GOOGLE_API_KEY=your_gemini_api_key_here
# 可選：指定 model
MODEL_NAME=gemini-2.5-pro

# 用於 Google Custom Search（search.py 與 agent.py 使用）
GOOGLE_CSE_API_KEY=your_custom_search_api_key_here
GOOGLE_CSE_CX=your_search_engine_id_here
```

注意：你的專案中也曾使用過 `GOOGLE_CSE_API_KEY` / `GOOGLE_CSE_CX`（或 `GOOGLE_CSE_ID`），請把對應的變數放入 `.env`。

---

## 各腳本說明與執行範例

下面提供每個腳本的用途與示範指令（PowerShell）：

### 1) `main.py` — 直接與 Gemini 互動

用途：示範如何用 `google.generativeai` 建立 model 並在 CLI 中與 LLM 對話。

執行：

```powershell
.\.venv\Scripts\python .\main.py
```

行為要點：
- 讀取 `GOOGLE_API_KEY`，呼叫 `genai.configure(api_key=...)`。
- 建立 `GenerativeModel`（預設在程式中可看到是哪個 model），然後在迴圈中呼叫 `model.generate_content()`。

如果缺少 API key，程式會印出錯誤並結束：

```
🔴 Error: GOOGLE_API_KEY not found. Please set it in your .env file.
```

### 2) `list_models.py` — 列出可用模型

用途：查詢帳號可用模型（name、display_name、supported_generation_methods 等），用來選擇合適的 model。

執行：

```powershell
.\.venv\Scripts\python .\list_models.py
```

輸出會列出模型物件或模型清單（大量資訊，適合做為選擇依據）。

### 3) `search.py` — Google Custom Search 工具（CLI + 程式化函式）

用途：作為搜尋工具原型，提供 `perform_web_search()`（會印出結果）與 `fetch_search_results()`（回傳 list(dict)）以供 agent 或其他程式呼叫。

執行（互動式）：

```powershell
.\.venv\Scripts\python .\search.py
```

非互動式（測試）：

```powershell
@"
Python requests library
exit
"@ | .\.venv\Scripts\python .\search.py
```

回傳欄位（每條 item）：`title`, `link`, `snippet`。

### 4) `agent.py` — LLM + 工具整合的代理

用途：示範 Agent 編排流程：

- 接收使用者問題。 
- 呼叫 LLM（Gemini）判斷是否需要搜尋（`ask_llm_should_search`，要求 LLM 回傳 JSON 指示）。
- 若需要則呼叫 `search.fetch_search_results()`，並把結果回傳給 LLM 要求摘要（`ask_llm_summarize`）。

執行：

```powershell
.\.venv\Scripts\python .\agent.py
```

行為說明：
- `agent.py` 會從 `.env` 讀取 Gemini API key 與 Custom Search key/CX。若缺少 Custom Search key，agent 仍可運行但在需要搜尋時會提示錯誤。
- LLM 決策解讀：agent 嘗試解析 LLM 回傳的 JSON；若解析失敗，agent 會保守處理（不進行搜尋）。你可改進為混合規則（LLM 建議 + 關鍵字規則）。

---

## 除錯與常見問題

- ModuleNotFoundError: No module named 'google' 或 'dotenv'
  - 原因：你可能在系統 Python（非 venv）執行或尚未安裝相依套件。
  - 檢查 Python 可執行檔：

```powershell
python -c "import sys; print(sys.executable)"
```

  - 若不是 `.venv\Scripts\python.exe`，請使用 venv 的 python 安裝套件或執行程式：

```powershell
.\.venv\Scripts\python -m pip install -r .\requirements.txt
.\.venv\Scripts\python .\agent.py
```

- pydantic-core / wheel build 錯誤（在 Python 3.12/3.13）
  - 問題：某些套件（例如 pydantic-core）在新 Python 版本上可能需要本機編譯（Rust toolchain），導致 pip build 失敗。
  - 解法（推薦）：安裝 Python 3.11，並用 `py -3.11 -m venv .venv` 建 venv；或在現有環境安裝 Rust（較複雜）。

- API 401 / 403 或權限錯誤
  - 檢查 `.env` 的 key 是否正確、API 是否在 Google Cloud Console 中啟用、以及金鑰是否有呼叫限制（IP、HTTP referrer）。

- Custom Search 找不到 `items`
  - 檢查你的 CSE（cx）是否設定為搜尋整個網路或包含你要的目標網站。

---

## 安全與最佳實務

- 把 `.env` 加入 `.gitignore`，不要上傳 API key。建議新增一個 `.env.example` 只包含變數名稱。
- 在 agent 中限制回傳給 LLM 的上下文長度（只提供必要的 title/snippet/link），以節省 token 並避免洩露不必要的內容。

---

## 建議的下一步（我可以代工）

1. 新增 `.env.example` 與更新 `.gitignore`（把 `.env` 忽略）。
2. 把 `search.py` 的程式化搜尋結果同時輸出 JSON（`results.json`），並在 `agent.py` 將相關 metadata 儲存到檔案以便追蹤。
3. 強化 `ask_llm_should_search`：採用 LLM 提議 + 規則過濾的混合決策以降低誤判。
4. 將 `main.py`/`agent.py` 改為可用 CLI 參數（argparse）指定 model、temperature、max_tokens，以便實驗不同組合。

如果要我幫你做其中一項或全部，告訴我優先順序，我會立刻實作。


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
