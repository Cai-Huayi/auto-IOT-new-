"""
device_control.py
振捣设备控制与执行模块
根据策略控制步进电机进行振捣操作，并自动计时断电。
参照广联达提供的步进电机控制代码实现。
"""

import time
import sys
# 导入sleep函数，并确保全局可用
from time import sleep as time_sleep

# 确保兼容性
def sleep(seconds):
    """封装sleep函数，确保兼容性"""
    time_sleep(seconds)

# 导入树莓派 GPIO 库用于控制步进电机
import RPi.GPIO as GPIO
print("成功导入 RPi.GPIO 库，使用真实的GPIO控制")

# 步进电机控制参数
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
    GPIO.setmode(GPIO.BCM)  # 将GPIO模式设置为BCM编号
    GPIO.setwarnings(False) # 忽略警告
    for i in glodon_motorPin:
        GPIO.setup(i, GPIO.OUT) # 设置步进电机的所有管脚为输出模式
    
    print("振捣电机初始化完成")
    return True

# 步进电机旋转 - 完全按照官方代码实现
def glodon_rotary(clb_direction, freq_hz=180, duration_s=1):
    """
    控制步进电机旋转
    :param clb_direction: 旋转方向，'a'为逆时针，'c'为顺时针
    :param freq_hz: 振捣频率（Hz）
    :param duration_s: 持续时间（秒）
    """
    # 根据频率调整步进电机速度
    # 将频率转换为每分钟转数，范围控制在5-30之间
    adjusted_rpm = max(5, min(30, freq_hz / 10))  # 限制RPM在安全范围内
    global glodon_rolePerMinute, glodon_stepSpeed
    glodon_rolePerMinute = adjusted_rpm
    glodon_stepSpeed = (60/glodon_rolePerMinute)/glodon_stepsPerRevolution
    
    print(f"\n[电机设置] 频率: {freq_hz}Hz, 转速: {adjusted_rpm}RPM, 步进时间: {glodon_stepSpeed:.6f}s")
    
    # 计算运行时间
    start_time = time.time()
    end_time = start_time + duration_s
    
    # 测试sleep函数
    print("[测试] 测试sleep函数...")
    sleep(0.1)  # 测试sleep函数是否正常工作
    
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
    for i in glodon_motorPin:
        GPIO.output(i, GPIO.LOW) # 设置所有管脚为低电平
    GPIO.cleanup() # 释放资源
    print("电机资源已释放")

def execute_strategy(strategy):
    """
    根据策略执行振捣操作，控制步进电机并自动计时断电。
    :param strategy: dict，包括频率、时间、深度、点位布局
    """
    print("\n=== 初始化振捣电机 ===")
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
    
    # 限制测试时只执行前5个点位
    test_limit = min(5, len(points))
    print(f"[测试模式] 只执行前 {test_limit} 个点位")
    
    for idx, point in enumerate(points[:test_limit]):
        vibration_status["current_point"] = idx
        
        # 兼容旧版点位格式
        if isinstance(point, dict) and "x" in point and "y" in point:
            # 新版点位格式
            point_id = point.get("id", idx+1)
            x, y = point.get("x", 0), point.get("y", 0)
            freq_hz = point.get("freq_hz", base_freq)
            time_s = point.get("time_s", base_time)
            depth_cm = point.get("depth_cm", 40)
            pos = f"P{point_id}"
        else:
            # 旧版点位格式
            pos = chr(ord('A') + idx) if idx < 26 else f"P{idx+1}"
            freq_hz = base_freq
            time_s = base_time
            depth_cm = strategy.get("recommended_depth_cm", 40)
            x, y = idx*10, 0  # 默认坐标
        
        print(f"\n[点位 {pos}] 坐标: ({x}, {y})")
        print(f"  - 振捣频率: {freq_hz} Hz")
        print(f"  - 振捣时间: {time_s} 秒")
        print(f"  - 振捣深度: {depth_cm} cm")
        
        # 模拟正反转交替（每个点位反转）
        direction = 'c' if idx % 2 == 0 else 'a'  # 奇数点位正转，偶数点位反转
        vibration_status["direction"] = direction
        vibration_status["frequency"] = freq_hz
        
        # 运行电机
        print(f"[开始振捣] 点位 {pos}")
        vibration_status["running"] = True
        dir_text = "顺时针" if direction == 'c' else "逆时针"
        print(f"  电机转向: {dir_text}")
        
        # 执行振捣
        glodon_rotary(direction, freq_hz, time_s)
        
        vibration_status["running"] = False
        print(f"[完成振捣] 点位 {pos}\n")
        time.sleep(1)  # 点位间延时
    
    # 释放资源
    destroy()
    print("=== 振捣操作完成 ===")

if __name__ == "__main__":
    # 测试用例
    sample_strategy = {
        "vibration_params": {
            "base_freq_hz": 180,
            "base_time_s": 10,
            "base_depth_cm": 40,
            "base_radius_cm": 25.0
        },
        "points": [
            {"id": 1, "x": 0.0, "y": 0.0, "freq_hz": 190, "time_s": 12, "depth_cm": 35, "radius_cm": 23.5},
            {"id": 2, "x": 0.5, "y": 0.0, "freq_hz": 185, "time_s": 11, "depth_cm": 38, "radius_cm": 23.0},
            {"id": 3, "x": 1.0, "y": 0.0, "freq_hz": 175, "time_s": 10, "depth_cm": 40, "radius_cm": 22.5},
            {"id": 4, "x": 1.5, "y": 0.0, "freq_hz": 170, "time_s": 9, "depth_cm": 42, "radius_cm": 22.0},
            {"id": 5, "x": 2.0, "y": 0.0, "freq_hz": 180, "time_s": 10, "depth_cm": 40, "radius_cm": 22.8}
        ]
    }
    
    # 执行振捣策略
    execute_strategy(sample_strategy)
