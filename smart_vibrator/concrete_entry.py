"""
concrete_entry.py
混凝土入场摄像头识别模块
模拟摄像头读取混凝土配料单并提取骨料类型、水灰比、配比比例。
"""

def extract_material_params_from_camera():
    """
    模拟摄像头OCR识别混凝土配料单。
    :return: dict {"aggregate_type": str, "water_cement_ratio": float, "proportion": str}
    """
    # 实际场景应调用OpenCV+Pytesseract，这里直接返回伪造数据
    return {
        "aggregate_type": "碎石",
        "water_cement_ratio": 0.42,
        "proportion": "1:2:3"
    }

if __name__ == "__main__":
    print(extract_material_params_from_camera())
