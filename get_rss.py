import feedparser
import time

# ==========================================
# 1. 監視するRSSフィードのURLリスト
# ==========================================
RSS_URLS = [
    "https://www.forexlive.com/feed/news",  # ForexLiveの総合ニュース
    # 必要に応じて他のRSS（Investing.com等）も追加可能
]

# 既に取得したニュースのIDを保存しておくリスト（二重取得防止用）
# ※本来はSQLite等に保存しますが、今回はメモリ上で管理
seen_article_ids = set()

# ==========================================
# 2. RSS取得関数
# ==========================================
def fetch_latest_news():
    print(f"\n[{time.strftime('%H:%M:%S')}] 📡 RSSフィードを巡回中...")
    
    new_articles = []
    
    for url in RSS_URLS:
        feed = feedparser.parse(url)
        
        # 最新の記事から順番に確認
        for entry in feed.entries:
            article_id = entry.id if hasattr(entry, 'id') else entry.link
            
            # まだ処理していない新しい記事ならリストに追加
            if article_id not in seen_article_ids:
                seen_article_ids.add(article_id)
                
                # タイトルと概要（description）を結合して1つのテキストにする
                title = entry.title
                summary = entry.description if hasattr(entry, 'description') else ""
                
                # HTMLタグが混ざっている場合は除去する処理を入れると更に良し
                full_text = f"【{title}】 {summary}"
                new_articles.append({"id": article_id, "text": full_text})
                
    return new_articles

# ==========================================
# 🧪 連携テスト（先ほどのChromaDB処理と繋げるイメージ）
# ==========================================

if __name__ == "__main__":
    # 最初の1回目は、過去の記事がドバッと取れてしまうのでスルーするか、
    # 最初の数件だけをテスト処理します。
    articles = fetch_latest_news()
    
    if articles:
        print(f"✨ {len(articles)}件の新しいニュースを発見しました！\n")
        
        # テストとして最新の1件だけを表示・処理してみる
        latest = articles[0]
        print(f"📝 取得テキスト:\n{latest['text']}\n")
        
        # ⬇️ ここで前回作った process_news(latest['id'], latest['text']) を呼び出す！
        # process_news(latest['id'], latest['text'])
        
    else:
        print("新しいニュースはありませんでした。")