from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from werkzeug.utils import secure_filename # 追加

# アプリケーションの作成
app = Flask(__name__)
app.config['SECRET_KEY'] = 'simple_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 画像の保存先ディレクトリを設定
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# ディレクトリが存在しない場合に作成
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# 許可される拡張子を設定
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# データベースの初期化
db = SQLAlchemy(app)

# モデルの定義
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    events = db.relationship('Event', backref='creator', lazy=True)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_filename = db.Column(db.String(255), nullable=True) # 画像ファイル名を追加
    comments = db.relationship('Comment', backref='event', lazy=True)
    participants = db.relationship('Participant', backref='event', lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user = db.relationship('User', backref='comments')

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user = db.relationship('User', backref='participations')

# 画像の拡張子が正しいかをチェックする関数
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 路由：ホーム
@app.route('/')
def index():
    events = Event.query.order_by(Event.date).all()
    return render_template('index.html', events=events)

# 路由：注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('用户名已存在！')
            return redirect(url_for('register'))
        
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('登録完了、ログインしてください！')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# 路由：登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            session['user_id'] = user.id
            session['username'] = user.username
            flash('ログインに成功しました！')
            return redirect(url_for('index'))
        else:
            flash('ユーザー名またはパスワードが正しくありません！')
    
    return render_template('login.html')

# 路由：登出
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('ログアウトしました！')
    return redirect(url_for('index'))

# 路由：画像の表示
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 路由：作成活动
@app.route('/create_event', methods=['GET', 'POST'])
def create_event():
    if 'user_id' not in session:
        flash('ログインしてください！')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        location = request.form['location']
        date_str = request.form['date']
        category = request.form['category']
        date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')

        # 画像ファイルの処理
        image_filename = None
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '' and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image_filename = filename  # 画像ファイル名を保存
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            elif image.filename == '':
                flash('画像が選択されていません。')
                return render_template('create_event.html')
            else:
                flash('許可されていない拡張子の画像ファイルです。')
                return render_template('create_event.html')

        new_event = Event(
            title=title,
            description=description,
            location=location,
            date=date,
            category=category,
            user_id=session['user_id'],  # ユーザーIDをセット
            image_filename=image_filename
        )

        db.session.add(new_event)
        db.session.commit()

        flash('イベントの作成に成功しました！')
        return redirect(url_for('index'))

    return render_template('create_event.html')

# 路由：活动详情
@app.route('/event/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    comments = Comment.query.filter_by(event_id=event_id).all()
    
    # 检查当前用户是否已参与
    is_participant = False
    if 'user_id' in session:
        participant = Participant.query.filter_by(event_id=event_id, user_id=session['user_id']).first()
        is_participant = participant is not None
    
    participants = Participant.query.filter_by(event_id=event_id).all()
    participant_count = len(participants)
    
    return render_template('event_detail.html', 
                          event=event, 
                          comments=comments, 
                          is_participant=is_participant,
                          participant_count=participant_count)

# 路由：添加评论
@app.route('/add_comment/<int:event_id>', methods=['POST'])
def add_comment(event_id):
    if 'user_id' not in session:
        flash('ログインしてください！')
        return redirect(url_for('login'))
    
    content = request.form['content']
    
    new_comment = Comment(
        content=content,
        user_id=session['user_id'],
        event_id=event_id
    )
    
    db.session.add(new_comment)
    db.session.commit()
    
    flash('コメントを投稿しました！')
    return redirect(url_for('event_detail', event_id=event_id))

# 路由：参加活动
@app.route('/join_event/<int:event_id>')
def join_event(event_id):
    if 'user_id' not in session:
        flash('ログインしてください！')
        return redirect(url_for('login'))
    
    # 检查是否已经参加
    existing = Participant.query.filter_by(event_id=event_id, user_id=session['user_id']).first()
    if existing:
        flash('すでに参加しています！')
        return redirect(url_for('event_detail', event_id=event_id))
    
    new_participant = Participant(
        user_id=session['user_id'],
        event_id=event_id
    )
    
    db.session.add(new_participant)
    db.session.commit()
    
    flash('参加しました！')
    return redirect(url_for('event_detail', event_id=event_id))

# 路由：退出活动
@app.route('/leave_event/<int:event_id>')
def leave_event(event_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    participant = Participant.query.filter_by(event_id=event_id, user_id=session['user_id']).first()
    
    if participant:
        db.session.delete(participant)
        db.session.commit()
        flash('退出しました！')
    
    return redirect(url_for('event_detail', event_id=event_id))

# 路由：搜索活动
@app.route('/search')
def search():
    query = request.args.get('query', '')
    date_sort = request.args.get('date_sort', '')
    location_filter = request.args.get('location_filter', '')
    category_filter = request.args.get('category_filter', '')

    # 全てのカテゴリーを取得
    categories = [category[0] for category in db.session.query(Event.category).distinct().all()]
    
    # ベースとなるクエリを準備
    base_query = Event.query
    
    # 検索キーワードによるフィルタリング
    if query:
        base_query = base_query.filter(
            (Event.title.contains(query)) | 
            (Event.description.contains(query)) |
            (Event.location.contains(query)) |
            (Event.category.contains(query))
        )

    # 場所によるフィルタリング
    if location_filter:
        base_query = base_query.filter(Event.location.contains(location_filter))

    # カテゴリによるフィルタリング
    if category_filter:
        base_query = base_query.filter(Event.category == category_filter)

    # 日時によるソート
    if date_sort == 'asc':
        base_query = base_query.order_by(Event.date.asc())
    elif date_sort == 'desc':
        base_query = base_query.order_by(Event.date.desc())

    # 最終的なクエリを実行
    events = base_query.all()

    return render_template(
        'search.html',
        events=events,
        query=query,
        date_sort=date_sort,
        location_filter=location_filter,
        category_filter=category_filter,
        categories = categories
    )

# 実行処理
if __name__ == '__main__':
    app.run(debug=True)
