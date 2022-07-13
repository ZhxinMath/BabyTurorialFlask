"""
Baby Tutorial Flask : class 1
Copyright (C) 2022 Zhang Xin, Harbin Institute of Technology

第一个脚本中，按照如下操作即可启动一个flask框架。
1.在命令行/Anaconda Prompt中启动虚拟环境
2.切换到目标文件夹class1下
3.在命令行中输入python app.py 执行代码，或者输入flask run（此时不可在anaconda prompt下进行，只能在控制台进行）
4.登录127.0.0.1:5000查看网页

具体代码原理可以查看书籍《Flask Web开发实战、入门、进阶于原理解析》
"""


from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return '<h1>Hello Flask!</h1>'

if __name__ == '__main__':
    app.run()

