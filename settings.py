from sqlalchemy import create_engine

# PostgreSQLの接続情報
path = 'postgresql+psycopg2://postgres:passwd@localhost:5433/sauna_db'

# エンジンの作成（データベースに接続するためのエンジン）
Engine = create_engine(
    path,  # 接続するデータベースのURL
    # encoding="utf-8",  # 文字エンコーディング
    echo=False  # SQLの実行内容を表示しない
)

