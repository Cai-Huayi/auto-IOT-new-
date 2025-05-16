#!/usr/bin/env python3
"""
紧急关闭蜂鸣器的独立脚本
尝试多种方法确保蜂鸣器关闭
"""

import Jetson.GPIO as GPIO
import time
import sys
import os

# BCM引脚定义
BUZZER_PIN = 17  # 蜂鸣器在BCM 17上
RED_LED_PIN = 17 # 红色LED与蜂鸣器共用BCM 17
GREEN_LED_PIN = 18 # 绿色LED在BCM 18上

def reset_gpio():
    print("\n===== 开始紧急关闭蜂鸣器程序 =====")
    
    try:
        # 彻底清理GPIO资源
        GPIO.cleanup()
        print("已清理所有GPIO资源")
    except:
        print("GPIO清理失败，继续执行...")
    
    # 设置GPIO模式
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    print("GPIO模式已设置为BCM")
    
    # 方法1: 直接控制GPIO
    print("\n[方法1] 直接控制GPIO...")
    try:
        # 设置引脚模式并初始化
        GPIO.setup(BUZZER_PIN, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(GREEN_LED_PIN, GPIO.OUT, initial=GPIO.LOW)
        
        # 确保设置生效
        time.sleep(0.5)
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
        GPIO.output(GREEN_LED_PIN, GPIO.LOW)
        print("  引脚状态已设置：蜂鸣器(17)=HIGH，绿灯(18)=LOW")
    except Exception as e:
        print(f"  方法1失败: {e}")

    # 方法2: 引脚状态转换序列
    print("\n[方法2] 尝试引脚状态转换序列...")
    try:
        # 初始化
        GPIO.setup(BUZZER_PIN, GPIO.OUT)
        GPIO.setup(GREEN_LED_PIN, GPIO.OUT)
        
        # 状态转换序列
        print("  执行状态转换序列...")
        for _ in range(3):
            # 切换到一个状态
            GPIO.output(BUZZER_PIN, GPIO.LOW)
            GPIO.output(GREEN_LED_PIN, GPIO.HIGH)
            time.sleep(0.3)
            
            # 切换回安全状态
            GPIO.output(BUZZER_PIN, GPIO.HIGH)
            GPIO.output(GREEN_LED_PIN, GPIO.LOW)
            time.sleep(0.3)
        
        print("  状态转换序列已完成")
    except Exception as e:
        print(f"  方法2失败: {e}")
    
    # 方法3: 从smart_vibrator中导入模块并使用其函数
    print("\n[方法3] 尝试使用smart_vibrator模块的函数...")
    try:
        # 添加父目录到Python路径以便导入模块
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # 尝试导入所需模块
        try:
            from smart_vibrator.utils.led_control import all_leds_off, green_on
            from smart_vibrator.utils.buzzer_control import buzzer_off
            from smart_vibrator.device_control import control_devices
            
            print("  模块导入成功")
            
            # 尝试使用多种组合
            print("  尝试all_leds_off() + buzzer_off()...")
            all_leds_off()
            buzzer_off()
            time.sleep(0.5)
            
            print("  尝试green_on() + buzzer_off()...")
            green_on()
            buzzer_off()
            time.sleep(0.5)
            
            print("  尝试control_devices(\"off\")...")
            control_devices("off")
            time.sleep(0.5)
            
            print("  尝试control_devices(\"green\") + control_devices(\"off\")...")
            control_devices("green")
            time.sleep(0.5)
            control_devices("off")
            
            print("  模块函数调用完成")
        except Exception as e:
            print(f"  导入或使用模块失败: {e}")
    except Exception as e:
        print(f"  方法3失败: {e}")

    # 最终确保引脚状态
    try:
        # 再次设置安全状态
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
        GPIO.output(GREEN_LED_PIN, GPIO.LOW)
        
        # 等待并清理
        time.sleep(1)
        GPIO.cleanup()
        print("\n所有GPIO资源已清理")
    except Exception as e:
        print(f"最终清理失败: {e}")
    
    print("\n===== 紧急关闭蜂鸣器程序结束 =====")
    print("如果有方法成功关闭了蜂鸣器，请记下是哪一步。")

if __name__ == "__main__":
    # 检查是否以root权限运行
    if os.geteuid() != 0:
        print("警告: 此脚本需要root权限才能控制GPIO")
        print("请使用 'sudo python3 buzzer_emergency_off.py' 运行\n")
        exit(1)
    
    reset_gpio() 