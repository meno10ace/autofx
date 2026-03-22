import feedparser
import chromadb
import time

# ==========================================
# 1. データベースの準備（保管庫）
# ==========================================
# メモリ上ではなく、フォルダにデータを永続化して保存するように設定
chroma_client = chromadb.PersistentClient(path="./news_db")
collection = chroma_client.get_or_create_collection(name="forex_news")

# ==========================================
# 2. RSSからニュースを取得（配管）
# ==========================================
RSS_URL = "https://www.forexlive.com/feed/news"

def fetch_and_filter_news():
    print(f"\n[{time.strftime('%H:%M:%S')}] 📡 RSSを取得中...")
    feed = feedparser.parse(RSS_URL)
    
    # 最新のものから処理したいのでリバース（逆順）にする等はお好みで
    for entry in feed.entries:
        news_id = entry.id if hasattr(entry, 'id') else entry.link
        title = entry.title
        summary = entry.description if hasattr(entry, 'description') else ""
        full_text = f"【{title}】 {summary}"
        
        # ==========================================
        # 3. ChromaDBで新規性チェック
        # ==========================================
        # データベースに1件以上データがある場合のみ類似度チェック
        if collection.count() > 0:
            results = collection.query(
                query_texts=[full_text],
                n_results=1
            )
            
            # 距離(distance)が小さいほど似ている。0.2以下なら「ほぼ同じ」とみなす
            distance = results['distances'][0][0] if results['distances'][0] else 1.0
            
            if distance < 0.2:
                # print(f"⏭️ スキップ (既出): {title[:30]}...") # ログがうるさい場合はコメントアウト
                continue
        
        # ==========================================
        # 4. 新規ニュースを発見！DBに保存
        # ==========================================
        print(f"🌟 新規ニュース発見！: {title}")
        
        # ここでChromaDBに保存（add）する！
        collection.add(
            documents=[full_text],
            metadatas=[{"title": title}],
            ids=[news_id]
        )
        
        # ⬇️ 本来はここで Gemini API にフルテキストを投げて JSON を作らせる
        # analyze_with_gemini(full_text)

    print(f"📦 現在ChromaDBに記憶されているニュース総数: {collection.count()}件")

# ==========================================
# 実行
# ==========================================
if __name__ == "__main__":
    fetch_and_filter_news()