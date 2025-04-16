import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-super-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../instance/tasks.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model.h5')
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), './uploads/')
    RESULT_FOLDER = os.path.join(os.path.dirname(__file__), './results/') # 相对路径容易出问题
    PREDICTION_TIMEOUT = 3600  # 1小时超时
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'txt', 'csv'}
    SCHEDULER_API_ENABLED = True
    