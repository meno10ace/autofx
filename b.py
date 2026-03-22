import chromadb
import json
import os
from datetime import datetime

# ==========================================
# 1. データベースの初期設定
# ==========================================

# スコア管理用JSONファイルのパス
SCORE_FILE = "currency_scores.json"

# ChromaDBの初期化（ここではテスト用にメモリ上で動かします）
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="news_memory")

# ==========================================
# 2. JSONの読み書き関数（Score Manager）
# ==========================================

def load_scores():
    """JSONから現在のスコアを読み込む"""
    if os.path.exists(SCORE_FILE):
        with open(SCORE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    # ファイルが無ければ初期値を返す
    return {"USD": 0, "JPY": 0, "EUR": 0, "last_updated": ""}

def save_scores(scores):
    """スコアをJSONに保存する"""
    with open(SCORE_FILE, 'w', encoding='utf-8') as f:
        json.dump(scores, f, indent=2, ensure_ascii=False)

# ==========================================
# 3. メイン処理：ニュースのフィルタリングと採点
# ==========================================

def process_news(news_id, news_text):
    print(f"\n📰 新着ニュース受信: {news_text}")

    # ① 記憶（ChromaDB）から類似ニュースを検索
    # まだデータが空の場合はスキップする処理を入れています
    if collection.count() > 0:
        results = collection.query(
            query_texts=[news_text],
            n_results=1
        )
        
        # 距離（Distance）が近い＝内容が似ている（※0.3以下を「既出」と判定する例）
        if results['distances'][0] and results['distances'][0][0] < 0.3:
            print("🛑 【判定】これは既出のニュースです。AIへの送信をスキップします。")
            return

    print("🟢 【判定】新規性の高いニュースです！Geminiで解析します...")

    # ② （本来はここにStep1のGemini APIを叩く処理が入ります）
    # 今回はダミーで「JPYが -20点 された」という結果が返ってきたと仮定します
    ai_result = {"currency": "JPY", "score_change": -20}
    
    # ③ JSONのスコアを更新（Score Manager）
    current_scores = load_scores()
    current_scores[ai_result["currency"]] += ai_result["score_change"]
    current_scores["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_scores(current_scores)
    
    print(f"📈 【スコア更新】{ai_result['currency']} のスコアを {ai_result['score_change']} しました。")
    print(f"📊 現在の全スコア: {current_scores}")

    # ④ このニュースをChromaDBに「記憶」させる
    collection.add(
        documents=[news_text],
        metadatas=[{"date": current_scores["last_updated"]}],
        ids=[news_id]
    )
    print("🧠 ニュースをChromaDBの記憶に保存しました。")

# ==========================================
# 🧪 実験テストの実行
# ==========================================

# 1通目：まったく新しいニュース
process_news("news_001", "日銀、次回の決定会合でマイナス金利解除を見送りへ")

# 2通目：少し言い回しが違うだけの同じニュース（類似度で弾かれるかテスト）
process_news("news_002", "日本銀行はマイナス金利政策の解除を次回の会合では見送る公算")

# 3通目：全く違うテーマの新しいニュース
process_news("news_003", "米FRB、インフレ懸念から年内の追加利上げを示唆")