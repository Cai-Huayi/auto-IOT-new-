#!/bin/bash

# 安装OpenCV和Tesseract OCR相关依赖
echo "正在安装摄像头OCR所需依赖..."

# 更新包列表
sudo apt-get update

# 安装OpenCV依赖
sudo apt-get install -y python3-opencv

# 安装Tesseract OCR及其依赖
sudo apt-get install -y tesseract-ocr
sudo apt-get install -y libtesseract-dev
sudo apt-get install -y tesseract-ocr-chi-sim  # 中文简体语言包

# 安装Python库
pip install opencv-python
pip install pytesseract
pip install numpy
pip install pillow

echo "依赖安装完成！"
