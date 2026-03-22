import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime

try:
    # 1. マスターキー（合鍵）を使ってFirebaseにログイン
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred)

    # 2. Firestore（データベース）の操作用リモコンを取得
    db = firestore.client()
    print("☁️ Firebaseへの接続に成功しました！データを送信します...")

    # 3. クラウド上の「本棚」と「本」を指定
    # "funda_scores" という本棚（コレクション）の、"latest" という本（ドキュメント）を指定します
    doc_ref = db.collection('funda_scores').document('latest')

    # 4. 送信するテストデータ
    test_data = {
        "message": "Hello from Auto FX Quant AI!",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Online",
        "USD_score_test": 100
    }

    # 5. データをクラウドに上書き保存（set）
    doc_ref.set(test_data)
    print("✅ データの送信が完了しました！")

except Exception as e:
    print(f"❌ エラーが発生しました: {e}")

    #pcsk_4jBQbw_ATMoVsCB1Mish5g3t7D5K8VtfDXUnLy4UobgKXbkdBWPpMie6RGP1wKBBvArY5J