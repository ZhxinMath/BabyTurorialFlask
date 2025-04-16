from flask import Flask, render_template, redirect, url_for, request, flash, send_from_directory, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import FileField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime
from werkzeug.utils import secure_filename
from config import Config
from datetime import datetime, timedelta
import os

# Flask app 配置
app = Flask(__name__)
app.config.from_object(Config)

# 数据库配置
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.init_app(app)

# 数据库模型
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='waiting')
    created_at = db.Column(db.DateTime, default=datetime.now)
    input_type = db.Column(db.String(10))  # file or text
    input_content = db.Column(db.Text)
    result = db.Column(db.Text)

# 表单类
class PredictionForm(FlaskForm):
    file_input = FileField('Upload File')
    text_input = TextAreaField('Input Sequence')
    submit = SubmitField('Submit Task')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 登录路由
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('submit'))
        return 'User name or password is wrong, please check and try again'
    return render_template('login.html')

# 注册路由
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        return 'User name already exists'
    return render_template('register.html')

# 数据库初始化
@app.route('/init_db')
def init_db():
    db.create_all()
    return "Database initialized!"

# 数据库清理
@app.route('/clear_db')
def clear_db():
    db.drop_all()
    db.create_all()
    # cutoff_time = datetime.now() - timedelta(days=30)
    # old_tasks = Task.query.filter(Task.created_at < cutoff_time).all()
    # for task in old_tasks:
    #     db.session.delete(task)
    # db.session.commit()
    # print("Old tasks deleted!")
    return "Database cleared and reinitialized!"

# 主页路由
@app.route('/')
def home():
    return render_template('homepage.html')

# 提交任务
@app.route('/submit', methods=['GET', 'POST'])
@login_required
def submit():
    form = PredictionForm()
    if form.validate_on_submit():
        task_name = f"Task {Task.query.count() + 1}"
        # 检查是否输入为空
        if not form.file_input.data and not form.text_input.data:
            flash('Please upload a file or input sequence', 'danger')
            return redirect(url_for('submit'))
        new_task = Task(
            user_id=current_user.id,
            name=task_name,
            input_type='file' if form.file_input.data else 'text',
            input_content=form.text_input.data if form.text_input.data else '' # 如果没有文本输入，则先空置，后续存储文件名
        )
        # 文件处理
        if form.file_input.data:
            file = form.file_input.data
            filename = secure_filename(file.filename)  # 确保文件名安全
            file_ext = os.path.splitext(filename)[1].lower()[1:]  # 获取文件扩展名

            # 检查扩展名是否合法
            if file_ext not in app.config['ALLOWED_EXTENSIONS']:
                flash(f'Disallowed file types: {file_ext}, please upload{", ".join(app.config["ALLOWED_EXTENSIONS"])} 格式的文件', 'danger')
                return redirect(url_for('submit'))

            # 生成唯一文件名并保存
            filename = f"{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}{file_ext}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new_task.input_content = filename

        db.session.add(new_task)
        db.session.commit()

        # 启动 Celery 任务
        from tasks import process_task  # 避免循环导入
        process_task.delay(new_task.id)

        flash('Task submitted successfully', 'success')
        return redirect(url_for('submit'))

    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()
    return render_template('submit.html', form=form, tasks=tasks)


@app.route('/download/<int:task_id>')
def download_file(task_id):
    # 假设您有一个函数可以获取任务的文件路径
    task = Task.query.get(task_id)  
    if task and task.status == 'COMPLETED':
        # 假设结果文件存储在某个目录中
        # filename = f"result_{task_id}.txt"  # 根据您的实际文件名格式调整
        directory = app.config['RESULT_FOLDER']
        filename = task.result # 根据您的实际文件名格式调整
        # 校验
        if not os.path.exists(os.path.join(directory, filename)):
            print("File not found:", os.path.join(directory, filename))
            abort(404)
        # Debugging: checking file permissions
        if not os.access(os.path.join(directory, filename), os.R_OK):
            print(f"File is not readable: {os.path.join(directory, filename)}")
            abort(403)
        return send_from_directory(directory, os.path.basename(filename), as_attachment=True)
    else:
        print("Task not found or not completed")
        abort(404)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 仅在启动时创建数据库
    app.run(debug=True)
