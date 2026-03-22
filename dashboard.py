import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
import os
from datetime import datetime

# カテゴリー名の翻訳マップ
CAT_JAPANESE = {
    "Monetary_Policy": "金融政策",
    "Economic_Data": "経済指標",
    "Geopolitics": "地政学"
}

# ==========================================
# 1. ページ設定（クオンツ・デスク仕様）
# ==========================================
st.set_page_config(
    page_title="AI Fundamental Dashboard",
    page_icon="📈",
    layout="wide", # 画面を横いっぱいに使う
    initial_sidebar_state="collapsed" # サイドバーは初期状態で閉じる
)

# タイトル
st.title("🧮 AIファンダメンタル・センチメント・ダッシュボード")
st.markdown("---")

SCORE_FILE = "backtest_scores.json"

# --- 【テスト用】リッチなJSONデータ（image_0.pngの内容準拠）を作成する関数 ---
def create_dummy_data_from_signal():
    if os.path.exists(SCORE_FILE):
        return # 既にファイルがあれば作成しない
    
    # image_0.pngのデータをダミーデータ化
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dummy_data = {
        "system_last_updated": now,
        "currencies": {
            "USD": {
                "total_score": 80.0,
                "last_updated": "2026-03-22 18:56:40",
                "color": "green", # image_0.pngの🟢
                "categories": {
                    "金融政策": {"score": 80, "timestamp": now, "momentum": "high", "phase": "facts", "latest_reason": "FRB議長が市場の予想を裏切り、年内の追加利上げを強く示唆しました。強烈なドル買いトレンドの初動となります。"},
                    "経済指標": {"score": 0, "timestamp": now, "momentum": "neutral", "phase": "", "latest_reason": ""}
                }
            },
            "JPY": {
                "total_score": -60.0,
                "last_updated": "2026-03-22 18:56:42",
                "color": "red", # image_0.pngの🔴
                "categories": {
                    "金融政策": {"score": -60.0, "timestamp": now, "momentum": "high", "phase": "rumor", "latest_reason": "日銀関係者への取材により、次回の決定会合でのマイナス金利解除は見送られる公算が大きいとの観測が広がっています。"}
                }
            },
            "EUR": { # その他テスト用通貨
                "total_score": 25.0,
                "last_updated": now,
                "color": "lightgreen",
                "categories": {
                    "金融政策": {"score": 30.0, "timestamp": now, "momentum": "high", "phase": "facts", "latest_reason": "ECB理事によるタカ派発言"},
                    "経済指標": {"score": -5.0, "timestamp": now, "momentum": "low", "phase": "rumor", "latest_reason": "ユーロ圏PMIが予想を下回る"}
                }
            },
            "GBP": { # その他テスト用通貨
                "total_score": -10.0,
                "last_updated": now,
                "color": "lightcoral",
                "categories": {
                    "金融政策": {"score": -10.0, "timestamp": now, "momentum": "high", "phase": "facts", "latest_reason": "英中銀政策決定。"}
                }
            }
        }
    }
    with open(SCORE_FILE, 'w', encoding='utf-8') as f:
        json.dump(dummy_data, f, indent=2, ensure_ascii=False)
    st.success("📝 テスト用のリッチなJSONデータを作成しました。")

# ==========================================
# 2. データの読み込み
# ==========================================
# テストデータの作成
create_dummy_data_from_signal()

# JSON読み込み関数（キャッシュして高速化）
@st.cache_data(ttl=10) # 10秒間はキャッシュを使う
def load_score_data():
    if not os.path.exists(SCORE_FILE):
        return None
    with open(SCORE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

data = load_score_data()

# ==========================================
# 3. ダッシュボード配置（レイアウト）
# ==========================================

if data:
    # --- Row 1: 通貨強弱ランキング (ユーザー要求:テキストで) ---
    st.header("🏆 通貨強弱ランキング (Total Score)")
    st.sidebar.markdown(f"**最終更新:**\n{data['system_last_updated']}")

    ranking_list = []
    for currency, c_data in data["currencies"].items():
        ranking_list.append({
            "Currency": currency,
            "Total Score": c_data["total_score"],
            "ColorIcon": "🟢" if c_data["total_score"] > 0 else "🔴" if c_data["total_score"] < 0 else "⚪"
        })

    df_ranking = pd.DataFrame(ranking_list).sort_values(by="Total Score", ascending=False)
    
    # テキストでランキングを表示
    # 最も確実なループの書き方
    # テキストでランキングを表示
    # 最も確実なループの書き方
    ranking_text = ""
    for i, (index, row) in enumerate(df_ranking.iterrows()):
        ranking_text += f"{i+1}. {row['Currency']} ({row['Total Score']}) {row['ColorIcon']}  "
    st.text(ranking_text)

    st.markdown("---")

    # --- Row 2: 通貨別センチメント・カード (image_1.pngのイメージ) ---
    st.header("🔍 通貨別センチメント・カード")
    
    # 通貨名をリスト化し、横並びに配置（画面端で換行）
    currencies = list(data["currencies"].keys())
    # 1行に表示するカード数
    columns_per_row = 3
    
    for i in range(0, len(currencies), columns_per_row):
        cols = st.columns(columns_per_row)
        for j in range(columns_per_row):
            if i + j < len(currencies):
                currency = currencies[i + j]
                c_data = data["currencies"][currency]
                
                with cols[j]:
                    # カード形式のコンテナ
                    with st.container(border=True):
                        # 通貨名
                        st.subheader(currency)
                        
                        # トータルスコア 円グラフ (image_1.pngのdonut chart)
                        # ストリームリットの標準機能で「donut chart」を作るのは複雑なため、
                        # st.metricと色付けされた丸い枠で草図のイメージを再現
                        
                        col_chart_l, col_chart_c, col_chart_r = st.columns([1, 4, 1])
                        with col_chart_l: st.write("-")
                        with col_chart_c:
                            # 简化円グラフ：スコアに応じて色を変えるカスタムHTML丸枠
                            color = "green" if c_data["total_score"] > 0 else "red" if c_data["total_score"] < 0 else "grey"
                            
                            # 円グラフ内のスコア表示
                            st.markdown(f'<div style="text-align: center; border: 3px solid {color}; border-radius: 50%; width: 70px; height: 70px; line-height: 64px; font-size: 28px; font-weight: bold; margin: 0 auto;">{c_data["total_score"]}</div>', unsafe_allow_html=True)
                            st.metric(label="トータルスコア", value="", help="全カテゴリの合計スコア。")
                        with col_chart_r: st.write("+")
                        
                        # カテゴリーと点数 (image_1.pngのリスト形式)
                        st.write("**カテゴリー別スコア**")
                        # 縦長のデータを横長の表にするための加工
                        df_details = pd.DataFrame.from_dict(c_data["categories"], orient='index').reset_index()
                        df_details = df_details[["index", "score"]].set_index("index").T
                        df_details.index = [c_data["total_score"]] # インデックスをトータルスコアにする (横長のリストに見せるため)
                        # カテゴリー名の翻訳を適用した新しい辞書を作成
                        translated_categories = {CAT_JAPANESE.get(k, k): v["score"] for k, v in c_data["categories"].items()}
                        df_details = pd.DataFrame([translated_categories])
                        st.dataframe(df_details, hide_index=True)
                        
                        # 最新のニュース (image_1.pngのテキスト)
                        st.write("**最新の理由**")
                        # カテゴリーを問わず、最も新しい理由を表示
                        latest_cat = max(c_data["categories"], key=lambda k: c_data["categories"][k]["timestamp"] or "")
                        latest_reason = c_data["categories"][latest_cat]["latest_reason"]
                        st.write(latest_reason if latest_reason else "理由はありません。")

                        # クリックしたら詳細画面へ (image_1.pngの要求)
                        # ストリームリットでは「カードをクリック」を直接検知するのが難しいため、
                        # カード下部に専用の詳細表示ボタンを設置し、セッション状態を管理します。
                        if st.button(f"{currency} 詳細表示", key=f"btn_{currency}", type="secondary"):
                            st.session_state.selected_currency = currency
                            st.rerun()

    # --- Row 3: 詳細分析画面 (image_1.pngのクリック後に表示される画面) ---
    if 'selected_currency' in st.session_state and st.session_state.selected_currency:
        st.markdown("---")
        selected_currency = st.session_state.selected_currency
        currency_data = data["currencies"][selected_currency]
        
        st.header(f"📊 {selected_currency} 詳細分析画面")
        
        # 左右のレイアウト
        col_detail_l, col_detail_r = st.columns([1, 2])
        with col_detail_l:
            # カテゴリー別の内訳を雷達図（レーダーチャート）で表示
            # カテゴリー名を日本語に変換してからリスト化
            categories_en = list(currency_data["categories"].keys())
            categories_ja = [CAT_JAPANESE.get(cat, cat) for cat in categories_en] # 日本語に変換
            scores = [currency_data["categories"][cat]["score"] for cat in categories_en]

            fig_radar = go.Figure(data=go.Scatterpolar(
                r=scores,
                theta=categories_ja, # 日本語の軸名を使用
                fill='toself'
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[-100, 100] # スコア範囲を固定
                    )
                ),
                showlegend=False
            )
            st.plotly_chart(fig_radar, use_container_width=True)
            
        with col_detail_r:
            # 完整の最新理由
            st.subheader("💡 完整分析理由フィード")
            # 最新の理由をソートして表示
            cat_list = sorted(currency_data["categories"].items(), key=lambda x: x[1]["timestamp"] or "", reverse=True)
            for cat_name, cat_data in cat_list:
                if cat_data["latest_reason"]:
                    icon = "🟢" if cat_data["score"] > 0 else "🔴" if cat_data["score"] < 0 else "⚪"
                    # カテゴリー名を日本語で表示
                    cat_name_ja = CAT_JAPANESE.get(cat_name, cat_name)
                    st.markdown(f"{icon} **【{cat_name_ja}】** スコア: {cat_data['score']} | {cat_data['timestamp']}")
                    st.markdown(f"  {cat_data['latest_reason']}")
                    st.markdown("---")
                    
        # 詳細画面を閉じるボタン
        if st.button("详细画面を閉じる"):
            st.session_state.selected_currency = None
            st.rerun()

else:
    st.error(f"❌ {SCORE_FILE} が見つかりません。バックエンドシステムを稼働させるか、テストデータを生成してください。")