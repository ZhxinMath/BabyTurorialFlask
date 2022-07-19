# encoding:utf-8
"""
用于辅助测试后台脚本的入口，可以直接运行test观察tasks.py运行情况，或者在app.py中运行。

"""
from redis import Redis
import rq
import tasks
import time

# 设定任务编号
task=2 # or 1
# microblog-tasks为redis-server启动时的队列名称
queue = rq.Queue('microblog-tasks', connection=Redis.from_url('redis://'))
# 5为函数传入参数
if task==1:
    job = queue.enqueue(tasks.example1,5)
    # 获取任务id
    print(job.get_id())

elif task==2:
    job = queue.enqueue(tasks.example2, 5)
    # 获取任务id
    job.get_id()
    # 查看任务进度（仅支持任务2）
    while job.meta=={}:
        # 刷新任务进度
        job.refresh()
    while job.meta['progress']!=100:
        job.refresh()
        print('任务进度：{} %'.format(job.meta['progress']))
        time.sleep(2)
    print('任务进度：{} %'.format(job.meta['progress']))

