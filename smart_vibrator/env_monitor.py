"""
env_monitor.py
环境参数采集模块
模拟读取四类环境传感器数据：湿度、温度、坍落度、钢筋分布密度。
"""

import random

def get_environment_data():
    """
    模拟传感器采集环境参数。
    :return: dict {"humidity": float, "temperature": float, "slump": float, "rebar_density": float}
    """
    data = {
        "humidity": round(random.uniform(50, 80), 1),          # 湿度 50~80%
        "temperature": round(random.uniform(15, 35), 1),       # 温度 15~35°C
        "slump": round(random.uniform(140, 220), 0),           # 坍落度 140~220mm
        "rebar_density": round(random.uniform(0.2, 0.5), 2)    # 钢筋分布密度 0.2~0.5
    }
    return data

if __name__ == "__main__":
    print(get_environment_data())
