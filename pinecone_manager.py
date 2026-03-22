import google.generativeai as genai
from pinecone import Pinecone, ServerlessSpec
import hashlib
from datetime import datetime
import os
from dotenv import load_dotenv

# .envファイルの中身を読み込む
load_dotenv()

# ==========================================
# 1. APIキーの設定（環境変数から安全に取得）
# ==========================================
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# エラーチェック（もし読み込めなかったら警告を出すプロの書き方）
if not PINECONE_API_KEY or not GEMINI_API_KEY:
    raise ValueError("🚨 .env ファイルからAPIキーが読み込めません！ファイルが存在するか確認してください。")


# Geminiの設定（テキストを数値ベクトルに変換する専用モデルを使います）
genai.configure(api_key=GEMINI_API_KEY)
EMBEDDING_MODEL = 'models/gemini-embedding-001' # ← ここを安定版の 001 に変更！

# Pineconeの設定
pc = Pinecone(api_key=PINECONE_API_KEY)
INDEX_NAME = "funda-news-index-v2"

# ==========================================
# 2. クラウド・インデックス（記憶の箱）の準備
# ==========================================
def setup_pinecone():
    """Pinecone上にベクトルを保存する箱（インデックス）を作成します"""
    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
    
    if INDEX_NAME not in existing_indexes:
        print("🌲 Pineconeに新しい記憶の箱（インデックス）を作成中...（約1分かかります）")
        pc.create_index(
            name=INDEX_NAME,
            dimension=3072, # Geminiのベクトルの次元数
            metric="cosine", # 類似度計算の方式（コサイン類似度）
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1" # 無料枠の標準サーバー
            )
        )
        print("✅ インデックスの作成が完了しました！")
    return pc.Index(INDEX_NAME)

# インデックスへの接続
index = setup_pinecone()

# ==========================================
# 3. 記憶の照合と保存（メインロジック）
# ==========================================
def check_novelty_cloud(news_text, threshold=0.85):
    """
    ニュースが初耳かどうかをPineconeに問い合わせる
    戻り値: (is_new: bool, similarity_score: float)
    """
    try:
        # 1. ニューステキストをGeminiでベクトル（768個の数字の列）に変換
        embedding_result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=news_text
        )
        vector = embedding_result['embedding']

        # 2. Pineconeに「過去に似たベクトルはないか？」と検索（上位1件を取得）
        search_results = index.query(
            vector=vector,
            top_k=1,
            include_metadata=True
        )

        # 3. 類似度（スコア）の判定
        if len(search_results['matches']) > 0:
            highest_score = search_results['matches'][0]['score']
            matched_text = search_results['matches'][0]['metadata'].get('text', '')
            
            if highest_score >= threshold:
                print(f"💤 【重複スキップ】類似度 {highest_score:.2f} の過去ニュースと意味が一致しました。")
                print(f"   (過去のニュース: {matched_text[:30]}...)")
                return False, highest_score

        # 4. 初耳（閾値未満）なら、Pineconeに新しい記憶として保存（Upsert）
        # 記事のハッシュ値（一意のID）を作成
        news_id = hashlib.md5(news_text.encode()).hexdigest()
        
        # 🛡️ 日本語で通信エラーが起きないよう、英語の暗号（ASCII）に変換
        safe_text = news_text.encode('unicode-escape').decode('ascii')

        index.upsert(
            vectors=[{
                "id": news_id, 
                "values": vector, 
                "metadata": {
                    "text": safe_text, # 暗号化して保存
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            }]
        )
        print("🧠 【初耳ニュース】Pineconeに新しい記憶を刻み込みました。")
        return True, 0.0

    except Exception as e:
        print(f"❌ Pinecone/Gemini連携エラー: {e}")
        # エラー時は安全のために処理を通す（または落とす）設計。今回は通します。
        return True, 0.0

# ==========================================
# 🧪 テスト実行
# ==========================================
if __name__ == "__main__":
    print("\n--- 🧪 第1回テスト: 初めてのニュース ---")
    news_1 = "【速報】日銀がマイナス金利政策の解除を決定しました。歴史的な転換点となります。"
    is_new_1, _ = check_novelty_cloud(news_1)

    print("\n--- 🧪 第2回テスト: 言い回しを変えた同じニュース ---")
    news_2 = "BOJ（日本銀行）は大規模金融緩和を修正し、ついにマイナス金利を撤廃する方針を固めました。"
    is_new_2, _ = check_novelty_cloud(news_2)
    
    print("\n--- 🧪 第3回テスト: 全く違うニュース ---")
    news_3 = "米FRB議長、年内の利下げについて慎重な姿勢を強調。"
    is_new_3, _ = check_novelty_cloud(news_3)