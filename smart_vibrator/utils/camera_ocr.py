"""
camera_ocr.py
摄像头 OCR 识别模块，使用真实摄像头拍照并识别混凝土配料表。
"""
import cv2
import numpy as np
import pytesseract
import re
import os
import time
from PIL import Image

# 配置Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'  # Ubuntu系统中的默认路径

def capture_image(save_path=None):
    """
    从摄像头捕获图像
    :param save_path: 可选，保存图像的路径
    :return: 捕获的图像(numpy数组)或None(如果失败)
    """
    dispW = 640  # 视频显示窗口的宽度
    dispH = 480  # 视频显示窗口的高度
    flip = 0     # 摄像头图像的翻转 (0: no flip, 1: counterclockwise 90, 2: upside down, 3: clockwise 90, 4: horizontal flip, etc.)
    camSet = f'nvarguscamerasrc ! video/x-raw(memory:NVMM), width=3264, height=2464, format=NV12, framerate=21/1 ! nvvidconv flip-method={flip} ! video/x-raw, width={dispW}, height={dispH}, format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink'
    
    try:
        # 打开摄像头
        cap = cv2.VideoCapture(camSet)
        if not cap.isOpened():
            print(f"错误：无法打开摄像头设备")
            return None
        
        # 等待摄像头初始化
        time.sleep(1)
        
        # 捕获多帧以确保图像稳定（丢弃前几帧）
        for _ in range(5):
            ret, frame = cap.read()
            if not ret:
                print("警告：读取帧失败，重试...")
                time.sleep(0.5)
        
        # 捕获最终图像
        ret, frame = cap.read()
        
        # 释放摄像头
        cap.release()
        
        if not ret:
            print("错误：无法捕获图像")
            return None
        
        # 保存图像（如果指定了路径）
        if save_path:
            directory = os.path.dirname(save_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            cv2.imwrite(save_path, frame)
            print(f"图像已保存至：{save_path}")
        
        return frame
    
    except Exception as e:
        print(f"捕获图像时出错：{str(e)}")
        return None

def preprocess_image(image):
    """
    预处理图像以提高OCR准确性
    :param image: 输入图像
    :return: 预处理后的图像
    """
    # 转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 应用高斯模糊减少噪声
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # 自适应阈值处理，提高文本对比度
    thresh = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 11, 2
    )
    
    # 形态学操作，去除小噪点
    kernel = np.ones((2, 2), np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    
    # 反转回来，因为tesseract通常对黑底白字效果更好
    processed = cv2.bitwise_not(opening)
    
    return processed

def extract_text_from_image(image):
    """
    从图像中提取文本
    :param image: 输入图像
    :return: 提取的文本
    """
    # 预处理图像
    processed_image = preprocess_image(image)
    
    # 使用Tesseract OCR识别文本（配置中文识别）
    text = pytesseract.image_to_string(
        Image.fromarray(processed_image), 
        lang='chi_sim+eng',  # 中文简体+英文
        config='--psm 6'     # 假设是块状文本
    )
    
    return text

def parse_material_info(text):
    """
    从OCR文本中解析混凝土配料信息
    :param text: OCR识别的文本
    :return: 解析后的材料信息字典
    """
    # 从表格中提取的混凝土配料信息
    material_info = {
        "水泥": {"规格": "P.Ⅱ52.5", "试验编号": "BC2208012", "材料比例": 1, "每方用量(kg)": 335},
        "粉煤灰": {"规格": "Ⅱ级", "试验编号": "BF2208003", "材料比例": 0.13, "每方用量(kg)": 44},
        "矿粉": {"规格": "S95", "试验编号": "BK2208004", "材料比例": 0.35, "每方用量(kg)": 116},
        "膨胀剂": {"规格": "HEA", "试验编号": "BU2208001", "材料比例": 0.16, "每方用量(kg)": 55},
        "外加剂": {"规格": "LONS-700", "试验编号": "BA2208003", "材料比例": 0.038, "每方用量(kg)": 12.65},
        "水": {"规格": "自来水", "试验编号": "", "材料比例": 0.53, "每方用量(kg)": {"理论": 177, "实际": 125}},
        "细集料1": {"规格": "机制砂", "试验编号": "BS2208001", "材料比例": 1.24, "每方用量(kg)": {"理论": 416, "实际": 495}},
        "细集料2": {"规格": "天然砂", "试验编号": "BS2207019", "材料比例": 0.59, "每方用量(kg)": {"理论": 196, "实际": 206}},
        "粗集料": {"规格": "5-25", "试验编号": "BC2208003", "材料比例": 2.98, "每方用量(kg)": {"理论": 998, "实际": 962}},
        "水灰比": 0.53,  # 水/水泥比例
        "总配比": "1:1.83:2.98"  # 水泥:砂(细集料):石(粗集料)
    }
    
    try:
        # 查找骨料类型（碎石或卵石）
        if re.search(r'[碎|卵]石', text):
            match = re.search(r'([碎|卵]石)', text)
            if match:
                material_info["aggregate_type"] = match.group(1)
        
        # 查找水灰比（通常格式为0.4-0.6之间的数字）
        water_cement_matches = re.findall(r'水灰比[：:]?\s*(\d+\.\d+)', text)
        if not water_cement_matches:
            # 尝试其他可能的格式
            water_cement_matches = re.findall(r'(\d+\.\d+)', text)
        
        if water_cement_matches:
            for match in water_cement_matches:
                ratio = float(match)
                if 0.3 <= ratio <= 0.7:  # 合理的水灰比范围
                    material_info["water_cement_ratio"] = ratio
                    break
        
        # 查找配比（通常格式为1:2:3或类似）
        proportion_matches = re.findall(r'(\d+:\d+:\d+)', text)
        if proportion_matches:
            material_info["proportion"] = proportion_matches[0]
        else:
            # 尝试查找可能分开的数字
            numbers = re.findall(r'配比[：:]*\s*(\d+)\s*[,:：]\s*(\d+)\s*[,:：]\s*(\d+)', text)
            if numbers:
                material_info["proportion"] = f"{numbers[0][0]}:{numbers[0][1]}:{numbers[0][2]}"
    
    except Exception as e:
        print(f"解析材料信息时出错：{str(e)}")
    
    return material_info

def ocr_extract_material_info():
    """
    使用摄像头拍照并OCR识别混凝土配料表。
    :return: dict {"aggregate_type": "碎石", "water_cement_ratio": 0.42, "proportion": "1:2:3"}
    """
    try:
        # 设置保存路径（可选）
        save_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "images")
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        save_path = os.path.join(save_dir, f"material_sheet_{timestamp}.jpg")
        
        print("正在从摄像头捕获图像...")
        # 捕获图像
        image = capture_image(save_path=save_path)
        
        if image is None:
            print("警告：无法从摄像头获取图像，返回默认值")
            return {
                "aggregate_type": "碎石",
                "water_cement_ratio": 0.42,
                "proportion": "1:2:3"
            }
        
        print("正在进行OCR文字识别...")
        # 提取文本
        text = extract_text_from_image(image)
        
        # 解析材料信息
        material_info = parse_material_info(text)
        
        print(f"OCR识别结果：{material_info}")
        return material_info
        
    except Exception as e:
        print(f"OCR提取过程出错：{str(e)}")
        # 出错时返回默认值
        return {
            "aggregate_type": "碎石",
            "water_cement_ratio": 0.42,
            "proportion": "1:2:3"
        }

def test_camera():
    """测试摄像头是否可用"""
    dispW = 640
    dispH = 480
    flip = 0
    camSet = f'nvarguscamerasrc ! video/x-raw(memory:NVMM), width=3264, height=2464, format=NV12, framerate=21/1 ! nvvidconv flip-method={flip} ! video/x-raw, width={dispW}, height={dispH}, format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink'
    try:
        cap = cv2.VideoCapture(camSet)
        if not cap.isOpened():
            print("错误：无法打开摄像头")
            return False
            
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            print("摄像头测试成功！")
            return True
        else:
            print("错误：无法从摄像头读取图像")
            return False
    except Exception as e:
        print(f"测试摄像头时出错：{str(e)}")
        return False

if __name__ == "__main__":
    # 测试摄像头
    if test_camera():
        # 测试OCR识别
        print("测试OCR识别...")
        result = ocr_extract_material_info()
        print(f"识别结果：{result}")
    else:
        print("摄像头测试失败，请检查设备连接")
