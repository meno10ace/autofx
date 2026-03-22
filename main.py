import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Firebase用ライブラリ
import firebase_admin
from firebase_admin import credentials, firestore

# 自作のクラウド記憶モジュール（先ほど作ったもの）
from pinecone_manager import check_novelty_cloud

# 自作のGemini分析モジュール（既存のもの）
# ※ご自身のファイル名・関数名に合わせて変更してください
from gemini_analyzer import analyze_news 

# ==========================================
# 1. 初期設定とクラウド接続
# ==========================================
load_dotenv()

# Firebaseの接続（重複して初期化しないための安全策）
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

def main():
    print("🚀 自動FXクオンツ・エージェントを起動します...")
    
    # --------------------------------------------------
    # 1. ニュースの取得（※ここはご自身の取得コードに置き換えてください）
    # --------------------------------------------------
    # 例：12時間分のニュースリストを取得してきたと仮定
    latest_news_list = [
        "【速報】日銀がマイナス金利政策の解除を決定しました。歴史的な転換点となります。",
        "米FRB議長、年内の利下げについて慎重な姿勢を強調。インフレ再燃を警戒。",
        "BOJ（日本銀行）は大規模金融緩和を修正し、ついにマイナス金利を撤廃する方針を固めました。" # ← これは弾かれるはず
    ]

    # 今回の実行で加算するスコアの初期化
    session_scores = {"USD": 0, "JPY": 0, "EUR": 0, "GBP": 0, "AUD": 0}
    processed_count = 0

    # --------------------------------------------------
    # 2. フィルタリング（Pinecone）と 分析（Gemini）
    # --------------------------------------------------
    for news_text in latest_news_list:
        print(f"\n📰 ニュース確認: {news_text[:30]}...")

        # 🌲 Pineconeで初耳かチェック
        is_new, _ = check_novelty_cloud(news_text)

        if is_new:
            print("🧠 初耳ニュースです！Geminiにファンダメンタルズ分析を依頼します...")
            
            try:
                # 🤖 Geminiでスコアを計算（ご自身の関数を呼び出す）
                # 戻り値は {"USD": 10, "JPY": -20, ...} のような辞書を想定
                analysis_result = analyze_news(news_text)
                
                # スコアを今回のセッションに合算
                for currency in session_scores.keys():
                    if currency in analysis_result:
                        session_scores[currency] += analysis_result[currency]
                
                processed_count += 1
                
            except Exception as e:
                print(f"❌ Gemini分析エラー: {e}")
        else:
            # 既にPineconeにある（過去に似たニュースを処理済み）場合はスキップ
            pass

    # --------------------------------------------------
    # 3. スコアの合算と Firebase（クラウド）への保存
    # --------------------------------------------------
    if processed_count > 0:
        print("\n🗄️ 新しいスコアが発生しました。Firebaseの累計データを更新します...")
        
        doc_ref = db.collection('funda_scores').document('latest')
        doc = doc_ref.get()
        
        # クラウドから「前回の累計スコア」を取得（初めてなら0スタート）
        if doc.exists:
            total_scores = doc.to_dict().get("scores", {"USD": 0, "JPY": 0, "EUR": 0, "GBP": 0, "AUD": 0})
        else:
            total_scores = {"USD": 0, "JPY": 0, "EUR": 0, "GBP": 0, "AUD": 0}

        # クラウドの累計スコアに、今回のスコアを足し合わせる
        for currency in total_scores.keys():
            total_scores[currency] += session_scores[currency]

        # Firebaseに上書き保存
        update_data = {
            "scores": total_scores,
            "last_processed_count": processed_count,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Active"
        }
        doc_ref.set(update_data)
        print(f"✅ Firebaseへのスコア保存が完了しました！ 最新累計: {total_scores}")
    else:
        print("\n💤 新しいニュースがなかったため、スコアの更新はありません。")

    print("\n🏁 エージェントの全タスクが正常に完了しました。")

if __name__ == "__main__":
    main()