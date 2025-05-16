"""
main.py
主程序调度入口，串联各模块实现智能振捣全流程。
"""
import time
import os
import json

import Jetson.GPIO as GPIO # Added for global GPIO cleanup if needed, and initial mode setting
from vibration_strategy import generate_strategy
from device_control import execute_strategy, control_devices # 导入control_devices函数以便直接使用
from cloud_upload import upload_data
from utils.config import get_config
from utils.sensor_interface import read_temperature, read_humidity, read_slump, read_rebar_density
from utils.camera_ocr import ocr_extract_material_info
from visualize_points import visualize_vibration_points, generate_vibration_excel
from utils.led_control import setup_led, cleanup_led, all_leds_off # cleanup_led might not be needed if global cleanup is used
from utils.buzzer_control import setup_buzzer, cleanup_buzzer, buzzer_off # cleanup_buzzer might not be needed


def main():
    config = get_config()
    print("[系统配置]", config)

    # === GPIO和外设初始化 ===
    print("\n=== GPIO 和外设初始化 ===")
    try:
        # 1. 设置GPIO模式 (仅一次)
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        print("[GPIO] 模式设置为 BCM，已关闭警告")
        
        # 1.5 首先设置关键引脚状态
        print("[紧急关闭] 直接设置关键引脚状态...")
        # 设置蜂鸣器/红灯引脚(BCM 17)为HIGH
        GPIO.setup(17, GPIO.OUT)
        GPIO.output(17, GPIO.HIGH)
        # 设置绿灯引脚(BCM 18)为HIGH
        GPIO.setup(18, GPIO.OUT)
        GPIO.output(18, GPIO.HIGH)
        time.sleep(0.5)  # 给一点时间确保设置生效
        # 如果蜂鸣器通过命令2已经打开，此时必须通过命令1才能关闭它
        GPIO.output(17, GPIO.HIGH) # 再次确认
        print("[紧急关闭] 已设置蜂鸣器引脚为HIGH, 绿灯引脚为HIGH，蜂鸣器应该已关闭")

        # 2. 初始化LED模块
        setup_led()
        
        # 3. 初始化蜂鸣器模块
        setup_buzzer()
        
        # 4. 确保状态正确
        print("[初始化关闭] 再次确保所有设备处于期望状态...")
        control_devices("off")  # 通过标准函数确保所有设备关闭
        
        led_initialized = True
        buzzer_initialized = True
        print("[初始化] LED和蜂鸣器模块设置完成。")
        
        # 注意: 步进电机的 glodon_setup() 会在 execute_strategy 内部被调用
        # 它也会设置自己的GPIO引脚，并应使用已设置的BCM模式

    except Exception as e:
        print(f"[严重错误] 外设初始化失败: {e}")
        print("       程序可能无法正常工作。请检查硬件连接和Jetson.GPIO库。")
        # 在这里决定是否要退出或尝试继续
        # return # 例如，如果初始化失败则退出
        # 为了调试，我们暂时允许继续，但实际应用中应处理此错误
        led_initialized = False
        buzzer_initialized = False

    try:
        print("\n=== [1] 混凝土材料参数识别 ===")
        material_params = ocr_extract_material_info()
        print("材料参数:", material_params)

        print("\n=== [2] 环境参数采集 ===")
        
        # 多次读取温度并取平均值
        print("温度数据采集中...")
        temp_readings = []
        for i in range(10):
            temp = read_temperature()
            temp_readings.append(temp)
            print(f"  温度读数 #{i+1}: {temp:.1f}°C")
            time.sleep(0.5)  # 短暂延时
        
        # 计算平均温度
        avg_temp = sum(temp_readings) / len(temp_readings)
        print(f"  平均温度: {avg_temp:.1f}°C")
        
        # 采集其他传感器数据
        sensor_data = {
            "temperature": round(avg_temp, 1),
            "humidity": read_humidity(),
            "slump": read_slump(),
            "rebar_density": read_rebar_density()
        }
        print("传感器数据:", sensor_data)

        # 兼容原env_monitor采集格式
        env_params = sensor_data

        print("\n=== [3] 振捣策略生成 ===")
        strategy = generate_strategy(material_params, env_params)
        print("振捣策略:", strategy)
        
        # 保存策略到文件
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        os.makedirs(output_dir, exist_ok=True)
        strategy_file = os.path.join(output_dir, "vibration_strategy.json")
        
        with open(strategy_file, 'w', encoding='utf-8') as f:
            json.dump(strategy, f, ensure_ascii=False, indent=2)
        print(f"策略已保存至: {strategy_file}")
        
        # 询问用户是否需要可视化
        visualize = input("\n是否需要可视化振捣点位布局? (y/n): ").strip().lower()
        if visualize == 'y' or visualize == 'yes':
            print("\n=== [3.1] 振捣点位可视化 ===")
            image_file = os.path.join(output_dir, "vibration_points.png")
            visualize_vibration_points(strategy, save_path=image_file)

        print("\n=== [4] 设备控制与执行 ===")
        # 执行振捣策略，控制步进电机
        vibration_executed = False  # 标记是否执行了振捣操作
        try:
            # 询问用户是否要执行振捣操作
            execute_vibration = input("\n是否执行振捣操作? (需要GPIO权限) (y/n): ").strip().lower()
            if execute_vibration == 'y' or execute_vibration == 'yes':
                print("\n开始执行振捣操作...")
                # 调用设备控制模块执行振捣策略
                execute_strategy(strategy) # This function now handles its own motor setup and destroy
                vibration_executed = True  # 标记振捣操作已执行
            else:
                print("\n跳过振捣操作")
        except Exception as e:
            print(f"\n执行振捣操作时出错: {e}")
            print("\n可能的原因:")
            print("1. 没有安装 RPi.GPIO 库 (请运行: sudo apt-get install python3-rpi.gpio)")
            print("2. 没有足够的权限 (请使用 sudo 运行)")
            print("3. 当前系统不支持GPIO操作")

        # 振捣完成后生成实时质量日志
        if vibration_executed:
            print("\n=== [4.1] 生成实时质量日志 ===")
            try:
                excel_file = os.path.join(output_dir, "振捣实时质量日志.xlsx")
                excel_path = generate_vibration_excel(strategy, excel_file)
                if excel_path:
                    print(f"振捣实时质量日志已生成: {excel_path}")
                else:
                    print("实时质量日志生成失败，请检查是否安装了pandas和openpyxl库")
            except Exception as e:
                print(f"生成实时质量日志时出错: {e}")
                print("请确保安装了必要的库: sudo apt-get install python3-pandas python3-openpyxl")

        print("\n=== [5] 数据闭环上传 ===")
        report_data = {
            "material_params": material_params,
            "env_params": env_params,
            "strategy": strategy
        }
        # 使用配置中的报告路径
        reports_dir = config.get("report_save_path", "data/reports/")
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir, exist_ok=True)
        # 让 cloud_upload 用统一路径（如需进一步集成可在 cloud_upload 中读取 config）
        upload_data(report_data)
    finally:
        print("\n=== [系统清理] 清理外设资源 ===")
        try:
            print("正在关闭所有LED和蜂鸣器...")
            if led_initialized: # 确保只在初始化成功时尝试关闭
                all_leds_off()
            if buzzer_initialized: # 确保只在初始化成功时尝试关闭
                buzzer_off()
            
            # 使用已验证的方法确保蜂鸣器关闭
            print("使用特殊方法关闭蜂鸣器...")
            try:
                GPIO.setup(17, GPIO.OUT)
                GPIO.output(17, GPIO.HIGH)
                GPIO.setup(18, GPIO.OUT)
                GPIO.output(18, GPIO.HIGH)
                time.sleep(0.3)  # 给一点时间确保设置生效
                print("已设置蜂鸣器引脚为HIGH, 绿灯引脚为HIGH，蜂鸣器应该已关闭")
            except Exception as e:
                print(f"特殊方法失败: {e}")
                
            print("所有受控外设已尝试关闭。")
            
            # 步进电机的 destroy() 包含它自己的 GPIO.cleanup()，这可能会导致冲突
            # 因此，我们将只在这里进行一次全局的 GPIO.cleanup()
            # 如果 execute_strategy 被调用，其内部的 destroy() 也会被执行
            # 我们需要确保 device_control.destroy() 不再调用 GPIO.cleanup() 或者只清理它自己的引脚
            
            print("准备执行全局 GPIO.cleanup()...")
            GPIO.cleanup() # 清理所有已使用的GPIO通道
            print("[清理] 所有GPIO资源已通过全局cleanup释放")
            
        except Exception as e:
            print(f"[错误] 系统清理过程中发生错误: {e}")
        finally:
            print("系统清理完成。")

if __name__ == "__main__":
    main()
