from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    display_name = db.Column(db.String(40), nullable=False)
    avatar = db.Column(db.String(200), default='default.svg')
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default='member')
    total_points = db.Column(db.Integer, default=0)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    posts = db.relationship('Post', backref='author', lazy='dynamic',
                             cascade='all, delete-orphan')
    checkins = db.relationship('CheckIn', backref='user', lazy='dynamic',
                                cascade='all, delete-orphan')
    learning_records = db.relationship('LearningRecord', backref='user', lazy='dynamic',
                                        cascade='all, delete-orphan')
    points_logs = db.relationship('PointsLog', backref='user', lazy='dynamic',
                                   cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def add_points(self, points, action, description=''):
        self.total_points += points
        log = PointsLog(user_id=self.id, action=action,
                        points=points, description=description)
        db.session.add(log)

    @property
    def today_checkins(self):
        today = date.today()
        return CheckIn.query.filter_by(user_id=self.id, date=today).count()

    @property
    def streak_days(self):
        """计算连续打卡天数"""
        checkin_dates = set()
        for c in self.checkins:
            checkin_dates.add(str(c.date))
        if not checkin_dates:
            return 0
        streak = 0
        from datetime import timedelta
        d = date.today()
        for _ in range(365):
            if str(d) in checkin_dates:
                streak += 1
                d -= timedelta(days=1)
            else:
                break
        return streak


class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(200))
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def time_ago(self):
        diff = datetime.utcnow() - self.created_at
        if diff.days > 0:
            return f'{diff.days}天前'
        if diff.seconds >= 3600:
            return f'{diff.seconds // 3600}小时前'
        if diff.seconds >= 60:
            return f'{diff.seconds // 60}分钟前'
        return '刚刚'


class CheckIn(db.Model):
    __tablename__ = 'checkin'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, default=date.today, nullable=False)
    photo_path = db.Column(db.String(200))
    description = db.Column(db.String(500))
    points = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'date', name='unique_user_date'),)


class KnowledgeArticle(db.Model):
    __tablename__ = 'knowledge_article'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.String(300))
    cover = db.Column(db.String(200))
    points = db.Column(db.Integer, default=5)
    read_count = db.Column(db.Integer, default=0)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    learning_records = db.relationship('LearningRecord', backref='article', lazy='dynamic',
                                        cascade='all, delete-orphan')


class LearningRecord(db.Model):
    __tablename__ = 'learning_record'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('knowledge_article.id'), nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'article_id', name='unique_user_article'),)


class PointsLog(db.Model):
    __tablename__ = 'points_log'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
