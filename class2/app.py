"""
Baby Tutorial Flask : class 2
Copyright (C) 2022 Zhang Xin, Harbin Institute of Technology

第二个脚本中，我们将考虑模板开发，同时获取网页输入的参数
在网页中打开/register即可注册，打开/show即可展现已注册用户

具体代码原理可以查看书籍《Flask Web开发实战、入门、进阶于原理解析》
"""

import json
from flask import Flask,request,render_template

app = Flask(__name__)


users = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register',methods=['GET','POST'])
def register():
    # print(request.method)
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        repassword = request.form.get('repassword')
        if password == repassword:
            user = {'username':username,'password':password}
            users.append(user)
            return '注册成功 <a href = "/">返回首页</a>'
        else:
            return '两次密码不一致'
    return render_template('register.html')

@app.route('/show')
def show():
    j_str = json.dumps(users)
    return j_str



if __name__ == '__main__':
    app.run()

