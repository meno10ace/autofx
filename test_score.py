import json
import os
from datetime import datetime

SCORE_FILE = "currency_scores.json"

# ==========================================
# 1. テスト用のダミーデータ作成（初回のみ実行）
# ==========================================
def create_dummy_data():
    """48時間前に +100点 の特大ニュースが出た、という状態を作る"""
    now = datetime.now()
    # 意図的に48時間前のタイムスタンプを作成
    old_time = now.timestamp() - (48 * 3600) 
    old_time_str = datetime.fromtimestamp(old_time).strftime("%Y-%m-%d %H:%M:%S")

    dummy_data = {
        "system_last_updated": old_time_str,
        "currencies": {
            "USD": {
                "total_score": 100,
                "last_updated": old_time_str,
                "categories": {
                    "Monetary_Policy": {
                        "score": 100, # 初期スコア100点
                        "timestamp": old_time_str, # 48時間前
                        "latest_reason": "48時間前のFRBタカ派発言"
                    }
                }
            }
        }
    }
    with open(SCORE_FILE, 'w', encoding='utf-8') as f:
        json.dump(dummy_data, f, indent=2, ensure_ascii=False)
    print("📁 48時間前のダミーデータ(USD: 100点)を作成しました。\n")

# ==========================================
# 2. スコア減衰（ディケイ）ロジック
# あなたは世界トップクラスのマクロヘッジファンドのクオンツAI
# ==========================================
# カテゴリーごとの「24時間あたりの残存率」を定義
DECAY_RATES = {
    "Monetary_Policy": 0.9,  # 金融政策：長く効く
    "Economic_Data": 0.7,    # 経済指標：早めに忘れる
    "Geopolitics": 0.95,     # 地政学：解決までずっと怖い
    "Default": 0.8           # その他
}

def apply_time_decay():
    """カテゴリー別の減衰率を適用してスコアを計算する"""
    
    # (JSON読み込み等の処理は前回と同じ...)
    
    for currency, c_data in data["currencies"].items():
        new_total = 0
        
        for cat_name, cat_data in c_data["categories"].items():
            if cat_data["score"] == 0 or not cat_data["timestamp"]:
                continue
            
            # 1. カテゴリーに対応する減衰率を取得（なければDefault）
            rate = DECAY_RATES.get(cat_name, DECAY_RATES["Default"])
            
            # 2. 経過時間の計算
            last_time = datetime.strptime(cat_data["timestamp"], "%Y-%m-%d %H:%M:%S")
            elapsed_hours = (datetime.now() - last_time).total_seconds() / 3600
            
            # 3. カテゴリー別減衰ロジックの適用
            decay_factor = rate ** (elapsed_hours / 24)
            decayed_score = round(cat_data["score"] * decay_factor, 1)
            
            print(f"  [{currency} - {cat_name}] (率:{rate})")
            print(f"    経過: {elapsed_hours:.1f}h | {cat_data['score']} -> {decayed_score}")
            
            new_total += decayed_score

        print(f"  👉 {currency} の動的な Total Score: {new_total}\n")

# ==========================================
# 🧪 テスト実行
# ==========================================
if __name__ == "__main__":
    # 1. 48時間前のダミーJSONファイルを作る
    create_dummy_data()
    
    # 2. 減衰を計算して表示する
    apply_time_decay()