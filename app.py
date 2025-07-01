import logging

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于会话管理，可自定义
# 初始化数据库
def init_db():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS task (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            leader TEXT NOT NULL,
            description TEXT NOT NULL,
            executor TEXT NOT NULL,
            receive_time TEXT NOT NULL,
            finsh_time TEXT NOT NULL,
            overall_progress TEXT,
            progress_in_detail TEXT
        )
    ''')
    # 创建用户表
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    # 定义多个用户数据
    users = [
        ('admin', 'admin'),
        ('zhangshuxin', 'zhangshuxin'),
        ('wanghao', 'wanghao'),
        ('songyi', 'songyi'),
        ('zhuhongli', 'zhuhongli'),
        ('panhuali', 'panhuali'),
        ('shaoning', 'shaoning'),
        ('xueyan', 'xueyan'),
        ('zhangge', 'zhangge'),
        ('zhanghao', 'zhanghao'),
        ('wangshan', 'wangshan'),
        ('donghongyu', 'donghongyu'),
        ('zhangenhao', 'zhangenhao')
        # 可以根据需要添加更多用户
    ]
    for username, password in users:
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?,?)", (username, password))
            logging.debug(f"成功插入用户: {username}")
        except sqlite3.IntegrityError:
            logging.debug(f"用户 {username} 已存在，跳过插入。")
    conn.commit()
    conn.close()


# 登录页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username =? AND password =?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['username'] = username
            if username == 'admin':
                session['mode'] = 'display'  # admin 用户进入展示模式
            else:
                session['mode'] = 'edit'  # 其他用户进入编辑模式
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='用户名或密码错误')
    return render_template('login.html')

# 注销功能
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('mode', None)
    return redirect(url_for('login'))

# 切换到编辑模式
@app.route('/switch_to_edit_mode')
def switch_to_edit_mode():
    session['mode'] = 'edit'
    return redirect(url_for('index'))

# 切换到展示模式
@app.route('/switch_to_display_mode')
def switch_to_display_mode():
    session['mode'] = 'display'
    return redirect(url_for('index'))
# 首页，展示任务列表
@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('SELECT * FROM task')
    tasks = c.fetchall()
    conn.close()
    username = session['username']  # 获取当前登录用户的用户名
    mode = session.get('mode', 'display')
    leaders = ['张振刚总', '李世冲总', '朱晓威主任']
    executors = ['朱洪利', '宋艺', '张树新', '张浩', '王珊', '张革', '王浩', '张恩浩', '潘华莉', '董弘宇', '邵宁', '薛䶮']
    return render_template('index.html', tasks=tasks, username=username, mode=mode, leaders=leaders, executors=executors)


# 新增任务
@app.route('/add', methods=['GET', 'POST'])
def add():
    if 'username' not in session:
        return redirect(url_for('login'))
    if session.get('mode') != 'edit':
        return redirect(url_for('index'))
    if request.method == 'POST':
        leader = request.form.get('leader')
        description = request.form.get('description')
        executor = request.form.get('executor')
        receive_time = request.form.get('receive_time')
        finsh_time = request.form.get('finsh_time')
        overall_progress = request.form.get('overall_progress')
        progress_in_detail = request.form.get('progress_in_detail')

        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()
        try:
            c.execute('''
                INSERT INTO task (leader, description, executor, receive_time, finsh_time, overall_progress, progress_in_detail)
                VALUES (?,?,?,?,?,?,?)
            ''', (leader, description, executor, receive_time, finsh_time, overall_progress, progress_in_detail))
            conn.commit()
            return jsonify({'status': 'success', 'message': '任务新增成功'})
        except Exception as e:
            conn.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 500
        finally:
            conn.close()


# 删除任务
@app.route('/delete/<int:id>')
def delete(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    if session.get('mode') != 'edit':
        return redirect(url_for('index'))
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('DELETE FROM task WHERE id =?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# # 编辑任务
# @app.route('/edit/<int:id>', methods=['GET', 'POST'])
# def edit(id):
#     if 'username' not in session:
#         return redirect(url_for('login'))
#     if session.get('mode') != 'edit':
#         return redirect(url_for('index'))
#     if request.method == 'POST':
#         leader = request.form.get('leader')
#         description = request.form.get('description')
#         executor = request.form.get('executor')
#         receive_time = request.form.get('receive_time')
#         finsh_time = request.form.get('finsh_time')
#         overall_progress = request.form.get('overall_progress')
#         progress_in_detail = request.form.get('progress_in_detail')
#
#         conn = sqlite3.connect('tasks.db')
#         c = conn.cursor()
#         c.execute('''
#             UPDATE task
#             SET leader =?, description =?, executor =?, receive_time =?, finsh_time =?, overall_progress =?, progress_in_detail =?
#             WHERE id =?
#         ''', (leader, description, executor, receive_time, finsh_time, overall_progress, progress_in_detail, id))
#         conn.commit()
#         conn.close()
#         return redirect(url_for('index'))
#
#     conn = sqlite3.connect('tasks.db')
#     c = conn.cursor()
#     c.execute('SELECT * FROM task WHERE id =?', (id,))
#     task = c.fetchone()
#     conn.close()
#     leaders = ['韩宇总', '韩增辉总', '朱晓威主任']
#     executors = ['朱洪利', '宋艺', '张树新', '张浩', '王珊', '张革', '王浩', '张恩浩', '潘华莉', '董弘宇', '邵宁', '薛䶮']
#     return render_template('edit.html', task=task, leaders=leaders, executors=executors)

# 处理表格内数据更新
@app.route('/update_task', methods=['POST'])
def update_task():
    if 'username' not in session:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    if session.get('mode') != 'edit':
        return jsonify({'status': 'error', 'message': '非编辑模式'}), 403
    data = request.get_json()
    task_id = data.get('id')
    column = data.get('column')
    value = data.get('value')

    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    try:
        if column == 'leader':
            c.execute("UPDATE task SET leader =? WHERE id =?", (value, task_id))
        elif column == 'description':
            c.execute("UPDATE task SET description =? WHERE id =?", (value, task_id))
        elif column == 'executor':
            c.execute("UPDATE task SET executor =? WHERE id =?", (value, task_id))
        elif column == 'receive_time':
            c.execute("UPDATE task SET receive_time =? WHERE id =?", (value, task_id))
        elif column == 'finsh_time':
            c.execute("UPDATE task SET finsh_time =? WHERE id =?", (value, task_id))
        elif column == 'overall_progress':
            c.execute("UPDATE task SET overall_progress =? WHERE id =?", (value, task_id))
        elif column == 'progress_in_detail':
            c.execute("UPDATE task SET progress_in_detail =? WHERE id =?", (value, task_id))
        conn.commit()
        return jsonify({'status': 'success', 'message': '更新成功'})
    except Exception as e:
        conn.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
    app.run(debug=True)
