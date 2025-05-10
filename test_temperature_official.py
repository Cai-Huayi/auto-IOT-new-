#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
温度传感器测试程序 - 使用simulatedTemperatureSensorExperiment.ipynb中的代码

此程序用于测试PCF8591模块连接的温度传感器
使用base目录中的官方PCF8591.py模块和simulatedTemperatureSensorExperiment.ipynb中的代码
"""

import os
import sys
import time
import math
import random

# 添加base目录到路径
base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'base')
if os.path.exists(base_dir):
    sys.path.append(base_dir)
    try:
        import PCF8591 as ADC
        print("成功导入PCF8591模块")
    except ImportError as e:
        print(f"导入PCF8591模块失败: {e}")
        print("请确保base目录中包含PCF8591.py文件")
        sys.exit(1)
else:
    print(f"未找到base目录: {base_dir}")
    sys.exit(1)

# 尝试导入GPIO模块
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
    # 设置GPIO模式
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    print("成功导入GPIO模块")
except ImportError:
    GPIO_AVAILABLE = False
    print("导入GPIO模块失败，数字温度检测功能将不可用")

# 温度传感器配置
glodon_DO = 17  # 温度传感器Do管脚，与sensor_interface.py保持一致

# 初始化PCF8591
def setup():
    try:
        ADC.setup(0x48)  # 设置PCF8591模块地址
        if GPIO_AVAILABLE:
            GPIO.setup(glodon_DO, GPIO.IN)  # 温度传感器DO端口设置为输入模式
        print("PCF8591初始化成功，地址: 0x48")
        return True
    except Exception as e:
        print(f"PCF8591初始化失败: {e}")
        return False

# 打印出温度传感器的提示信息
def glodon_Print(x):
    if x == 1:     # 正合适
        print('')
        print('***********')
        print('* Just right ，Better~ *')
        print('***********')
        print('')
    if x == 0:    # 太热了
        print('')
        print('************')
        print('* It is Too Hot! *')
        print('************')
        print('')

# 读取温度 - 使用simulatedTemperatureSensorExperiment.ipynb中的代码
def read_temperature():
    try:
        # 读取AIN0上的模拟值
        glodon_analogVal = ADC.read(0)
        
        # 转换到5V范围
        glodon_Vr = 5 * float(glodon_analogVal) / 255
        
        # 检查分母是否为零
        if (5 - glodon_Vr) <= 0:
            print(f"警告: 电压计算异常(Vr={glodon_Vr})")
            return 25.0, glodon_analogVal  # 返回默认室温和原始值
        
        # 计算电阻值
        glodon_Rt = 10000 * glodon_Vr / (5 - glodon_Vr)
        
        # 检查对数参数
        if glodon_Rt <= 0:
            print(f"警告: 电阻值异常(Rt={glodon_Rt})")
            return 25.0, glodon_analogVal  # 返回默认室温和原始值
        
        # 使用NTC热敏电阻公式计算温度
        try:
            glodon_temp = 1/(((math.log(glodon_Rt / 10000)) / 3950) + (1 / (273.15+25)))
            glodon_temp = glodon_temp - 273.15  # 转换为摄氏度
            
            # 限制在合理范围内
            glodon_temp = max(min(glodon_temp, 50), -10)
            
            return glodon_temp, glodon_analogVal
        except Exception as e:
            print(f"温度计算错误: {e}")
            return 25.0, glodon_analogVal  # 返回默认室温和原始值
    
    except Exception as e:
        print(f"读取温度传感器错误: {e}")
        return 25.0, 0  # 返回默认室温和0

# 测试所有通道
def test_all_channels():
    print("\n测试所有通道...")
    for i in range(4):
        value = ADC.read(i)
        print(f"通道 {i}: {value}")
    print("测试完成\n")

# 连续监测温度 - 使用simulatedTemperatureSensorExperiment.ipynb中的循环函数
def monitor_temperature():
    print("\n开始连续监测温度，按Ctrl+C停止...")
    print("时间\t\tADC值\t温度(°C)\t状态")
    print("-" * 50)
    
    # 记录数据
    readings = []
    adc_values = []
    temps = []
    
    try:
        start_time = time.time()
        glodon_status = 1   # 状态值
        glodon_tmp = 1      # 当前值
        
        while True:
            # 读取温度
            temp, value = read_temperature()
            elapsed = time.time() - start_time
            
            # 记录数据
            readings.append((elapsed, value, temp))
            adc_values.append(value)
            temps.append(temp)
            
            # 读取数字端口状态
            status_text = "未知"
            if GPIO_AVAILABLE:
                try:
                    glodon_tmp = GPIO.input(glodon_DO)  # 读取温度传感器数字端口
                    
                    if glodon_tmp != glodon_status:  # 判断状态值发生改变
                        glodon_Print(glodon_tmp)      # 打印出温度传感器的提示信息
                        glodon_status = glodon_tmp    # 更新状态值
                    
                    status_text = "正合适" if glodon_tmp == 1 else "太热了"
                except Exception as gpio_err:
                    print(f"GPIO读取错误: {gpio_err}")
            
            # 显示数据
            print(f"{elapsed:.1f}s\t\t{value}\t{temp:.1f}°C\t\t{status_text}")
            
            time.sleep(0.2)  # 延时200ms，与原始代码保持一致
    
    except KeyboardInterrupt:
        print("\n监测已停止")
        
        # 显示统计信息
        print("\n监测统计:")
        print(f"样本数: {len(readings)}")
        print(f"ADC值 - 平均: {sum(adc_values)/len(adc_values):.1f}, 最小: {min(adc_values):.1f}, 最大: {max(adc_values):.1f}")
        print(f"温度 - 平均: {sum(temps)/len(temps):.1f}°C, 最小: {min(temps):.1f}°C, 最大: {max(temps):.1f}°C")

if __name__ == "__main__":
    print("温度传感器测试程序 - 使用simulatedTemperatureSensorExperiment.ipynb中的代码")
    print("----------------------------------")
    
    # 初始化PCF8591
    if not setup():
        print("初始化失败，退出测试")
        sys.exit(1)
    
    # 显示测试菜单
    print("\n请选择测试选项：")
    print("1. 测试所有通道")
    print("2. 连续监测温度传感器")
    print("3. 退出")
    
    while True:
        try:
            choice = int(input("\n请输入选项编号: "))
            
            if choice == 1:
                test_all_channels()
            elif choice == 2:
                monitor_temperature()
            elif choice == 3:
                print("退出测试程序")
                break
            else:
                print("无效选项，请重新输入")
        except ValueError:
            print("输入错误，请输入数字")
        except KeyboardInterrupt:
            print("\n用户中断，退出程序")
            break
    
    print("\n测试结束，再见！")
