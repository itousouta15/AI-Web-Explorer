import os
import requests
from dotenv import load_dotenv

def setup_environment():
    # 載入環境變數並回傳 API 金鑰與搜尋引擎 ID。
    load_dotenv()
    
    api_key = os.getenv("GOOGLE_CSE_API_KEY")
    cse_id = os.getenv("GOOGLE_CSE_CX")

    if not api_key or not cse_id:
        raise ValueError("請確認 .env 檔案中已設定 GOOGLE_CSE_API_KEY 和 GOOGLE_CSE_CX。")
        
    return api_key, cse_id

def perform_web_search(query: str, api_key: str, cse_id: str, num_results: int = 5):
    """
    使用 Google Custom Search API 進行搜尋,並印出原始結果。
    """
    print(f"\n⚡ 正在為 '{query}' 執行網路搜尋...")
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'q': query,
        'key': api_key,
        'cx': cse_id,
        'num': num_results
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # 檢查請求是否成功 (狀態碼 2xx)
        
        search_results = response.json()
        
        # 檢查是否回傳 items
        if 'items' not in search_results:
            print("找不到相關的搜尋結果。")
            return
            
        print("\n--- 原始搜尋結果 ---")
        # 遍歷並印出每一條結果
        for i, item in enumerate(search_results['items']):
            title = item.get('title', '無標題')
            link = item.get('link', '無連結')
            snippet = item.get('snippet', '無摘要').replace('\n', ' ') # 移除摘要中的換行符
            
            print(f"\n[{i+1}] 標題: {title}")
            print(f"    連結: {link}")
            print(f"    摘要: {snippet}")
            
        # 回傳原始 items 以便程式化使用
        return search_results['items']
            
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 錯誤: {http_err}")
        print(f"   詳細資訊: {response.text}")
    except requests.exceptions.RequestException as req_err:
        print(f"網路連線錯誤: {req_err}")
    except Exception as e:
        print(f"發生未預期的錯誤: {e}")

def main():
    # 處理使用者輸入與呼叫搜尋功能
    try:
        api_key, cse_id = setup_environment()
        print("輸入 'quit' 或 'exit' 來離開。")

        while True:
            user_query = input("\n請輸入要搜尋的關鍵字: ")
            if user_query.lower() in ['quit', 'exit']:
                print("掰掰！")
                break
            
            if not user_query.strip():
                continue
                
            perform_web_search(user_query, api_key, cse_id)

    except ValueError as e:
        print(f"啟動失敗: {e}")

if __name__ == "__main__":
    main()

def fetch_search_results(query: str, api_key: str, cse_id: str, num_results: int = 5):
    """程式化取得搜尋結果並回傳 list(dict)（不印出）。

    回傳的每個 dict 包含至少 'title', 'link', 'snippet' 等鍵（若無則為預設值）。
    """
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'q': query,
        'key': api_key,
        'cx': cse_id,
        'num': num_results
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = response.json()
        items = results.get('items', [])
        normalized = []
        for item in items:
            normalized.append({
                'title': item.get('title', ''),
                'link': item.get('link', ''),
                'snippet': item.get('snippet', '').replace('\n', ' ')
            })
        return normalized
    except Exception:
        return []
