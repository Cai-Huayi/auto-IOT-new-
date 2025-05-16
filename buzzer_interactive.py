#!/usr/bin/env python3
"""
蜂鸣器和LED交互式控制工具
允许用户通过命令行控制蜂鸣器和LED，找出能够彻底关闭蜂鸣器的命令组合
"""

import Jetson.GPIO as GPIO
import time
import sys
import os

# BCM引脚定义
BUZZER_PIN = 17  # 蜂鸣器在BCM 17上
RED_LED_PIN = 17 # 红色LED与蜂鸣器共用BCM 17
GREEN_LED_PIN = 18 # 绿色LED在BCM 18上

# 确保包含项目模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 尝试导入项目模块
try:
    from smart_vibrator.utils.led_control import all_leds_off, green_on, red_on
    from smart_vibrator.utils.buzzer_control import buzzer_off, buzzer_on
    from smart_vibrator.device_control import control_devices
    modules_imported = True
    print("成功导入项目模块")
except Exception as e:
    modules_imported = False
    print(f"导入项目模块失败: {e}")
    print("将仅使用基本GPIO控制")

def init_gpio():
    """初始化GPIO"""
    try:
        # 清理可能的已有设置
        GPIO.cleanup()
        print("已清理现有GPIO设置")
    except:
        pass
    
    # 设置GPIO模式
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # 设置引脚
    GPIO.setup(BUZZER_PIN, GPIO.OUT)
    GPIO.setup(GREEN_LED_PIN, GPIO.OUT)
    
    # 初始状态 - 蜂鸣器和LED关闭
    GPIO.output(BUZZER_PIN, GPIO.HIGH)  # 假设HIGH关闭蜂鸣器
    GPIO.output(GREEN_LED_PIN, GPIO.LOW)  # 假设LOW关闭绿灯
    
    print("GPIO已初始化，引脚状态设置为：")
    print(f"  蜂鸣器/红灯 (BCM {BUZZER_PIN}): HIGH (应关闭)")
    print(f"  绿灯 (BCM {GREEN_LED_PIN}): LOW (应关闭)")

def execute_command(cmd):
    """执行命令"""
    global modules_imported
    
    cmd = cmd.strip().lower()
    
    # 基本GPIO命令
    if cmd == "1" or cmd == "buzzer_high":
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
        print(f"蜂鸣器 (BCM {BUZZER_PIN}) 已设置为 HIGH")
        
    elif cmd == "2" or cmd == "buzzer_low":
        GPIO.output(BUZZER_PIN, GPIO.LOW)
        print(f"蜂鸣器 (BCM {BUZZER_PIN}) 已设置为 LOW")
        
    elif cmd == "3" or cmd == "green_high":
        GPIO.output(GREEN_LED_PIN, GPIO.HIGH)
        print(f"绿灯 (BCM {GREEN_LED_PIN}) 已设置为 HIGH")
        
    elif cmd == "4" or cmd == "green_low":
        GPIO.output(GREEN_LED_PIN, GPIO.LOW)
        print(f"绿灯 (BCM {GREEN_LED_PIN}) 已设置为 LOW")
        
    elif cmd == "5" or cmd == "reset":
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
        GPIO.output(GREEN_LED_PIN, GPIO.LOW)
        print("已重置所有引脚状态")
        
    elif cmd == "6" or cmd == "toggle":
        # 切换引脚状态
        for _ in range(3):
            GPIO.output(BUZZER_PIN, GPIO.LOW)
            GPIO.output(GREEN_LED_PIN, GPIO.HIGH)
            time.sleep(0.3)
            GPIO.output(BUZZER_PIN, GPIO.HIGH)
            GPIO.output(GREEN_LED_PIN, GPIO.LOW)
            time.sleep(0.3)
        print("已执行状态切换序列")
    
    # 项目模块命令 - 仅当成功导入模块时可用
    elif modules_imported:
        if cmd == "7" or cmd == "buzzer_off":
            buzzer_off()
            print("已执行 buzzer_off()")
            
        elif cmd == "8" or cmd == "buzzer_on":
            buzzer_on()
            print("已执行 buzzer_on()")
            
        elif cmd == "9" or cmd == "all_leds_off":
            all_leds_off()
            print("已执行 all_leds_off()")
            
        elif cmd == "10" or cmd == "green_on":
            green_on()
            print("已执行 green_on()")
            
        elif cmd == "11" or cmd == "red_on":
            red_on()
            print("已执行 red_on()")
            
        elif cmd == "12" or cmd == "dev_off":
            control_devices("off")
            print("已执行 control_devices(\"off\")")
            
        elif cmd == "13" or cmd == "dev_green":
            control_devices("green")
            print("已执行 control_devices(\"green\")")
            
        elif cmd == "14" or cmd == "dev_red_buzzer":
            control_devices("red_buzzer")
            print("已执行 control_devices(\"red_buzzer\")")
            
        elif cmd == "15" or cmd == "green_buzzer_off":
            # 特殊组合 - 先green_on再buzzer_off
            green_on()
            time.sleep(0.3)
            buzzer_off()
            print("已执行 green_on() 然后 buzzer_off()")
            
        elif cmd == "16" or cmd == "off_green_off":
            # 特殊组合 - 先all_off再green再all_off
            all_leds_off()
            buzzer_off()
            time.sleep(0.3)
            green_on()
            time.sleep(0.3)
            all_leds_off()
            buzzer_off()
            print("已执行 all_leds_off() + buzzer_off() 然后 green_on() 然后 all_leds_off() + buzzer_off()")
            
        else:
            print(f"未知命令: {cmd}")
    else:
        print(f"未知命令或模块未导入: {cmd}")
        print("只能使用基本GPIO命令(1-6)")

def show_menu():
    """显示命令菜单"""
    print("\n======= 蜂鸣器和LED控制菜单 =======")
    print("基本GPIO命令:")
    print("  1. buzzer_high - 设置蜂鸣器/红灯引脚为HIGH")
    print("  2. buzzer_low  - 设置蜂鸣器/红灯引脚为LOW")
    print("  3. green_high  - 设置绿灯引脚为HIGH")
    print("  4. green_low   - 设置绿灯引脚为LOW")
    print("  5. reset       - 重置所有引脚状态")
    print("  6. toggle      - 执行状态切换序列")
    
    global modules_imported
    if modules_imported:
        print("\n项目模块命令:")
        print("  7. buzzer_off   - 执行buzzer_off()")
        print("  8. buzzer_on    - 执行buzzer_on()")
        print("  9. all_leds_off - 执行all_leds_off()")
        print("  10. green_on     - 执行green_on()")
        print("  11. red_on       - 执行red_on()")
        print("  12. dev_off      - 执行control_devices(\"off\")")
        print("  13. dev_green    - 执行control_devices(\"green\")")
        print("  14. dev_red_buzzer - 执行control_devices(\"red_buzzer\")")
        print("  15. green_buzzer_off - 执行green_on()然后buzzer_off()")
        print("  16. off_green_off - 执行all+buzzer关闭->绿灯打开->all+buzzer关闭")
    
    print("\n命令:")
    print("  help  - 显示此菜单")
    print("  exit  - 退出程序")
    print("=====================================")

def main():
    # 初始化
    init_gpio()
    
    # 显示菜单
    show_menu()
    
    # 主循环
    try:
        while True:
            cmd = input("\n请输入命令: ")
            
            if cmd.lower() == "exit":
                break
            elif cmd.lower() == "help":
                show_menu()
            else:
                execute_command(cmd)
                
    except KeyboardInterrupt:
        print("\n用户中断程序")
    finally:
        # 清理GPIO
        try:
            GPIO.output(BUZZER_PIN, GPIO.HIGH)  # 确保蜂鸣器关闭
            GPIO.output(GREEN_LED_PIN, GPIO.LOW)  # 确保绿灯关闭
            time.sleep(0.5)
            GPIO.cleanup()
            print("\nGPIO资源已清理")
        except:
            pass
        
        print("程序已退出")

if __name__ == "__main__":
    # 检查是否以root权限运行
    if os.geteuid() != 0:
        print("警告: 此脚本需要root权限才能控制GPIO")
        print("请使用 'sudo python3 buzzer_interactive.py' 运行\n")
        exit(1)
    
    main() 