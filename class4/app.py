# -*- coding: utf-8 -*-
"""
Baby Tutorial Flask : class 3
Copyright (C) 2022 Zhang Xin, Harbin Institute of Technology

第四个脚本中，我们将配合css对网页进行美化。事实上所有的网页都可以直接打开

具体的教程可以通过这个网站了解css：https://www.runoob.com/css/css-tutorial.html
也可以在这个网站下尝试编写css：https://www.runoob.com/try/try.php?filename=trycss_default
你可以在这个网站下获取许多css例子：
你可以在这个网站下获取许多css美化结果 https://codepen.io/
"""
from flask import Flask,request,render_template,Response,send_file
import os
import time
import json
app = Flask(__name__)

# 用于在html页面中寻找css、js文件所在的路径
app._static_folder = "./templates/static"

@app.route('/web1')
def web1page():
    return render_template('web1.html')


@app.route('/web2')
def web2page():
    return render_template('web2.html')


@app.route('/web3')
def web3page():
    path = "/home/zhangxin/flask/class4"
    dirs = os.listdir(path)
    temp = []
    for dir in dirs:
        temp.append({'name': dir})

    return render_template('index.html', data=temp)


@app.route('/web4')
def web4page():
    content = [
        ['HumanXX','human','完成','2023/6/1/22:40','2023/6/2/13:20'],
        ['RatXX', 'rat', '进行中', '2023/6/3/22:40', ''],
        ['RatXX', 'rat', '进行中', '2023/6/3/22:40', ''],
        ['RatXX', 'rat', '进行中', '2023/6/3/22:40', ''],
        ['RatXX', 'rat', '进行中', '2023/6/3/22:40', ''],
        ['RatXX', 'rat', '进行中', '2023/6/3/22:40', '']

    ]
    return render_template('web4.html', content=content)


@app.route('/web5')
def web5page():

    return render_template('web5.html')





@app.route('/web6', methods=['GET', 'POST'])
def web6page():
    if request.method == 'POST':
        # 处理不同的POST请求，在这里的关键字索引是HTML中的name
        # 上传文件
        if 'upload_file' in request.form:
            print("in the upload process")
            file = request.files['file-uploader']
            name = file.filename
            file.save("./{}".format(name))
            # 记录文件上传数据
            timestr = time.strftime("%Y%m%d-%H%M%S")
            tmp_json = [name, timestr,'upload']
            # 将文件上传数据写入json中
            if not os.path.exists("io.json"):
                with open("./io.json", "w") as f:
                    json.dump(tmp_json, f)
                f.close()
            else:
                with open("./io.json", "r") as f:
                    io_json = json.load(f)
                f.close()
                io_json.append(tmp_json)
                with open("./io.json", "w") as f:
                    json.dump(io_json, f)
                f.close()

            return '文件{}接受成功，<a href = "/web6">返回首页</a>查看当前程序进度'.format(name)

        # 选中文件进行下载
        elif 'download_file' in request.form:
            print("in the download process")
            DownLoadFileName = request.form.get('file_select')
            print(DownLoadFileName)
            # send_file(DownLoadFileName, as_attachment=True)
            # 记录文件下载数据
            timestr = time.strftime("%Y%m%d-%H%M%S")
            tmp_json = [DownLoadFileName, timestr,'download']
            # 将文件下载数据写入json中
            if not os.path.exists("io.json"):
                with open("./io.json", "w") as f:
                    json.dump(tmp_json, f)
                f.close()
            else:
                with open("./io.json", "r") as f:
                    io_json = json.load(f)
                f.close()
                io_json.append(tmp_json)
                with open("./io.json", "w") as f:
                    json.dump(io_json, f)
                f.close()

            return '文件{}正在下载，<a href = "/web6">返回首页</a>查看当前程序进度'.format(DownLoadFileName),send_file(DownLoadFileName, as_attachment=True)

    # 将可下载文件数据显示在下拉列表中。
    print("in the show process")
    path = "/home/zhangxin/flask/class4"
    dirs = os.listdir(path)
    temp = []
    for dir in dirs:
        if '.' in dir:
            temp.append({'name': dir})

    # 将文件上传历史数据显示在表格中。
    labels = ["文件名","操作时间","操作类型"]
    if not os.path.exists("io.json"):
        with open("./io.json", "w") as f:
            json.dump([], f)
        f.close()
    with open("./io.json", "r") as f:
        record = json.load(f)
    f.close()


    return render_template('web6.html',labels = labels,  record=record, data = temp)





@app.route("/test" , methods=['GET', 'POST'])
def test():
    select = request.form.get('comp_select')
    print(select)
    return(str(select)) # just to see what select is





if __name__ == '__main__':
    # app.run()
    # To change the web ip, use the following command
    # app.run(host='192.168.11.240',port=5000,debug=True)
    app.run(host='127.0.0.1', port=5000, debug=True)
