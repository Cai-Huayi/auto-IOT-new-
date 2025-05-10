"""
main.py
主程序调度入口，串联各模块实现智能振捣全流程。
"""
import time
import os
import json

from vibration_strategy import generate_strategy
from device_control import execute_strategy
from cloud_upload import upload_data
from utils.config import get_config
from utils.sensor_interface import read_temperature, read_humidity, read_slump, read_rebar_density
from utils.camera_ocr import ocr_extract_material_info
from visualize_points import visualize_vibration_points





def main():
    config = get_config()
    print("[系统配置]", config)

    print("=== [1] 混凝土材料参数识别 ===")
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
    try:
        # 询问用户是否要执行振捣操作
        execute_vibration = input("\n是否执行振捣操作? (需要GPIO权限) (y/n): ").strip().lower()
        if execute_vibration == 'y' or execute_vibration == 'yes':
            print("\n开始执行振捣操作...")
            # 调用设备控制模块执行振捣策略
            execute_strategy(strategy)
        else:
            print("\n跳过振捣操作")
    except Exception as e:
        print(f"\n执行振捣操作时出错: {e}")
        print("\n可能的原因:")
        print("1. 没有安装 RPi.GPIO 库 (请运行: sudo apt-get install python3-rpi.gpio)")
        print("2. 没有足够的权限 (请使用 sudo 运行)")
        print("3. 当前系统不支持GPIO操作")

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

if __name__ == "__main__":
    main()
