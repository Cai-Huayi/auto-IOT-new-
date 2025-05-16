#!/usr/bin/env python3
"""
紧急重置GPIO状态的工具
适用于Jetson Nano
"""

import Jetson.GPIO as GPIO
import time
import os
import sys

def reset_gpio():
    print("=== 紧急重置GPIO状态 ===")
    
    # 先尝试完全清理
    try:
        GPIO.cleanup()
        print("已清理所有GPIO引脚")
    except:
        print("GPIO清理失败，继续执行...")
    
    # 设置BCM模式
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # 目标引脚
    pins = [17, 18]  # 蜂鸣器和LED的引脚
    
    # 尝试重置引脚状态
    print("正在重置引脚:", pins)
    
    # Jetson Nano特殊处理
    for pin in pins:
        try:
            # 设置为输出
            GPIO.setup(pin, GPIO.OUT)
            
            # 反复切换状态尝试复位
            print(f"重置引脚 {pin}...")
            for state in [GPIO.HIGH, GPIO.LOW, GPIO.HIGH, GPIO.LOW, GPIO.HIGH]:
                GPIO.output(pin, state)
                time.sleep(0.2)
                
            # 蜂鸣器在17号引脚，需要HIGH关闭 (假设低电平触发)
            # 红色LED在17号引脚，也假设低电平触发 (LOW亮, HIGH灭)
            if pin == 17:
                GPIO.output(pin, GPIO.HIGH) # 关闭蜂鸣器和红灯
                print(f"引脚 {pin} (蜂鸣器/红灯) 设置为HIGH (关闭)")
            else: # pin == 18 (绿色LED)
                GPIO.output(pin, GPIO.LOW) # 关闭绿灯 (假设高电平触发)
                print(f"引脚 {pin} (绿灯) 设置为LOW (关闭)")
                
        except Exception as e:
            print(f"重置引脚 {pin} 失败: {e}")
    
    # # 额外尝试PWM控制 (暂时注释掉，因为它之前报错)
    # try:
    #     print("尝试PWM控制蜂鸣器...")
    #     pwm = GPIO.PWM(17, 100)
    #     pwm.start(0)
    #     time.sleep(0.5)
    #     pwm.stop()
    # except Exception as e: # 更具体地捕获可能的PWM错误
    #     print(f"PWM控制尝试失败: {e}")
    
    # 再次清理所有资源
    try:
        # 先设置默认状态
        GPIO.output(17, GPIO.HIGH)  # 蜂鸣器/红灯 关闭
        GPIO.output(18, GPIO.LOW)   # 绿灯 关闭
        
        # 等待状态稳定
        time.sleep(1)
        
        # 最后清理资源
        GPIO.cleanup()
        print("已完成引脚状态重置")
    except:
        print("最终清理失败")

if __name__ == "__main__":
    # 提示可能需要sudo权限
    if os.geteuid() != 0:
        print("警告: 此脚本可能需要root权限才能完全控制GPIO")
        print("建议使用 'sudo python3 reset_gpio.py' 运行")
        
    try:
        reset_gpio()
        print("GPIO重置完成")
    except Exception as e:
        print(f"重置过程出错: {e}")
        sys.exit(1)
    
    print("\n如果设备仍然工作，请尝试以下措施:")
    print("1. 使用sudo权限运行此脚本")
    print("2. 检查硬件连接，确认是否有电阻或其他电路影响")
    # print("3. 尝试安装Jetson.GPIO库替代RPi.GPIO") # 这一条现在已经做了
    print("3. 仔细检查引脚定义和LED/蜂鸣器的触发电平（高电平亮还是低电平亮）")
    print("4. 重启Jetson Nano") 