import requests
import json
import time

# 先ほど取得したDiscordのWebhook URLをここに貼ります
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1485215442900615190/sPDauOLSc1eyqZsjnI4S1c-BH6cnjR16UXzoVadDBX80ixyaYgUdlaA9CajyDA8fQrLu"

def send_discord_alert(currency, score, category, phase, reason):
    """
    AIが弾き出したスコアをDiscordに綺麗に通知する関数
    (【修正】カテゴリーとフェーズを日本語に翻訳する機能を追加)
    """
    
    # --- 【修正点】英語名を日本語名に変換する辞書（マッピング） ---
    # AIが出力する想定の英語名と、表示したい日本語名をペアにします
    category_map = {
        "Monetary_Policy": "金融政策",
        "Economic_Data": "経済指標",
        "Geopolitics": "地政学",
        # 必要に応じてAIに判定させるカテゴリーを追加してください
    }
    
    phase_map = {
        "fact": "事実",
        "rumor": "思惑・観測"
    }

    # 日本語に変換（もし辞書になければ元の英語を表示する安全設計）
    category_ja = category_map.get(category, category)
    phase_ja = phase_map.get(phase, phase)
    
    # --- ここまで修正 ---

    # スコアによって通知の色とアイコンを変える（クオンツ仕様）
    if score >= 50:
        color = 0x00FF00  # 緑（強い買い）
        icon = "🟢 【爆買いシグナル】"
    elif score > 0:
        color = 0x00AA00  # 薄い緑（買い）
        icon = "↗️ 【買い優勢】"
    elif score <= -50:
        color = 0xFF0000  # 赤（強い売り）
        icon = "🔴 【暴落警戒シグナル】"
    elif score < 0:
        color = 0xAA0000  # 薄い赤（売り）
        icon = "↘️ 【売り優勢】"
    else:
        color = 0x808080  # グレー（中立）
        icon = "⚪ 【ニュートラル】"

    # Discordに送るリッチメッセージ（Embed）の組み立て
    payload = {
        "embeds": [
            {
                "title": f"{icon} {currency} ファンダメンタル急変",
                "color": color,
                "fields": [
                    {"name": "📊 スコア変動", "value": f"**{score} 点**", "inline": True},
                    # 【修正】日本語変換後の変数（_ja）を使用
                    {"name": "🏷️ カテゴリ", "value": f"`{category_ja}`", "inline": True},
                    {"name": "🔍 フェーズ", "value": f"`{phase_ja}`", "inline": True},
                    {"name": "💡 AIの分析理由", "value": reason, "inline": False}
                ],
                "footer": {"text": f"AI Fundamental Engine | {time.strftime('%Y-%m-%d %H:%M:%S')}"}
            }
        ]
    }

    # Discordへ送信！
    try:
        response = requests.post(
            DISCORD_WEBHOOK_URL,
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 204:
            print("✅ Discordへの通知（日本語化対応版）に成功しました！")
        else:
            print(f"❌ 通知失敗: {response.status_code}")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

# ==========================================
# 🧪 テスト実行（引数はAIが出力する想定の英語のまま）
# ==========================================
if __name__ == "__main__":
    
    print("通知テスト（日本語化対応版）を開始します...")
    
    # テスト1：強烈なドル買いのニュースが来た場合（カテゴリー：Monetary_Policy、フェーズ：fact）
    send_discord_alert(
        currency="USD",
        score=80,
        category="Monetary_Policy", # 英語のまま
        phase="fact", # 英語のまま
        reason="FRB議長が市場の予想を裏切り、年内の追加利上げを強く示唆しました。強烈なドル買いトレンドの初動となります。"
    )
    
    time.sleep(2) # 連続送信エラーを防ぐため少し待つ
    
    # テスト2：円売りの思惑ニュースが来た場合（カテゴリー：Monetary_Policy、フェーズ：rumor）
    send_discord_alert(
        currency="JPY",
        score=-60,
        category="Monetary_Policy", # 英語のまま
        phase="rumor", # 英語のまま
        reason="日銀関係者への取材により、次回の決定会合でのマイナス金利解除は見送られる公算が大きいとの観測が広がっています。"
    )