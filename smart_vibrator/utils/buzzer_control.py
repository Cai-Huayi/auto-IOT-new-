import Jetson.GPIO as GPIO
import time

# 修改为BCM模式下的引脚编号
glodon_Buzzer = 17    # 使用BCM 17（与红色LED相同，两者关联, 假设低电平响）

def setup_buzzer(pin=glodon_Buzzer):
    '''初始化蜂鸣器GPIO引脚（适用于Jetson Nano）'''
    global glodon_BuzzerPin                
    glodon_BuzzerPin = pin
    
    # GPIO模式应由主程序或更高级别的模块统一设置
    # if GPIO.getmode() is None:
    #     GPIO.setmode(GPIO.BCM)
    
    GPIO.setwarnings(False)
    GPIO.setup(glodon_BuzzerPin, GPIO.OUT)
    
    # 初始状态：确保蜂鸣器关闭 (低电平响 -> HIGH关闭)
    GPIO.output(glodon_BuzzerPin, GPIO.HIGH)
    
    print(f"蜂鸣器初始化完成（Jetson Nano模式），使用引脚 BCM-{glodon_BuzzerPin}, 已设置为HIGH (关闭状态)")

#  打开蜂鸣器
def buzzer_on():
    '''打开蜂鸣器'''
    GPIO.output(glodon_BuzzerPin, GPIO.LOW)  # 低电平触发，使其发声
    # print("蜂鸣器已打开")

# 关闭蜂鸣器
def buzzer_off():
    '''关闭蜂鸣器'''
    GPIO.output(glodon_BuzzerPin, GPIO.HIGH) # 高电平关闭
    # print("蜂鸣器已关闭")

def cleanup_buzzer():
    '''释放蜂鸣器使用的GPIO资源'''
    buzzer_off() # 确保蜂鸣器关闭
    # GPIO.cleanup(glodon_BuzzerPin) # GPIO.cleanup() 应该在主程序末尾统一调用
    print(f"蜂鸣器GPIO已设置为关闭状态，等待主程序统一cleanup")

if __name__ == "__main__":
    try:
        GPIO.setmode(GPIO.BCM) # __main__ 测试时需要设置模式
        setup_buzzer()
        print("\n测试蜂鸣器，持续3秒...")
        buzzer_on()
        time.sleep(3)
        buzzer_off()
        print("蜂鸣器测试完成")
    except KeyboardInterrupt:
        print("用户中断测试")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        print("清理测试环境...")
        buzzer_off() #确保关闭
        GPIO.cleanup(glodon_BuzzerPin) # 单独测试时清理
        print("测试清理完成") 