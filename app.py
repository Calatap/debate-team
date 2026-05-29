import os
import uuid
from datetime import date, datetime

from flask import (Flask, render_template, redirect, url_for, request,
                   flash, jsonify, send_from_directory, abort)
from flask_login import (LoginManager, login_user, logout_user,
                         login_required, current_user)
from markupsafe import escape
from werkzeug.utils import secure_filename

from models import db, User, Post, CheckIn, KnowledgeArticle, LearningRecord, PointsLog

# ===== 配置 =====
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'mp4'}

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'debate-team-secret-key-2025')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'debate.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 7

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = '请先登录'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ===== 管理员默认密码 =====
ADMIN_PASSWORD = 'admin123'


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}


@app.template_filter('nl2br')
def nl2br_filter(text):
    if not text:
        return ''
    from markupsafe import Markup
    return Markup(escape(text).replace('\n', '<br>\n'))


# ===== 初始化数据库并填充知识库 =====
def init_db():
    db.create_all()
    if KnowledgeArticle.query.count() == 0:
        articles = [
            {
                'title': '辩论基础：立论与驳论',
                'category': '入门',
                'summary': '学习辩论中最核心的立论和驳论技巧',
                'content': '''## 立论

立论是一场比赛的开场陈词，决定了你的论证框架。

### 立论的要素
1. **定义** — 对辩题中的关键概念进行界定
2. **标准** — 评判辩题的标准是什么
3. **论点** — 支撑你方立场的2-3个核心论点

### 立论的技巧
- 定义要清晰但留有弹性
- 标准要对自己有利
- 论点之间要有逻辑递进

## 驳论

驳论是反驳对方论点的环节。

### 驳论的步骤
1. **倾听** — 准确理解对方的论点
2. **拆解** — 找出对方论证中的漏洞
3. **反驳** — 用事实和逻辑进行回击

### 常见的逻辑谬误
- 偷换概念
- 以偏概全
- 滑坡谬误
- 人身攻击''',
                'points': 10
            },
            {
                'title': '辩论中的逻辑思维',
                'category': '进阶',
                'summary': '掌握辩论中常用的逻辑推理方法',
                'content': '''## 演绎推理

### 三段论
大前提 → 小前提 → 结论

例：
- 大前提：所有人类都会死
- 小前提：苏格拉底是人
- 结论：苏格拉底会死

## 归纳推理

从特殊到一般的推理过程。

## 类比推理

通过两件事物的相似性进行推理。

### 辩论中常用的逻辑模型
1. **ARE模型** — Assertion（主张）、Reasoning（推理）、Evidence（证据）
2. **Toulmin模型** — Claim（主张）、Data（数据）、Warrant（理由）

## 常见逻辑陷阱
- 虚假两难
- 循环论证
- 诉诸权威
- 诉诸情感''',
                'points': 15
            },
            {
                'title': '辩论赛制详解',
                'category': '入门',
                'summary': '华语辩论的主流赛制及规则',
                'content': '''## 华语辩论主流赛制

### 新国辩赛制（4v4）
1. 立论环节：正方一辩 → 反方一辩（各3分钟）
2. 质询环节：反方四辩质询正方一辩 → 正方四辩质询反方一辩（各1分30秒）
3. 驳论环节：正方二辩 → 反方二辩（各2分钟）
4. 质询环节：反方三辩质询正方二辩 → 正方三辩质询反方二辩（各1分30秒）
5. 自由辩论：交替发言（各4分钟）
6. 总结环节：反方三辩 → 正方三辩（各3分钟）

### 辩论礼仪
1. 发言时需起立
2. 质询时被质询方需回答
3. 不得人身攻击
4. 尊重主席和评委''',
                'points': 5
            },
            {
                'title': '如何准备辩论赛',
                'category': '实战',
                'summary': '赛前准备的完整流程和方法',
                'content': '''## 赛前准备六步法

### 第一步：破题
- 拆解辩题中的每个关键词
- 找出双方的争议焦点
- 确定己方的立场和底线

### 第二步：查资料
- 查找相关数据统计
- 搜集权威专家的观点
- 找典型案例和事例

### 第三步：建立论点框架
- 确定2-3个核心论点
- 每个论点配好论据
- 准备可能的攻防

### 第四步：模拟攻防
- 预测对方可能的论点
- 准备反驳方案
- 多次模拟自由辩论

### 第五步：写辩稿
- 一辩：立论稿
- 二辩：驳论稿
- 三辩：总结稿

### 第六步：心理准备
- 调整心态
- 团队配合默契
- 关键时刻的战术''',
                'points': 15
            },
            {
                'title': '价值辩论技巧',
                'category': '进阶',
                'summary': '如何在价值辩论中占据道德高地',
                'content': '''## 什么是价值辩论

价值辩论关注的是"应该"的问题，而非"是不是"的问题。

### 价值辩论的核心
1. **价值倡导** — 你倡导什么样的价值观
2. **利益权衡** — 不同价值之间的取舍
3. **情景构建** — 在具体情境中讨论价值

### 常见价值框架
- 自由 vs 安全
- 效率 vs 公平
- 个人权利 vs 集体利益

### 价值辩论的技巧
1. **升华** — 将具体问题提升到价值层面
2. **共情** — 用故事和情感打动评委
3. **比较** — 说明己方价值优于对方价值
4. **底线** — 守住不可退让的价值底线

### 经典价值辩论案例
- 应不应该废除死刑
- 应不应该允许代孕
- 人性本善还是本恶''',
                'points': 20
            },
            {
                'title': '自由辩论的攻防策略',
                'category': '实战',
                'summary': '自由辩论阶段的战术技巧和实战经验',
                'content': '''## 自由辩论的核心原则

### 1. 打点不打面
集中攻击对方最薄弱的论点，不要漫无目的地发散。

### 2. 追问到底
对一个问题连续追问，直到对方露出破绽。

### 3. 主动推进
不要总是被动回应，要学会主动抛出问题。

### 常用战术

**追击型**
- 抓住对方的逻辑漏洞连续轰炸
- 用连环问题迫使对方自相矛盾

**防守型**
- 用事实和数据构筑防线
- 巧妙回避不利问题

**陷阱型**
- 预设问题引导对方进入不利境地
- 用二难推理限制对方选择

### 时间管理
- 留出时间给队友补充
- 最后30秒做总结提升''',
                'points': 15
            },
        ]
        for art in articles:
            article = KnowledgeArticle(
                title=art['title'],
                category=art['category'],
                content=art['content'],
                summary=art['summary'],
                points=art['points'],
                created_by=1
            )
            db.session.add(article)
        db.session.commit()


# ===== 首页 / 动态 =====
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('feed'))
    return redirect(url_for('login'))


# ===== 认证 =====
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('feed'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=True)
            flash('登录成功！', 'success')
            return redirect(url_for('feed'))
        flash('用户名或密码错误', 'danger')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('feed'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')
        display_name = request.form.get('display_name', '').strip() or username

        if not username or not password:
            flash('用户名和密码不能为空', 'danger')
            return render_template('register.html')
        if password != confirm:
            flash('两次密码不一致', 'danger')
            return render_template('register.html')
        if len(username) < 2 or len(username) > 20:
            flash('用户名长度应为2-20个字符', 'danger')
            return render_template('register.html')
        if len(password) < 4:
            flash('密码至少4位', 'danger')
            return render_template('register.html')
        if User.query.filter_by(username=username).first():
            flash('用户名已被注册', 'danger')
            return render_template('register.html')

        user = User(username=username, display_name=display_name)
        user.set_password(password)

        # 第一个注册用户自动成为管理员
        if User.query.count() == 0:
            user.role = 'admin'

        db.session.add(user)
        db.session.commit()
        login_user(user, remember=True)
        flash(f'欢迎加入辩论队，{display_name}！', 'success')
        return redirect(url_for('feed'))
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已退出登录', 'info')
    return redirect(url_for('login'))


# ===== 动态列表 =====
@app.route('/feed')
@login_required
def feed():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    return render_template('feed.html', posts=posts)


@app.route('/post/create', methods=['POST'])
@login_required
def create_post():
    content = request.form.get('content', '').strip()
    if not content:
        flash('说点什么吧', 'danger')
        return redirect(url_for('feed'))

    image_path = None
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f'post_{uuid.uuid4().hex}.{ext}'
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            image_path = filename

    post = Post(user_id=current_user.id, content=content, image_path=image_path)
    db.session.add(post)

    points_earned = 2
    current_user.add_points(points_earned, 'post', '发布动态')
    db.session.commit()
    flash(f'发布成功 +{points_earned}分', 'success')
    return redirect(url_for('feed') + '#new-post')


@app.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.likes += 1
    db.session.commit()
    return jsonify({'likes': post.likes})


# ===== 打卡 =====
@app.route('/checkin', methods=['GET', 'POST'])
@login_required
def checkin():
    if request.method == 'POST':
        desc = request.form.get('description', '').strip()
        today = date.today()

        existing = CheckIn.query.filter_by(
            user_id=current_user.id, date=today).first()
        if existing:
            flash('今天已经打过卡了！', 'warning')
            return redirect(url_for('checkin'))

        photo_path = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f'checkin_{uuid.uuid4().hex}.{ext}'
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                photo_path = filename

        bonus = 2 if current_user.streak_days >= 3 else 0
        points = 10 + bonus

        checkin = CheckIn(
            user_id=current_user.id, date=today,
            photo_path=photo_path, description=desc,
            points=points
        )
        db.session.add(checkin)
        current_user.add_points(points, 'checkin', f'每日打卡{bonus > 0 and "（连续奖励）" or ""}')
        db.session.commit()

        flash(f'打卡成功！+{points}分{bonus > 0 and "（含连续打卡奖励+2）" or ""}', 'success')
        return redirect(url_for('checkin'))

    today = date.today()
    today_checkin = CheckIn.query.filter_by(
        user_id=current_user.id, date=today).first()

    # 最近打卡记录
    recent_checkins = CheckIn.query.filter(
        CheckIn.user_id == current_user.id
    ).order_by(CheckIn.date.desc()).limit(30).all()

    return render_template('checkin.html',
                           today_checkin=today_checkin,
                           recent_checkins=recent_checkins)


# ===== 排行榜 =====
@app.route('/leaderboard')
@login_required
def leaderboard():
    users = User.query.order_by(User.total_points.desc()).all()
    rank = 1
    for u in users:
        u.rank = rank
        rank += 1
    return render_template('leaderboard.html', users=users)


# ===== 知识库 =====
@app.route('/knowledge')
@login_required
def knowledge():
    category = request.args.get('category', '')
    query = KnowledgeArticle.query
    if category:
        query = query.filter_by(category=category)
    articles = query.order_by(KnowledgeArticle.created_at.desc()).all()

    # 标记用户已学过的
    learned_ids = set()
    for r in current_user.learning_records:
        learned_ids.add(r.article_id)

    categories = db.session.query(
        KnowledgeArticle.category
    ).distinct().all()
    categories = [c[0] for c in categories]

    return render_template('knowledge.html',
                           articles=articles,
                           learned_ids=learned_ids,
                           categories=categories,
                           current_category=category)


@app.route('/knowledge/<int:article_id>')
@login_required
def knowledge_detail(article_id):
    article = KnowledgeArticle.query.get_or_404(article_id)
    learned = LearningRecord.query.filter_by(
        user_id=current_user.id, article_id=article_id).first()
    return render_template('knowledge_detail.html',
                           article=article, learned=learned)


@app.route('/knowledge/<int:article_id>/learn', methods=['POST'])
@login_required
def learn_article(article_id):
    article = KnowledgeArticle.query.get_or_404(article_id)
    existing = LearningRecord.query.filter_by(
        user_id=current_user.id, article_id=article_id).first()
    if existing:
        return jsonify({'status': 'already', 'msg': '已学习过'})

    record = LearningRecord(user_id=current_user.id, article_id=article_id)
    db.session.add(record)
    article.read_count += 1
    current_user.add_points(article.points, 'learn', f'学习文章：{article.title}')
    db.session.commit()
    return jsonify({'status': 'ok', 'points': article.points,
                    'msg': f'学习完成 +{article.points}分'})


# ===== 管理员：新建知识 =====
@app.route('/admin/knowledge/create', methods=['GET', 'POST'])
@login_required
def admin_create_knowledge():
    if current_user.role != 'admin':
        abort(403)
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        summary = request.form.get('summary', '').strip()
        content = request.form.get('content', '').strip()
        points = request.form.get('points', 5, type=int)

        if not title or not content:
            flash('标题和内容不能为空', 'danger')
            return render_template('admin_create_knowledge.html')

        article = KnowledgeArticle(
            title=title, category=category, summary=summary,
            content=content, points=points, created_by=current_user.id
        )
        db.session.add(article)
        db.session.commit()
        flash('知识文章创建成功！', 'success')
        return redirect(url_for('knowledge'))
    return render_template('admin_create_knowledge.html')


# ===== 个人主页 =====
@app.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.limit(20).all()
    checkin_count = user.checkins.count()
    learn_count = user.learning_records.count()
    return render_template('profile.html',
                           user=user, posts=posts,
                           checkin_count=checkin_count,
                           learn_count=learn_count)


@app.route('/profile')
@login_required
def my_profile():
    return redirect(url_for('profile', username=current_user.username))


# ===== 上传文件访问 =====
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# ===== 启动 =====
if __name__ == '__main__':
    with app.app_context():
        init_db()
    port = int(os.environ.get('PORT', 5000))
    print('=' * 50)
    print('辩论队管理系统已启动！')
    print('=' * 50)
    app.run(host='0.0.0.0', port=port)
