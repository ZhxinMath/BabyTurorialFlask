#!/bin/bash

# 进入项目目录（根据你的实际路径调整）
cd ~/flask_for_submit

# 启动 Redis（如果未运行）
REDIS_PID=$(pgrep redis-server)
if [ -z "$REDIS_PID" ]; then
    echo "Starting Redis..."
    redis-server --daemonize yes
else
    echo "Redis is already running (PID: $REDIS_PID)"
fi


# 启动 Celery Worker（在虚拟环境下后台运行）
echo "Starting Celery Worker..."
# nohup /home/zhangxin/.conda/envs/bert_for_web/bin/python celery_worker.py > celery.log 2>&1 & # 队列设计为1，避免同时有多个进程消耗显存
/home/zhangxin/.conda/envs/bert_for_web/bin/python -m celery -A tasks.celery worker --pool=threads --loglevel=info > celery.log 2>&1 &
#/home/zhangxin/.conda/envs/bert_for_web/bin/python -m celery -A tasks.celery worker --loglevel=info > celery.log 2>&1 &
# nohup python -m celery -A tasks.celery worker --loglevel=info > celery.log 2>&1 &
CELERY_PID=$!
echo "Celery Worker started (PID: $CELERY_PID)"

# 设置 Flask 为 Debug 模式
# echo "Setting Flask in Debug mode..."
# export FLASK_ENV=development

# 启动 Flask 应用（在虚拟环境下前台运行）
echo "Starting Flask App..."
# nohup flask run --host=0.0.0.0 --port=5000 > flask.log 2>&1 &# 如果需要debug模式--debug
flask run --host=0.0.0.0 --port=5000

# 清理函数（按 Ctrl+C 时执行）
cleanup() {
    echo "Stopping Celery Worker (PID: $CELERY_PID)..."
    kill $CELERY_PID
    echo "Stopping Redis..."
    redis-cli shutdown
    deactivate  # 退出虚拟环境
    exit 0
}

# 捕获 Ctrl+C 信号
trap cleanup SIGINT