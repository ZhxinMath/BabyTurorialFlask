# module_manager.py
import os
import torch
import numpy as np
from transformers import BertTokenizer, BertForSequenceClassification


class ModelManager:
    def __init__(self, device=None):
        # self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        # self.tokenizer = self.get_tokenizer("./models/vocab.txt")
        # self.model = BertForSequenceClassification.from_pretrained(
        #     "/home/zhangxin/flask_for_submit/models/checkpoint-763450", num_labels=2
        # )
        # self.model.to(self.device)
        # self.model.eval()
        self.device = None
        self.tokenizer = None  # 初始化tokenizer为None，在load_model中设置为实际的tokenizer实例
        self.model = None

    def load_model(self, model_path="/home/zhangxin/flask_for_submit/models/checkpoint-763450"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = self.get_tokenizer("./models/vocab.txt")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file does not exist: {model_path}")
        self.model = BertForSequenceClassification.from_pretrained(model_path, num_labels=2)
        self.model.to(self.device)
        self.model.eval()

    def predict(self, text: str):
        if not text:
            return False, "Empty input"
        try:
            inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
            inputs = {key: value.to(self.device) for key, value in inputs.items()}
            with torch.no_grad():
                outputs = self.model(**inputs)
            logits = outputs.logits.cpu().numpy()
            return True, logits.argmax(axis=1).tolist()
        except Exception as e:
            return False, str(e)

    def predict_batch(self, texts: list[str]):
        if not texts or not isinstance(texts, list):
            return False, "Input must be a list of strings"
        try:
            inputs = self.tokenizer(
                texts,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=1024
            )
            inputs = {key: value.to(self.device) for key, value in inputs.items()}
            with torch.no_grad():
                outputs = self.model(**inputs)
            logits = outputs.logits.cpu().numpy()
            predictions = logits.argmax(axis=1).tolist()
            return True, predictions, logits.tolist()  # 返回预测结果和原始logits
        except Exception as e:
            return False, str(e)

    def get_tokenizer(self, vocab_path):
        if not os.path.exists(vocab_path):
            AMINO_ACIDS = list("ACDEFGHIKLMNPQRSTVWY") + ["X"]
            SPECIAL_TOKENS = ["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"]
            VOCAB = SPECIAL_TOKENS + AMINO_ACIDS
            with open(vocab_path, "w") as f:
                for token in VOCAB:
                    f.write(token + "\n")

        tokenizer = BertTokenizer(
          
            vocab_file=vocab_path,
            unk_token="[UNK]",
            pad_token="[PAD]",
            cls_token="[CLS]",
            sep_token="[SEP]",
            mask_token="[MASK]",
            do_lower_case=False,
            tokenize_chinese_chars=False
        )
        return tokenizer


# 创建模型全局实例
model_manager = ModelManager()



# 测试是否正常运行
# if __name__ == "__main__":
    # import pandas as pd
    # success, prediction = model_manager.predict("MAAWMRLLPLLALLALWGPD")
    # success, prediction = model_manager.predict_batch(["MAAWMRLLPLLALLALWGPD"]*100)
    # df = pd.read_csv("/home/zhangxin/flask_for_submit/models/human_virus_100k_seq_label_20aa.csv")
    # seq_20aa = df['sequence'].to_list()
    # label_seq = df['label'].to_list()
    # label_20aa = [1 if v == 'human' else 0 for v in label_seq]
    # 异常处理
    # success, prediction = model_manager.predict_batch([" ".join(seq) for seq in seq_20aa])

    # print(success, prediction)