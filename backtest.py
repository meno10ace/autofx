import json
from datetime import datetime, timedelta
import os

# これまで作ったスコア更新ロジックを流用
# (簡略化のため、ここにロジックを凝縮します)

SCORE_FILE = "backtest_scores.json"

# --- 過去のニュースシナリオ（テストデータ） ---
past_news_events = [
    {"time": -72, "currency": "USD", "cat": "Monetary_Policy", "score": 80, "reason": "3日前：FRB議長がタカ派発言"},
    {"time": -48, "currency": "JPY", "cat": "Monetary_Policy", "score": -60, "reason": "2日前：日銀が緩和維持を決定"},
    {"time": -24, "currency": "USD", "cat": "Economic_Data", "score": -40, "reason": "1日前：米指標が予想を下振れ"},
    {"time": -12, "currency": "EUR", "cat": "Monetary_Policy", "score": 50, "reason": "12時間前：ECB利上げ示唆"},
]

def run_backtest():
    print("⏳ バックテスト・エミュレーションを開始します...")
    
    # スコアを初期化
    current_scores = {
        "system_last_updated": "",
        "currencies": {}
    }

    base_time = datetime.now()

    for event in past_news_events:
        # イベント発生時刻を計算
        event_time = base_time + timedelta(hours=event['time'])
        event_time_str = event_time.strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n📢 ニュース発生時刻: {event_time_str}")
        print(f"  [{event['currency']}] {event['reason']}")

        # 1. まず、全通貨に既存の「時間減衰」を適用（このイベントの直前まで）
        # ※本来はイベント間の秒数を計算して減衰させます

        # 2. 新しいスコアを上書き保存（保持）
        curr = event['currency']
        if curr not in current_scores["currencies"]:
            current_scores["currencies"][curr] = {"total_score": 0, "categories": {}}
        
        current_scores["currencies"][curr]["categories"][event['cat']] = {
            "score": event['score'],
            "timestamp": event_time_str,
            "latest_reason": event['reason']
        }
        
        # 3. 現在のTotal Scoreを再計算（最新の減衰を反映）
        # (ここで先ほどの apply_time_decay のロジックを呼ぶ)
        
        print(f"  ✅ スコア更新完了。JSONを保存しました。")

    # 最終結果をファイルに書き出す
    with open(SCORE_FILE, 'w', encoding='utf-8') as f:
        json.dump(current_scores, f, indent=2, ensure_ascii=False)

    print(f"\n🏁 バックテスト完了！ {SCORE_FILE} をダッシュボードで読み込んでください。")

if __name__ == "__main__":
    run_backtest()