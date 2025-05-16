# 智能振捣系统（Smart Concrete Vibration System）

![智能振捣系统](https://img.shields.io/badge/Smart%20Vibrator-IoT%20%26%20AI-blue)
![平台](https://img.shields.io/badge/Platform-Windows%20%7C%20Ubuntu-lightgrey)
![版本](https://img.shields.io/badge/Version-1.0.0-green)

## 📋 项目概述

智能振捣系统是一个基于物联网与AI技术的混凝土施工质量控制解决方案。该系统实现了混凝土入场自动识别、环境参数实时采集、振捣策略智能生成、设备精准控制与数据闭环管理的全流程自动化。系统支持在Windows和Ubuntu环境下运行，并可通过GPIO接口控制真实的步进电机进行振捣操作，显著提升混凝土施工质量与效率。

## ✨ 核心特性

- **智能识别**：自动识别混凝土配料单，提取关键参数
- **环境感知**：实时采集温度、湿度、坠落度等环境参数
- **策略优化**：基于材料特性和环境条件，智能生成最优振捣策略
- **精准控制**：支持步进电机精确控制，实现不同频率和深度的振捣
- **可视化分析**：提供振捣点位三维可视化，直观展示振捣方案
- **数据闭环**：完整记录振捣过程数据，支持后续分析与优化
- **跨平台兼容**：同时支持Windows和Ubuntu系统

## 🔧 技术架构

系统采用模块化设计，主要包含以下核心模块：

1. **数据采集层**
   - 混凝土参数识别模块（OCR技术）
   - 环境参数采集模块（传感器接口）

2. **策略生成层**
   - 振捣策略计算引擎
   - 点位布局优化算法

3. **设备控制层**
   - 步进电机驱动模块
   - GPIO接口控制模块

4. **可视化与数据层**
   - 3D点位可视化模块
   - 数据存储与上传模块

## 📁 目录结构

```
auto-IOT/
├─ smart_vibrator/           # 智能振捣系统核心目录
│  ├─ main.py                # 主程序入口
│  ├─ vibration_strategy.py  # 振捣策略生成模块
│  ├─ device_control.py      # 设备控制模块
│  ├─ visualize_points.py    # 振捣点位可视化模块
│  ├─ cloud_upload.py        # 数据上传模块
│  ├─ concrete_entry.py      # 混凝土入场处理
│  ├─ env_monitor.py         # 环境监测模块
│  ├─ utils/                 # 工具模块
│  │  ├─ sensor_interface.py # 传感器接口
│  │  ├─ camera_ocr.py       # 摄像头和OCR接口
│  │  ├─ config.py           # 配置文件
│  │  ├─ buzzer_control.py   # 蜂鸣器控制模块
│  │  └─ led_control.py      # LED指示灯控制模块
│  ├─ output/                # 输出目录
│  │  ├─ vibration_strategy.json # 振捣策略JSON文件
│  │  └─ vibration_points.png    # 振捣点位可视化图像
│  └─ data/                  # 数据目录
│     └─ reports/            # 数据报告存储目录
├─ reset_gpio.py             # GPIO重置工具
├─ buzzer_emergency_off.py   # 蜂鸣器紧急关闭工具
├─ buzzer_interactive.py     # 蜂鸣器交互测试工具
└─ *.ipynb                   # 各种测试和实验Jupyter笔记本
```

## 🚀 功能模块详解

### 1. 混凝土入场识别

- 通过摄像头扫描混凝土配料单，提取骨料类型、水灰比、配比比例等信息
- 支持多种格式的配料单识别
- 当前版本使用模拟OCR接口，可轻松替换为真实OCR服务

### 2. 环境参数采集

- 实时采集温度、湿度、坠落度、钢筋分布密度等参数
- 支持多次采样取平均值，提高数据精度
- 异常值检测与自动校准

### 3. 振捣策略生成

- 基于材料参数和环境条件，计算最优振捣参数
- 为每个振捣点位生成独立的频率、时间、深度和有效半径
- 考虑点位位置、板块尺寸、材料特性等多种因素
- 支持用户手动调整参数，系统会自动优化其他相关参数

### 4. 设备控制与执行

- 精确控制步进电机的转速、方向和运行时间
- 支持顺时针和逆时针旋转，模拟不同振捣方式
- 根据频率自动调整电机速度和步进模式
- 兼容模拟模式和真实GPIO控制模式
- 紧急停止和异常处理机制

### 5. 振捣点位可视化

- 生成振捣点位的三维可视化图形
- 使用颜色映射显示不同频率和时间的点位
- 支持Windows和Ubuntu上的中文字体显示
- 可保存高清图像用于报告和分析
- 支持多角度查看和缩放

### 6. 数据闭环管理

- 将振捣策略和执行数据保存为标准JSON格式
- 记录每个点位的实际执行参数和时间戳
- 支持后续扩展云端上传和远程监控

## 💻 安装与运行

### Windows环境

1. **环境准备**
   ```bash
   # 安装Python 3.7+
   # 安装依赖包
   pip install numpy matplotlib
   ```

2. **运行主程序**
   ```bash
   python smart_vibrator/main.py
   ```

### Ubuntu环境

1. **环境准备**
   ```bash
   # 安装Python和依赖
   sudo apt-get update
   sudo apt-get install python3 python3-pip
   pip3 install numpy matplotlib
   
   # 安装GPIO库（用于控制步进电机）
   sudo apt-get install python3-rpi.gpio
   
   # 安装中文字体（用于可视化）
   sudo apt-get install fonts-wqy-zenhei fonts-wqy-microhei
   ```

2. **运行主程序**
   ```bash
   # 如需使用GPIO控制步进电机，需要root权限
   sudo python3 smart_vibrator/main.py
   
   # 如只需模拟运行
   python3 smart_vibrator/main.py
   ```

## 🔌 硬件连接

### 步进电机连接
- 步进电机驱动器连接到GPIO引脚(18, 23, 24, 25)
- 电源连接到5V和GND

### 传感器连接
- 温湿度传感器: GPIO 17
- 蜂鸣器: GPIO 27
- LED指示灯: GPIO 22

## 📊 使用示例

1. **启动系统**
   ```bash
   python smart_vibrator/main.py
   ```

2. **输入混凝土参数**
   - 系统会提示输入混凝土类型、尺寸等参数
   - 也可以选择使用摄像头扫描配料单

3. **环境参数采集**
   - 系统会自动采集环境参数
   - 也可以手动输入参数

4. **生成振捣策略**
   - 系统会自动计算最优振捣策略
   - 可以查看振捣点位可视化图

5. **执行振捣操作**
   - 选择是否执行实际振捣操作
   - 系统会控制步进电机按照策略执行振捣

6. **查看输出结果**
   - 振捣策略JSON文件：`smart_vibrator/output/vibration_strategy.json`
   - 可视化图像：`smart_vibrator/output/vibration_points.png`

## 🔄 开发路线图

### 已完成
- ✅ 项目基础结构与全流程打通
- ✅ 振捣策略生成模块实现详细策略计算
- ✅ 设备控制模块实现步进电机控制
- ✅ 振捣点位可视化模块实现三维图形生成
- ✅ 跨平台兼容性（Windows和Ubuntu）
- ✅ 数据保存与JSON格式输出
- ✅ 蜂鸣器和LED指示灯控制模块

### 进行中
- 🔄 振捣策略优化算法改进
- 🔄 设备控制精度提升
- 🔄 可视化界面优化

### 计划中
- 📅 对接真实摄像头与OCR识别
- 📅 对接真实环境传感器
- 📅 实现云端数据上传与分析
- 📅 开发Web界面和移动端应用
- 📅 多设备协同作业支持
- 📅 振捣效果预测与模拟

## 🤝 贡献指南

欢迎对项目提出改进建议和贡献代码。请遵循以下步骤：

1. Fork本仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启一个Pull Request

## 📄 许可证

本项目采用MIT许可证 - 详情请参见 [LICENSE](LICENSE) 文件

## 📞 联系方式

如有任何问题或建议，请通过以下方式联系我们：

- 项目维护者: Cai Huayi
- GitHub: [https://github.com/Cai-Huayi](https://github.com/Cai-Huayi)

---

**智能振捣系统** - 让混凝土施工更智能、更高效、更可靠！
