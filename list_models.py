import os
from dotenv import load_dotenv
import google.generativeai as genai


def main():
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("🔴 Error: GOOGLE_API_KEY not found. Please set it in your .env file or environment.")
        return

    try:
        genai.configure(api_key=api_key)
        models = genai.list_models()
        print("Available models:")
        for m in models:
            print(m)
    except Exception as e:
        print(f"🔴 Error calling list_models: {e}")


if __name__ == "__main__":
    main()
