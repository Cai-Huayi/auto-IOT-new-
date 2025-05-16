import Jetson.GPIO as GPIO
import time

# 修改为BCM模式下的引脚编号
pin_R = 17  # 红色LED, BCM 17, 与蜂鸣器共享, 假设低电平亮
pin_G = 18  # 绿色LED, BCM 18, 假设高电平亮

def setup_led():
    '''初始化双色LED引脚（适用于Jetson Nano）'''
    # GPIO模式应由主程序或更高级别的模块统一设置，这里不再重复设置
    # if GPIO.getmode() is None:
    #     GPIO.setmode(GPIO.BCM)
        
    GPIO.setwarnings(False)
    
    GPIO.setup(pin_R, GPIO.OUT)
    GPIO.setup(pin_G, GPIO.OUT)
    
    # 初始状态：确保所有LED都关闭
    # 红灯低电平亮，所以要输出高电平关闭
    GPIO.output(pin_R, GPIO.HIGH)
    # 绿灯高电平亮，所以要输出低电平关闭
    GPIO.output(pin_G, GPIO.LOW)
    
    print(f"双色LED初始化完成（Jetson Nano模式）。红色: Pin BCM-{pin_R} (设为HIGH关闭), 绿色: Pin BCM-{pin_G} (设为LOW关闭)")

def green_on():
    '''打开绿色LED，关闭红色LED'''
    # 关闭红色LED (红灯低电平亮 -> HIGH关闭)
    GPIO.output(pin_R, GPIO.HIGH)
    # 打开绿色LED (绿灯高电平亮 -> HIGH打开)
    GPIO.output(pin_G, GPIO.HIGH)
    # print("绿色LED亮起, 红色LED熄灭")

def red_on(): # 这个函数现在同时意味着蜂鸣器响
    '''打开红色LED，关闭绿色LED'''
    # 关闭绿色LED (绿灯高电平亮 -> LOW关闭)
    GPIO.output(pin_G, GPIO.LOW)
    # 打开红色LED (红灯低电平亮 -> LOW打开)
    GPIO.output(pin_R, GPIO.LOW)
    # print("红色LED亮起, 绿色LED熄灭")

def all_leds_off():
    '''关闭所有LED'''
    # 关闭红色LED (红灯低电平亮 -> HIGH关闭)
    GPIO.output(pin_R, GPIO.HIGH)
    # 关闭绿色LED (绿灯高电平亮 -> LOW关闭)
    GPIO.output(pin_G, GPIO.LOW)
    # print("所有LED已关闭")

def cleanup_led():
    '''释放LED使用的GPIO资源'''
    all_leds_off()
    # GPIO.cleanup([pin_R, pin_G]) # GPIO.cleanup() 应该在主程序末尾统一调用
    print("LED GPIO已设置为关闭状态，等待主程序统一cleanup")

if __name__ == "__main__":
    try:
        GPIO.setmode(GPIO.BCM) # __main__ 测试时需要设置模式
        setup_led()
        
        print("\n测试绿色LED (5秒)...")
        green_on()
        time.sleep(5)
        
        print("\n测试红色LED (5秒)...")
        red_on()
        time.sleep(5)
        
        all_leds_off()
        print("\nLED测试完成")
        
    except KeyboardInterrupt:
        print("用户中断测试")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        print("清理测试环境...")
        all_leds_off() # 确保关闭
        GPIO.cleanup([pin_R, pin_G]) # 单独测试时清理
        print("测试清理完成") 