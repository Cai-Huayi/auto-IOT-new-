#!/bin/bash

# 智能振捣系统 Ubuntu 部署脚本
echo "=== 智能振捣系统部署脚本 ==="
echo "正在准备环境..."

# 1. 更新系统包
echo "正在更新系统包..."
sudo apt-get update

# 2. 安装Python和必要工具
echo "正在安装Python和必要工具..."
sudo apt-get install -y python3 python3-pip python3-venv git

# 3. 创建项目目录
echo "正在创建项目目录..."
mkdir -p ~/smart_vibrator
cd ~/smart_vibrator

# 4. 克隆或复制项目文件
echo "请选择部署方式:"
echo "1. 从本地复制项目文件(如果您已经通过U盘等方式将文件传输到Ubuntu系统)"
echo "2. 从Git仓库克隆(如果您的项目在Git仓库中)"
read -p "请输入选项(1或2): " deploy_option

if [ "$deploy_option" == "1" ]; then
    read -p "请输入项目文件所在路径: " source_path
    cp -r $source_path/* ~/smart_vibrator/
    echo "文件已复制到 ~/smart_vibrator/"
elif [ "$deploy_option" == "2" ]; then
    read -p "请输入Git仓库URL: " git_url
    git clone $git_url ~/smart_vibrator
    echo "从Git仓库克隆完成"
else
    echo "选项无效，退出部署"
    exit 1
fi

# 5. 创建并激活虚拟环境
echo "正在创建Python虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 6. 安装依赖
echo "正在安装项目依赖..."
pip install opencv-python pytesseract numpy matplotlib

# 7. 创建数据目录(如果不存在)
mkdir -p data/reports

# 8. 检查文件权限
echo "正在设置文件权限..."
chmod +x main.py

echo "=== 部署完成 ==="
echo "您可以通过以下命令运行系统:"
echo "cd ~/smart_vibrator"
echo "source venv/bin/activate"
echo "python3 main.py"

# 询问是否立即运行
read -p "是否立即运行系统? (y/n): " run_option
if [ "$run_option" == "y" ] || [ "$run_option" == "Y" ]; then
    python3 main.py
fi
