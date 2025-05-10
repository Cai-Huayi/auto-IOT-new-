"""
sensor_interface.py
传感器接口模块，封装环境参数传感器的读取函数。
温度传感器使用真实PCF8591模块读取，其他参数仍为模拟数据。
直接使用simulatedTemperatureSensorExperiment.ipynb中的代码实现。
"""
import random
import time
import os
import sys
import math

# 尝试导入必要模块
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
    # 设置 GPIO 模式
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    print("成功导入GPIO模块")
except ImportError:
    GPIO_AVAILABLE = False
    print("导入GPIO模块失败，部分功能将不可用")

# 尝试导入官方PCF8591模块
base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'base')
if os.path.exists(base_dir) and os.path.exists(os.path.join(base_dir, 'PCF8591.py')):
    sys.path.append(base_dir)
    try:
        import PCF8591 as ADC
        print("成功导入官方PCF8591模块")
        USING_OFFICIAL_MODULE = True
    except ImportError as e:
        print(f"导入官方PCF8591模块失败: {e}")
        USING_OFFICIAL_MODULE = False
else:
    USING_OFFICIAL_MODULE = False
    print("未找到官方PCF8591模块，将使用模拟数据")

# 温度传感器配置
glodon_DO = 17  # 温度传感器Do管脚，根据实际连接调整

# 初始化标志
ADC_INITIALIZED = False

# 初始化设置
def glodon_setup():
    """初始化温度传感器设置"""
    global ADC_INITIALIZED
    
    if not USING_OFFICIAL_MODULE:
        return False
    
    try:
        ADC.setup(0x48)  # 设置PCF8591模块地址
        if GPIO_AVAILABLE:
            GPIO.setup(glodon_DO, GPIO.IN)  # 温度传感器DO端口设置为输入模式
        ADC_INITIALIZED = True
        print("温度传感器初始化成功")
        return True
    except Exception as e:
        print(f"温度传感器初始化失败: {e}")
        ADC_INITIALIZED = False
        return False

# 尝试初始化温度传感器
if USING_OFFICIAL_MODULE:
    glodon_setup()

def read_temperature():
    """
    读取温度传感器数据（°C）
    使用simulatedTemperatureSensorExperiment.ipynb中的代码实现
    如果传感器不可用，则返回模拟数据
    """
    # 如果官方模块不可用或未初始化，返回模拟数据
    if not USING_OFFICIAL_MODULE or not ADC_INITIALIZED:
        print("模块未初始化，返回模拟数据")
        return round(random.uniform(15, 35), 1)
    
    try:
        # 直接使用simulatedTemperatureSensorExperiment.ipynb中的代码
        glodon_analogVal = ADC.read(0)  # 读取AIN0上的模拟值
        
        # 转换到 5V 范围
        glodon_Vr = 5 * float(glodon_analogVal) / 255
        
        # 检查分母是否为零
        if (5 - glodon_Vr) <= 0:
            print(f"警告: 电压计算异常(Vr={glodon_Vr}), 使用备用方法")
            # 使用简化的计算方法
            glodon_temp = 25.0  # 默认室温
        else:
            # 计算电阻值
            glodon_Rt = 10000 * glodon_Vr / (5 - glodon_Vr)
            
            # 检查对数参数
            if glodon_Rt <= 0:
                print(f"警告: 电阻值异常(Rt={glodon_Rt}), 使用备用方法")
                glodon_temp = 25.0  # 默认室温
            else:
                try:
                    # 使用NTC热敷电阻公式计算温度
                    glodon_temp = 1/(((math.log(glodon_Rt / 10000)) / 3950) + (1 / (273.15+25)))
                    glodon_temp = glodon_temp - 273.15  # 转换为摄氏度
                except Exception as e:
                    print(f"温度计算错误: {e}")
                    glodon_temp = 25.0  # 默认室温
        
        # 限制在合理范围内
        glodon_temp = max(min(glodon_temp, 50), -10)
        
        # 根据实际温度值和DO端口状态判断温度状态
        # 设置温度阈值为30度，超过这个温度就认为“太热了”
        TEMP_THRESHOLD = 30.0
        
        # 优先使用实际温度值判断
        if glodon_temp > TEMP_THRESHOLD:
            print('\n************')
            print('* It is Too Hot! *')
            print('************\n')
        else:
            print('\n***********')
            print('* Just right \uff0cBetter~ *')
            print('***********\n')
            
        # 如果GPIO可用，也读取DO端口状态（仅用于调试）
        if GPIO_AVAILABLE:
            try:
                glodon_tmp = GPIO.input(glodon_DO)
                print(f"DO端口状态: {'High(1)' if glodon_tmp == 1 else 'Low(0)'}")
            except Exception as gpio_err:
                print(f"GPIO读取错误: {gpio_err}")
        
        # 返回四舍五入到一位小数的温度值
        return round(glodon_temp, 1)
    
    except Exception as e:
        print(f"读取温度传感器错误: {e}")
        # 出错时返回模拟数据
        return round(random.uniform(15, 35), 1)

def read_humidity():
    """模拟读取湿度传感器（%）"""
    return round(random.uniform(50, 80), 1)

def read_slump():
    """模拟读取混凝土坍落度传感器（mm）"""
    return round(random.uniform(140, 220), 0)

def read_rebar_density():
    """模拟读取钢筋分布密度传感器（0~1）"""
    return round(random.uniform(0.2, 0.5), 2)

if __name__ == "__main__":
    print("温度:", read_temperature())
    print("湿度:", read_humidity())
    print("坍落度:", read_slump())
    print("钢筋分布密度:", read_rebar_density())
