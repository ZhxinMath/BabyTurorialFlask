# encoding:utf-8
"""
Baby Tutorial Flask : class 3
Copyright (C) 2022 Zhang Xin, Harbin Institute of Technology

第三个脚本中，我们将实现在网页中启动后台任务，并随着刷新实时传入任务进度
后台任务可以先在test.py中进行测试，在回到本脚本中进行网页测试
0.注意！本rq程序仅支持在linux/OS环境下运行，不支持Windows
1.需要安装redis:
<base> $ sudo apt update
<base> $ sudo apt install redis-server
2.安装rq:
<base> $ conda activate <虚拟环境>
<venv> $ pip install rq
3.打开两个窗口A\B，在两个窗口均启动虚拟环境，并同时<进入项目所在文件夹>
4.在窗口A中启动worker进程 "microblog-tasks"，可以更改为其它名字
<venv> $ rq worker microblog-tasks
5.在窗口B中启动执行脚本即可
<venv> $ python app.py

练习：可以加入
"""

from flask import Flask,request,render_template
from redis import Redis
import rq
import tasks
app = Flask(__name__)

queue = rq.Queue('microblog-tasks', connection=Redis.from_url('redis://'))

# 检测输入的s是否是数字
def is_number(s):
    if s.count(".")==1:   #小数的判断
        if s[0]=="-":
            s=s[1:]
        if s[0]==".":
            return False
        s=s.replace(".","")
        for i in s:
            if i not in "0123456789":
                return False
        else:                #这个else与for对应的
            return True
    elif s.count(".")==0:   #整数的判断
        if s[0]=="-":
            s=s[1:]
        for i in s:
            if i not in "0123456789":
                return False
        else:
            return True
    else:
        return False

# 使用列表在不同函数之间传输程序进度
num=-1
jobs=[]


@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'POST':
        jobindex = request.form.get('jobnum')
        if (not jobindex) or (not is_number(jobindex)):
            return '请输入整数！'
        jobindex = int(jobindex)
        # 检验程序是否存在
        if jobindex > num:
            return '程序不存在，请重新输入！'
        # 刷新程序进度参数
        jobs[jobindex].refresh()
        while jobs[jobindex].meta == {}:
            # 刷新任务进度，直到有显示
            jobs[jobindex].refresh()
        return '程序{}进度为：{}%'.format(jobindex,jobs[jobindex].meta['progress'])
    return render_template('index.html')


@app.route('/ScriptArgs',methods=['GET','POST'])
def Script():
    # 修改全局变量需要在局部进行声明
    global num
    # 若网页使用POST请求，则返回结果页面
    if request.method == 'POST':
        # 从网页中获取参数
        ScriptArg = request.form.get('arg')
        # 如果输入为空，则将参数修改为默认值
        if not ScriptArg:
            ScriptArg=5
        # 校验参数
        if is_number(ScriptArg):
            # 启动任务
            num = num+1
            job = queue.enqueue(tasks.example2, int(ScriptArg))
            jobs.append(job)
            return '程序{}启动成功 <a href = "/">返回首页</a>查看当前程序进度'.format(num)
        else:
            return '请输入整数！'
    # 若网页使用Get请求，则返回注册页面
    return render_template('ScriptRunning.html')


if __name__ == '__main__':
    app.run()