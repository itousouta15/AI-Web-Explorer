import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from typing import List, Dict

from search import fetch_search_results


def setup_genai():
    load_dotenv()
    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    model_name = os.getenv('MODEL_NAME', 'models/gemini-2.5-flash-lite-preview-09-2025')
    if not api_key:
        raise ValueError('GOOGLE_API_KEY (or GEMINI_API_KEY) not found in environment')
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    return model


def ask_llm_should_search(model, question: str) -> Dict:
    """問 LLM 是否需要搜尋，並請它用 JSON 回答：{'need_search': bool, 'query': str}

    如果 LLM 回傳非 JSON，會嘗試解析失敗後以保守策略回傳 need_search=False。
    """
    system = (
        "你是一個能夠判斷是否需要網路搜尋來回答問題的助手。"
        "請僅回傳 JSON，格式：{\"need_search\": true|false, \"query\": \"...\"}。"
        "如果不需要搜尋，請將 need_search 設為 false 並提供空字串的 query。"
    )

    prompt = f"問題: {question}\n\n請依照系統指示回覆 JSON。"
    try:
        response = model.generate_content(f"{system}\n\n{prompt}")
        text = getattr(response, 'text', '')
        # 解析可能出現的 JSON
        try:
            parsed = json.loads(text.strip())
            return parsed
        except Exception:
            # 嘗試在回應中抽出 JSON 物件
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1 and end > start:
                try:
                    parsed = json.loads(text[start:end+1])
                    return parsed
                except Exception:
                    return {'need_search': False, 'query': ''}
            return {'need_search': False, 'query': ''}
    except Exception as e:
        print(f"LLM 決策呼叫失敗: {e}")
        return {'need_search': False, 'query': ''}


def ask_llm_summarize(model, question: str, search_items: List[Dict]) -> str:
    """把搜尋結果餵給 LLM，並要求它產生簡潔準確的摘要答案。"""
    # 把搜尋結果拼成一個乾淨的文字塊（只保留 title, snippet, link）
    snippet_lines = []
    for i, it in enumerate(search_items[:8]):
        snippet_lines.append(f"[{i+1}] {it.get('title','')}: {it.get('snippet','')} ({it.get('link','')})")

    context = "\n".join(snippet_lines)

    system = (
        "你是一位專業研究助理，負責在提供的網路搜尋結果中找出事實性資訊並回覆原始問題。"
        "請依據提供的搜尋結果回答，並在答案最後標註使用了幾個搜尋來源。"
    )

    prompt = (
        f"原始問題：{question}\n\n"
        "以下是檢索到的搜尋結果（原始）；請基於這些結果產生一個簡潔、事實導向的答案。"
        f"\n\n{context}\n\n回答："
    )

    try:
        response = model.generate_content(f"{system}\n\n{prompt}")
        return getattr(response, 'text', '')
    except Exception as e:
        print(f"LLM 生成摘要失敗: {e}")
        return "無法由 LLM 產生摘要（發生錯誤）。"


def run_agent():
    # 初始化
    try:
        model = setup_genai()
    except Exception as e:
        print(f"Agent 初始化失敗：{e}")
        return

    load_dotenv()
    cse_key = os.getenv('GOOGLE_CSE_API_KEY') or os.getenv('GOOGLE_API_KEY')
    cse_cx = os.getenv('GOOGLE_CSE_CX') or os.getenv('GOOGLE_CSE_ID') or os.getenv('GOOGLE_CSE_CX')

    if not cse_key or not cse_cx:
        print('警告：未找到 Custom Search API key 或 CX，agent 在需要搜尋時會失敗。')

    print('🚀 Agent ready. 輸入問題（輸入 exit 或 quit 結束）')
    while True:
        q = input('You: ')
        if q.strip().lower() in ['exit', 'quit']:
            print('Goodbye')
            break
        if not q.strip():
            continue

        decision = ask_llm_should_search(model, q)
        need_search = bool(decision.get('need_search', False))
        search_query = decision.get('query', '')

        if need_search and search_query and cse_key and cse_cx:
            print(f"🔎 Agent 決定要搜尋：{search_query}")
            items = fetch_search_results(search_query, cse_key, cse_cx, num_results=5)
            if not items:
                print('⚠️ 搜尋沒有回傳結果或發生錯誤，直接請 LLM 回答（不使用搜尋結果）')
                ans = ask_llm_summarize(model, q, [])
            else:
                ans = ask_llm_summarize(model, q, items)
        else:
            # 不需要搜尋 -> 直接讓 LLM 回答
            print('💬 Agent 決定不需搜尋，直接由 LLM 回答...')
            ans = ask_llm_summarize(model, q, [])

        print('\n=== Agent Answer ===')
        print(ans)
        print('====================\n')


if __name__ == '__main__':
    run_agent()
