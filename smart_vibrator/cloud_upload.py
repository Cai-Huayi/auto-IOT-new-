"""
cloud_upload.py
数据闭环模块
将施工数据保存为本地 JSON 文件，文件名包含日期时间。
"""
import json
import os
from datetime import datetime

def upload_data(data):
    """
    保存数据为本地JSON文件，文件名包含日期时间。
    :param data: dict，策略和执行结果集合
    """
    reports_dir = os.path.join(os.path.dirname(__file__), 'data', 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    now = datetime.now().strftime('%Y-%m-%d_%H-%M')
    filename = f"施工报告_{now}.json"
    file_path = os.path.join(reports_dir, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"数据已保存至: {file_path}")

if __name__ == "__main__":
    sample_data = {"test": 123, "result": "ok"}
    upload_data(sample_data)
