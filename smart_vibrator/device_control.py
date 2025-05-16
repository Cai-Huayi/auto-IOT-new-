"""
device_control.py
振捣设备控制与执行模块
根据策略控制步进电机进行振捣操作，并自动计时断电。
参照广联达提供的步进电机控制代码实现。
"""

import time
import sys
# 导入sleep函数，并确保全局可用
from time import sleep

# 严格按照官方示例导入
from utils.led_control import green_on, red_on, all_leds_off
from utils.buzzer_control import buzzer_on, buzzer_off

# 导入树莓派 GPIO 库用于控制步进电机
import Jetson.GPIO as GPIO
print("成功导入 RPi.GPIO 库，使用真实的GPIO控制")

# 步进电机控制参数（严格按照StepperMotorSensor.ipynb）
glodon_motorPin = (18, 23, 24, 25)     # 步进电机管脚对应的GPIO引脚
glodon_rolePerMinute = 15            # 每分钟转数，可以根据振捣频率调整
glodon_stepsPerRevolution = 2048    # 每转一圈的步数，取决于电机类型
glodon_stepSpeed = (60/glodon_rolePerMinute)/glodon_stepsPerRevolution  # 每一步所用的时间

# 振捣状态记录
vibration_status = {
    "running": False,      # 是否正在运行
    "direction": 'c',      # 'c'为顺时针（clockwise），'a'为逆时针（anticlockwise）
    "frequency": 180,      # 振捣频率（Hz）
    "current_point": 0,    # 当前振捣点位
    "total_points": 0,     # 总点位数
    "stop_flag": False     # 停止标志
}

# 初始化设置
def glodon_setup():
    """初始化步进电机控制引脚"""
    GPIO.setmode(GPIO.BCM)  # 将GPIO模式设置为BCM编号，与官方示例一致
    GPIO.setwarnings(False) # 忽略警告
    for i in glodon_motorPin:
        GPIO.setup(i, GPIO.OUT) # 设置步进电机的所有管脚为输出模式
    
    print("振捣电机初始化完成")
    return True

# 单独定义LED和蜂鸣器控制函数，避免多次调用导致冲突
def control_devices(step, idx=0, total=5):
    """
    控制LED和蜂鸣器的状态
    :param step: 控制步骤 "off"=全部关闭, "green"=绿灯亮, "red_buzzer"=红灯亮+蜂鸣器响
    :param idx: 当前循环索引
    :param total: 总循环次数
    """
    try:
        print(f"[设备控制] 正在执行'{step}'操作...")
        
        if step == "off":
            # 确保所有设备都关闭
            all_leds_off()  # 关闭所有LED
            buzzer_off()    # 关闭蜂鸣器
            print("[设备状态] 所有LED和蜂鸣器已关闭")
            
        elif step == "green":
            # 先关闭所有设备，然后打开绿灯
            all_leds_off()
            buzzer_off()
            # 打开绿灯
            green_on()
            print(f"[设备状态] 绿色LED已亮起（循环{idx+1}/{total}）")
            
        elif step == "red_buzzer":
            # 先关闭所有设备，然后打开红灯和蜂鸣器
            all_leds_off()
            time.sleep(0.1)  # 短暂延时确保状态切换
            # 打开红灯和蜂鸣器
            red_on()
            buzzer_on()
            print(f"[设备状态] 红色LED已亮起，蜂鸣器已开启（循环{idx+1}/{total}）")
    
    except Exception as e:
        print(f"[错误] 控制设备时发生错误: {e}")

# 步进电机旋转 - 完全按照官方代码实现
def glodon_rotary(clb_direction, freq_hz=180, duration_s=1):
    """
    控制步进电机旋转
    :param clb_direction: 旋转方向，'a'为逆时针，'c'为顺时针
    :param freq_hz: 振捣频率（Hz）
    :param duration_s: 持续时间（秒）
    """
    # 根据频率调整步进电机速度
    adjusted_rpm = max(5, min(30, freq_hz / 10))  # 限制RPM在安全范围内
    global glodon_rolePerMinute, glodon_stepSpeed
    glodon_rolePerMinute = adjusted_rpm
    glodon_stepSpeed = (60/glodon_rolePerMinute)/glodon_stepsPerRevolution
    
    print(f"\n[电机设置] 频率: {freq_hz}Hz, 转速: {adjusted_rpm}RPM, 步进时间: {glodon_stepSpeed:.6f}s")
    
    # 计算运行时间
    start_time = time.time()
    end_time = start_time + duration_s
    
    # 显示方向
    direction_text = "逆时针" if clb_direction == 'a' else "顺时针"
    print(f"[电机运行] 方向: {direction_text}, 时间: {duration_s}秒")
    
    try:
        # 持续运行指定时间
        while time.time() < end_time:
            # 完全按照官方代码实现
            if clb_direction == 'a':     # 逆时针旋转
                for j in range(4):
                    for i in range(4):
                        GPIO.output(glodon_motorPin[i], 0x99>>j & (0x08>>i))
                    sleep(glodon_stepSpeed)
            elif clb_direction == 'c':    # 顺时针旋转
                for j in range(4):
                    for i in range(4):
                        GPIO.output(glodon_motorPin[i], 0x99<<j & (0x80>>i))
                    sleep(glodon_stepSpeed)
            
            # 每秒显示一次运行状态
            elapsed = time.time() - start_time
            if int(elapsed) != int(elapsed - glodon_stepSpeed * 4):
                remaining = max(0, end_time - time.time())
                progress = min(100, int(elapsed / duration_s * 100))
                sys.stdout.write(f"\r振捣中: {elapsed:.1f}秒/{duration_s}秒 [进度: {progress}%] [频率: {freq_hz}Hz]")
                sys.stdout.flush()
    
    except KeyboardInterrupt:
        print("\n用户中断振捣")
    except Exception as e:
        print(f"\n振捣过程出错: {e}")
        import traceback
        traceback.print_exc()  # 打印详细错误信息
    
    print("\n振捣完成")
    return True

# 释放资源
def destroy():
    """释放电机控制资源"""
    # 确保所有外设关闭 (LED和蜂鸣器由主循环或其自身模块控制，这里主要关注电机)
    # control_devices("off") # 这个调用可以保留，以防万一，但主要清理在main
    
    print("正在停止步进电机...")
    for i in glodon_motorPin:
        try:
            GPIO.output(i, GPIO.LOW) # 设置所有电机管脚为低电平
        except Exception as e:
            print(f"  警告: 关闭电机引脚 {i} 时出错: {e} (可能未初始化或已清理)")
            
    # GPIO.cleanup(glodon_motorPin) # 不在这里进行cleanup，改由main.py统一处理
    # 或者只清理电机相关的引脚，但全局cleanup更推荐
    print("电机引脚已设置为LOW，等待主程序统一cleanup")

def execute_strategy(strategy):
    """
    根据策略执行振捣操作，控制步进电机并自动计时断电。
    :param strategy: dict，包括频率、时间、深度、点位布局
    """
    print("\n=== 初始化振捣电机 ===")
    # 首先确保所有LED和蜂鸣器处于关闭状态
    control_devices("off")
    
    # 初始化电机
    glodon_setup()
    
    # 提取振捣策略中的点位信息
    points = strategy.get("points", [])
    if not points:
        # 兼容旧版策略格式
        points = strategy.get("points_layout", [])
        if not points:
            print("错误：策略中没有点位信息")
            return
    
    # 提取振捣参数
    base_freq = strategy.get("vibration_params", {}).get("base_freq_hz", 180)
    base_time = strategy.get("vibration_params", {}).get("base_time_s", 10)
    
    # 兼容旧版策略格式
    if "recommended_freq_hz" in strategy:
        base_freq = strategy.get("recommended_freq_hz")
    if "recommended_time_s" in strategy:
        base_time = strategy.get("recommended_time_s")
    
    vibration_status["total_points"] = len(points)
    print(f"\n=== 开始振捣操作 (总点位数: {len(points)}) ===")
    
    # 执行最多5个振捣点位，按照用户要求
    num_cycles = 5
    actual_cycles = min(num_cycles, len(points))
    
    for idx, point in enumerate(points[:actual_cycles]):
        vibration_status["current_point"] = idx
        
        # 获取点位信息
        if isinstance(point, dict) and "x" in point and "y" in point:
            point_id = point.get("id", idx + 1)
            x, y = point.get("x", 0), point.get("y", 0)
            freq_hz = point.get("freq_hz", base_freq)
            time_s = point.get("time_s", base_time)
            depth_cm = point.get("depth_cm", 40)
            pos = f"P{point_id}"
        else:
            pos = chr(ord('A') + idx) if idx < 26 else f"P{idx + 1}"
            freq_hz = base_freq
            time_s = base_time
            depth_cm = strategy.get("recommended_depth_cm", 40)
            x, y = idx * 10, 0
        
        print(f"\n[循环 {idx + 1}/{actual_cycles}]")
        print(f"  正在模拟步进电机移动到点位 {pos} 坐标({x}, {y})...")
        
        # 1. 确保所有LED和蜂鸣器关闭
        control_devices("off")
        
        # 模拟电机移动时间
        time.sleep(3)
        
        # 2. 到达位置后，打开绿灯
        print(f"  步进电机已到达点位 {pos}.")
        control_devices("green", idx, actual_cycles)
        
        # 给较长时间观察绿灯(表示已就位)
        time.sleep(3)  # 延长到3秒，让绿灯亮的时间更长

        print(f"\n[开始振捣] 点位 {pos}")
        print(f"  - 振捣频率: {freq_hz} Hz")
        print(f"  - 振捣时间: {time_s} 秒")
        print(f"  - 振捣深度: {depth_cm} cm")
        
        # 根据奇偶数确定旋转方向
        direction = 'c' if idx % 2 == 0 else 'a'
        vibration_status["direction"] = direction
        vibration_status["frequency"] = freq_hz
        
        # 3. 开始振捣，红灯亮，蜂鸣器响
        vibration_status["running"] = True
        dir_text = "顺时针" if direction == 'c' else "逆时针"
        print(f"  电机转向: {dir_text}.")
        control_devices("red_buzzer", idx, actual_cycles)
        
        # 执行振捣
        glodon_rotary(direction, freq_hz, time_s)
        
        # 4. 振捣结束，关闭红灯和蜂鸣器
        vibration_status["running"] = False
        print(f"\n[完成振捣] 点位 {pos}.")
        control_devices("off")
        
        # 添加短暂暂停，让所有设备都保持关闭状态一小段时间
        time.sleep(1)
        
        if idx < actual_cycles - 1:
            print(f"  准备下一个循环...")
            # 在下一循环开始前，先让绿灯亮一段时间，表示准备就绪
            control_devices("green", idx, actual_cycles)
            time.sleep(2)  # 绿灯亮2秒表示准备就绪
            control_devices("off")  # 然后再次关闭所有设备
            time.sleep(0.5)  # 短暂暂停
        else:
            print(f"  全部 {actual_cycles} 个循环已完成.")
            # 最后一个循环结束后，绿灯亮起3秒表示全部完成
            control_devices("green", idx, actual_cycles)
            time.sleep(3)
            control_devices("off")
    
    # 释放资源
    destroy()
    print("=== 振捣操作完成 ===")

if __name__ == "__main__":
    # 测试用例
    sample_strategy = {
        "vibration_params": {
            "base_freq_hz": 180,
            "base_time_s": 5,  # 调整为更短的时间用于测试
            "base_depth_cm": 40,
            "base_radius_cm": 25.0
        },
        "points": [
            {"id": 1, "x": 0.0, "y": 0.0, "freq_hz": 190, "time_s": 5, "depth_cm": 35, "radius_cm": 23.5},
            {"id": 2, "x": 0.5, "y": 0.0, "freq_hz": 185, "time_s": 5, "depth_cm": 38, "radius_cm": 23.0},
            {"id": 3, "x": 1.0, "y": 0.0, "freq_hz": 175, "time_s": 5, "depth_cm": 40, "radius_cm": 22.5},
            {"id": 4, "x": 1.5, "y": 0.0, "freq_hz": 170, "time_s": 5, "depth_cm": 42, "radius_cm": 22.0},
            {"id": 5, "x": 2.0, "y": 0.0, "freq_hz": 180, "time_s": 5, "depth_cm": 40, "radius_cm": 22.8}
        ]
    }
    
    # 执行振捣策略
    execute_strategy(sample_strategy)
