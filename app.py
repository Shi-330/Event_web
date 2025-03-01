from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# アプリケーションの作成
app = Flask(__name__)
app.config['SECRET_KEY'] = 'simple_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

# ルート：ホーム
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
        
        flash('注册成功，请登录！')
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
            flash('登录成功！')
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误！')
    
    return render_template('login.html')

# 路由：登出
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('您已退出登录！')
    return redirect(url_for('index'))

# 路由：创建活动
@app.route('/create_event', methods=['GET', 'POST'])
def create_event():
    if 'user_id' not in session:
        flash('请先登录！')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        location = request.form['location']
        date_str = request.form['date']
        category = request.form['category']
        
        # 简单的日期格式转换
        date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        
        new_event = Event(
            title=title,
            description=description,
            location=location,
            date=date,
            category=category,
            user_id=session['user_id']
        )
        
        db.session.add(new_event)
        db.session.commit()
        
        flash('活动创建成功！')
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
        flash('请先登录！')
        return redirect(url_for('login'))
    
    content = request.form['content']
    
    new_comment = Comment(
        content=content,
        user_id=session['user_id'],
        event_id=event_id
    )
    
    db.session.add(new_comment)
    db.session.commit()
    
    flash('评论发布成功！')
    return redirect(url_for('event_detail', event_id=event_id))

# 路由：参加活动
@app.route('/join_event/<int:event_id>')
def join_event(event_id):
    if 'user_id' not in session:
        flash('请先登录！')
        return redirect(url_for('login'))
    
    # 检查是否已经参加
    existing = Participant.query.filter_by(event_id=event_id, user_id=session['user_id']).first()
    if existing:
        flash('您已经参加了这个活动！')
        return redirect(url_for('event_detail', event_id=event_id))
    
    new_participant = Participant(
        user_id=session['user_id'],
        event_id=event_id
    )
    
    db.session.add(new_participant)
    db.session.commit()
    
    flash('成功参加活动！')
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
        flash('您已退出该活动！')
    
    return redirect(url_for('event_detail', event_id=event_id))

# 路由：搜索活动
@app.route('/search')
def search():
    query = request.args.get('query', '')
    
    if query:
        events = Event.query.filter(
            (Event.title.contains(query)) | 
            (Event.description.contains(query)) |
            (Event.location.contains(query)) |
            (Event.category.contains(query))
        ).all()
    else:
        events = Event.query.all()
    
    return render_template('search.html', events=events, query=query)

# 初始化数据库
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)