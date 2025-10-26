import os
import google.generativeai as genai
from dotenv import load_dotenv

def main():
    # 讀取.env
    load_dotenv()

    # Get API key
    api_key = os.getenv("GOOGLE_API_KEY")

    # Check API key is available
    if not api_key:
        print("🔴 Error: GOOGLE_API_KEY not found. Please set it in your .env file.")
        return

    # 設定 Gemini API
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-2.5-flash-lite-preview-09-2025') # 可用模型可以運行 list_models.py 來查看
    except Exception as e:
        print(f"🔴 Error configuring Gemini API: {e}") # 錯誤訊息
        return

    print("🧠 Your AI Brain is ready. Ask me anything!")
    print("------------------------------------------")

    # 輸入並回應
    while True:
        question = input("You: ")
        if question.lower() in ['exit', 'quit']:
            print("🤖 Goodbye!")
            break
        
        if not question.strip():
            continue

        try:
            response = model.generate_content(question)
            print(f"AI: {response.text}\n")
        except Exception as e:
            print(f"🔴 An error occurred while generating the response: {e}")


if __name__ == "__main__":
    main()