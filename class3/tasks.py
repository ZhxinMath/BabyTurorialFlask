# encoding:utf-8
"""
后代任务脚本
example1为最简单的运行脚本
example2为包含进度示例的后台脚本
"""
import time
from rq import get_current_job



def example1(seconds):
    print('Starting task:No.1')
    for i in range(seconds):
        print(i)
        time.sleep(1)
    print('Task completed')

def example2(seconds):
    job = get_current_job()
    print('Starting task:No.2')
    for i in range(seconds):
        # job.meta是一个字典，可以任意写入进度对象。
        job.meta['progress'] = 100.0 * i / seconds
        job.save_meta()
        print(i)
        time.sleep(1)
    job.meta['progress'] = 100
    job.save_meta()
    print('Task completed')