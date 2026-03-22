import google.generativeai as genai
import json
import time
import re
import os
from dotenv import load_dotenv

# .envファイルの中身を読み込む
load_dotenv()

# ==========================================
# 1. APIキーの設定（環境変数から安全に取得）
# ==========================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# エラーチェック（もし読み込めなかったら警告を出すプロの書き方）
if not GEMINI_API_KEY:
    raise ValueError("🚨 .env ファイルからAPIキーが読み込めません！ファイルが存在するか確認してください。")

genai.configure(api_key=GEMINI_API_KEY)

# モデルの指定（高速でJSON出力に強いFlashモデルがおすすめ）
model = genai.GenerativeModel('gemini-2.5-flash')

def analyze_news(news_text):
    """
    ニューステキストをGeminiに投げ、スコア化されたJSONを返す
    """
    print("🧠 Geminiにニュースの解析を依頼中...")

    # システムプロンプト（AIへの絶対的な指示）
    # ※クオンツとしての判断基準と、出力形式をガチガチに固めます
    prompt = f"""
    あなたは世界トップクラスのマクロヘッジファンドのクオンツAIです。
    以下のFX関連ニュースを分析し、指定されたJSONフォーマットのみで出力してください。
    それ以外の挨拶や説明は一切不要です。

    【ニュース本文】
    {news_text}

    【分析ルール】
    1. 対象となる主要通貨（USD, JPY, EUR, GBP, AUD, etc）を抽出。
    2. ニュースがその通貨にとって「買い」ならプラススコア(1〜100)、「売り」ならマイナススコア(-1〜-100)を判定。
    3. カテゴリーを次の中から1つ選択: [Monetary_Policy, Economic_Data, Geopolitics, Other]
    4. フェーズを次の中から1つ選択: [fact, rumor]
    5. 分析理由を日本語で簡潔に記述。

    【出力JSONフォーマット例】
    {{
      "USD": {{
        "score": 80,
        "category": "Monetary_Policy",
        "phase": "fact",
        "reason": "FRB議長が年内の追加利上げを示唆したため。"
      }},
      "JPY": {{
        "score": -40,
        "category": "Monetary_Policy",
        "phase": "rumor",
        "reason": "日銀の緩和継続の観測報道が出たため。"
      }}
    }}
    """

    try:
        # APIリクエストを送信
        response = model.generate_content(prompt)
        result_text = response.text

        # 💡 防御力UP: markdownの ```json ... ``` などの装飾を正規表現で剥がす
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            clean_json = json_match.group(0)
            # JSONとして読み込めるかテスト
            parsed_data = json.loads(clean_json)
            print("✅ Geminiの解析成功！")
            return parsed_data
        else:
            print("⚠️ AIの出力からJSONを抽出できませんでした。")
            return None

    except Exception as e:
        print(f"❌ Gemini APIエラー: {e}")
        return None

# ==========================================
# 🧪 テスト実行
# ==========================================
if __name__ == "__main__":
    # テスト用のニューステキスト
    sample_news = "【速報】米CPI（消費者物価指数）が事前予想の3.1%を上回る3.4%に急上昇。インフレ再燃の懸念から、市場では年内の利下げ観測が急速に後退している。"
    
    result = analyze_news(sample_news)
    
    if result:
        print("\n👇 プログラムが扱える辞書データ（JSON）として返ってきました！")
        print(json.dumps(result, indent=2, ensure_ascii=False))