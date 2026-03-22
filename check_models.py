import os
import google.generativeai as genai
from dotenv import load_dotenv

# .envファイルからAPIキーを読み込む
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("🔍 Googleのサーバーに、現在利用可能な「埋め込み(Embedding)モデル」を問い合わせ中...")

try:
    # サーバーからモデル一覧を取得し、embedContentに対応しているものを探す
    found = False
    for m in genai.list_models():
        if 'embedContent' in m.supported_generation_methods:
            print(f"✅ 利用可能なモデルを発見: {m.name}")
            found = True
            
    if not found:
        print("⚠️ 埋め込み用モデルが一つも見つかりませんでした。APIキーの権限等の問題かもしれません。")
except Exception as e:
    print(f"❌ 通信エラー: {e}")