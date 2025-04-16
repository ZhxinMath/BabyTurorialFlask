# celery_task.py
from celery import Celery
from flask import Flask
from module_manager import ModelManager, model_manager 
from app import db, Task, app
import pandas as pd
import os

# from celery.signals import worker_process_init

celery = Celery(
    app.name,
    broker=app.config['CELERY_BROKER_URL'],
    backend=app.config['CELERY_RESULT_BACKEND']
)
celery.conf.update(app.config)

legend_text = """
Prediction Legend:
- TL (Too Long): Sequence exceeds 500aa. To save computational resources, please input sequences under 500aa or split them.
- SL (Sliding Window): Sequence is over 20aa, prediction was made by sliding window approach.
- WAA (Wrong Amino Acid): Input contains invalid amino acid characters (only ACDEFGHIKLMNPQRSTVWYX are allowed).
"""


# model_manager = None
# @worker_process_init.connect
# def init_model(**kwargs):
#     """Worker进程初始化时加载模型"""
#     global model_manager
#     print("[Worker] Initializing model...")
#     model_manager = ModelManager()
#     model_manager = model_manager.load_model()  # 此时才会真正加载模型
#     print("[Worker] Model initialized")

# 模型推理封装
model_manager.load_model()

def sequence_predict(input_text_list):
    # 预处理
    cleaned_inputs = []
    allowed_aa = set("ACDEFGHIKLMNPQRSTVWY")
    max_length = 20
    comments = []  # 记录每个序列的批注
    
    for seq in input_text_list:
        seq = seq.strip().upper()
        # 检查氨基酸是否合法
        if not all(aa in allowed_aa for aa in seq):
            comments.append("WAA")  # Wrong amino acid
            cleaned_inputs.append(None)
            continue
        # 检查序列长度
        if len(seq) > 500:
            comments.append("TL")  # Sequence too long
            cleaned_inputs.append(None)
            continue
        elif len(seq) > max_length:
            # 滑窗处理
            window_count = len(seq) - max_length + 1
            comments.extend(["SL"] * window_count)
            cleaned_inputs.extend([seq[i:i+max_length] for i in range(window_count)])
        else:
            comments.append("")  # 无批注
            cleaned_inputs.append(seq)

    # 筛选有效输入
    valid_inputs = [" ".join(seq) for seq in cleaned_inputs if seq is not None]
    
    if not valid_inputs:
        return False, "No valid amino acid sequence, please check input."
    
    # 批量预测
    r = model_manager.predict_batch(valid_inputs)
    if not r[0]:
        return False, str(r[1])  # 这里r[1]可能是错误信息
    else:
        success, predictions, logits = r

    # 重新整合输出
    final_results = []
    pred_idx = 0  # 预测结果索引
    
    for i in range(len(input_text_list)):
        original_seq = input_text_list[i]
        comment = comments[i] if i < len(comments) else ""
        
        if comment == "WAA" or comment == "TL":
            # 无效序列
            final_results.append({
                "origin seq": original_seq,
                "predicted seq": "",
                "prediction": "",
                "logits": "",
                "wrong code": comment
            })
        elif comment == "SL":
            # 滑窗处理 - 一个原始序列对应多个预测结果
            orig_len = len(original_seq)
            window_count = orig_len - max_length + 1
            for _ in range(window_count):
                if pred_idx < len(predictions):
                    final_results.append({
                        "origin seq": original_seq,
                        "predicted seq": valid_inputs[pred_idx],
                        "prediction": predictions[pred_idx],
                        "logits": logits[pred_idx],
                        "wrong code": "SL"
                    })
                    pred_idx += 1
        else:
            # 正常情况
            if pred_idx < len(predictions):
                final_results.append({
                    "origin seq": original_seq,
                    "predicted seq": cleaned_inputs[i],
                    "prediction": predictions[pred_idx],
                    "logits": logits[pred_idx],
                    "wrong code": comment
                })
                pred_idx += 1
            else:
                # 正常情况下不应该发生
                final_results.append({
                    "origin seq": original_seq,
                    "predicted seq": cleaned_inputs[i],
                    "prediction": "",
                    "logits": "",
                    "wrong code": "Failed"
                })
    
    return True, final_results

@celery.task(bind=True)
def process_task(self, task_id):
    print(f"[Celery] Start processing task: {task_id}")
    if model_manager is None:
        return "FAILED: Model not initialized"

    with app.app_context():
        task = Task.query.get(task_id)
        try:
            task.status = 'PROCESSING'
            db.session.commit()

            # Step 1: 获取任务输入
            if task.input_type == 'file':
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], task.input_content)
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"File does not exist: {file_path}")
                input_text_list = pd.read_csv(file_path, header=None, names=['sequence']).sequence.dropna().tolist()
            else:
                input_text_list = [line.strip() for line in task.input_content.split('\n') if line.strip()]
                if not input_text_list:
                    raise ValueError("Input is empty")
            
            # 校验输入数目，至多支持500条
            if len(input_text_list) > 500:
                raise ValueError("Input exceeds the maximum limit of 500 sequences")

            # Step 2: 模型推理
            success, final_results = sequence_predict(input_text_list)

            # Step 3: 保存结果
            if success:
                if not os.path.exists(app.config['RESULT_FOLDER']):
                    os.makedirs(app.config['RESULT_FOLDER'])
                result_path = os.path.join(app.config['RESULT_FOLDER'], f'result_{task_id}.csv')
                if os.path.exists(result_path):
                    os.remove(result_path)

                # prediction_df = pd.DataFrame({'sequence': input_text_list, 'prediction': prediction})
                prediction_df = pd.DataFrame(final_results)
                prediction_df.loc[0, 'Comment_Explanation'] = legend_text
                prediction_df.to_csv(result_path, index=False)

                task.result = result_path
                task.status = 'COMPLETED'
                print(f"[Celery] Task {task_id} completed successfully. Result saved at {result_path}")
            else:
                raise ValueError(f"Model prediction failed: {final_results}")

        except Exception as e:
            print(f"[Celery] Error processing task {task_id}: {e}")
            task.status = 'FAILED'
            task.result = str(e)
        finally:
            db.session.commit()
        return task.status



    
