# create_db.py
from app import app, db, User, Event  # app.py から必要なものをインポート
from datetime import datetime

def create_sample_data():
    with app.app_context():
        # ユーザーを作成
        user = User.query.filter_by(username="sampleuser").first()
        if not user:
            user = User(username="sampleuser", password="password")
            db.session.add(user)
            db.session.commit()

        # サンプルイベントを複数作成
        sample_events = [
            Event(title="テクノロジーセミナー", description="最新テクノロジーについて学びます", location="東京", date=datetime(2024, 11, 15, 10, 00), category="テクノロジー", user_id=user.id, image_filename="1.jpg"),
            Event(title="ヨガクラス", description="初心者向けのヨガクラス", location="大阪", date=datetime(2024, 10, 28, 13, 00), category="ヘルス", user_id=user.id, image_filename="2.jpg"),
            Event(title="プログラミングワークショップ", description="Pythonを使ったプログラミング", location="東京", date=datetime(2024, 12, 5, 15, 00), category="テクノロジー", user_id=user.id, image_filename="3.jpg"),
            Event(title="写真展", description="プロの写真家による写真展", location="福岡", date=datetime(2024, 9, 20, 11, 00), category="アート", user_id=user.id, image_filename="4.jpg"),
            Event(title="料理教室", description="本格的なイタリア料理教室", location="名古屋", date=datetime(2024, 10, 10, 18, 00), category="フード", user_id=user.id, image_filename="5.jpg"),
            Event(title="音楽フェスティバル", description="様々なジャンルの音楽フェス", location="東京", date=datetime(2024, 12, 24, 12, 00), category="音楽", user_id=user.id, image_filename="6.jpg"),
            Event(title="マラソン大会", description="初心者から参加できるマラソン大会", location="大阪", date=datetime(2024, 11, 8, 9, 00), category="スポーツ", user_id=user.id, image_filename="7.jpg"),
            Event(title="映画鑑賞会", description="インディーズ映画の鑑賞会", location="東京", date=datetime(2024, 10, 5, 19, 00), category="エンタメ", user_id=user.id, image_filename="8.jpg"),
            Event(title="デザインワークショップ", description="デザインの基礎を学ぶワークショップ", location="京都", date=datetime(2024, 11, 22, 14, 00), category="アート", user_id=user.id, image_filename="9.jpg"),
            Event(title="ワインテイスティング", description="世界各国のワインテイスティング", location="東京", date=datetime(2024, 10, 18, 17, 00), category="フード", user_id=user.id, image_filename="10.jpg"),
            Event(title="アニメーション展示", description="人気アニメーションの展示", location="東京", date=datetime(2024, 9, 15, 10, 00), category="エンタメ", user_id=user.id, image_filename="11.jpg"),
            Event(title="バスケットボール大会", description="地域バスケットボール大会", location="大阪", date=datetime(2024, 11, 29, 13, 00), category="スポーツ", user_id=user.id, image_filename="12.jpg"),
            Event(title="ガーデニング教室", description="ガーデニング初心者向け", location="東京", date=datetime(2024, 12, 15, 14, 00), category="ヘルス", user_id=user.id, image_filename="13.jpg"),
            Event(title="サイエンスカンファレンス", description="最新の科学技術", location="福岡", date=datetime(2024, 10, 2, 10, 00), category="テクノロジー", user_id=user.id, image_filename="14.jpg"),
        ]

        for event in sample_events:
            existing_event = Event.query.filter_by(title=event.title).first()
            if not existing_event:
                db.session.add(event)
                db.session.commit()

def create_db():
    with app.app_context():
        db.create_all()
        create_sample_data()

if __name__ == "__main__":
    create_db()
