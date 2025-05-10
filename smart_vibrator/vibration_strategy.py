"""
vibration_strategy.py
振捣策略生成模块
根据环境参数和混凝土配料信息输出振捣策略（频率、时间、深度、点位布局）。
"""
import numpy as np  # 添加numpy库的导入

def freq_to_radius(freq_hz, power_kw=None, slump_mm=None, aggregate_size_mm=None, viscosity_pas=None, temperature=None):
    """
    频率与有效振捣半径之间的拟合函数
    基于公式: R = K * (P^0.4 * S^0.3 * f^0.2) / (d^0.1 * μ^0.2)
    
    参数:
    - freq_hz: 振动频率 (Hz), 范围100~200 Hz
    - power_kw: 振捣棒功率 (kW), 范围1.0~3.0 kW, 如果为None则提示用户输入
    - slump_mm: 混凝土坍落度 (mm), 范围50~180 mm, 如果为None则提示用户输入
    - aggregate_size_mm: 骨料最大粒径 (mm), 范围5~40 mm, 如果为None则提示用户输入
    - viscosity_pas: 混凝土黏度系数 (Pa·s), 范围10~100 Pa·s, 如果为None则提示用户输入
    - temperature: 环境温度 (°C), 用于调整K值
    
    返回:
    - 有效振捣半径 (cm), 范围20~60 cm
    """
    # 如果缺少参数，提示用户输入
    if power_kw is None:
        try:
            power_kw = float(input("请输入振捣棒功率(kW, 范围1.0~3.0): "))
            power_kw = max(1.0, min(3.0, power_kw))  # 限制在有效范围内
        except ValueError:
            print("输入无效，使用默认值2.0 kW")
            power_kw = 2.0
    
    if slump_mm is None:
        try:
            slump_mm = float(input("请输入混凝土坍落度(mm, 范围50~180): "))
            slump_mm = max(50, min(180, slump_mm))  # 限制在有效范围内
        except ValueError:
            print("输入无效，使用默认值120 mm")
            slump_mm = 120
    
    if aggregate_size_mm is None:
        try:
            aggregate_size_mm = float(input("请输入骨料最大粒径(mm, 范围5~40): "))
            aggregate_size_mm = max(5, min(40, aggregate_size_mm))  # 限制在有效范围内
        except ValueError:
            print("输入无效，使用默认值20 mm")
            aggregate_size_mm = 20
    
    if viscosity_pas is None:
        try:
            viscosity_pas = float(input("请输入混凝土黏度系数(Pa·s, 范围10~100): "))
            viscosity_pas = max(10, min(100, viscosity_pas))  # 限制在有效范围内
        except ValueError:
            print("输入无效，使用默认值50 Pa·s")
            viscosity_pas = 50
    
    # 基础修正系数K
    K = 2.0  # 调整为更合理的默认值
    
    # 根据温度调整K值
    if temperature is not None:
        if temperature < 10:
            K = 2.4  # 低温环境，振捣效果降低，需要增大K值
        elif 10 <= temperature <= 20:
            K = 2.2  # 中低温
        elif 20 < temperature <= 30:
            K = 2.0  # 中温
        else:  # > 30
            K = 1.8   # 高温环境，混凝土流动性增加，振捣效果提高
    
    # 应用修改后的公式，大幅提高参数对结果的影响
    # 原公式: R = K * (P^0.4 * S^0.3 * f^0.2) / (d^0.1 * μ^0.2)
    # 新公式: R = K * (P^0.7 * S^0.6 * f^0.4) / (d^0.5 * μ^0.4)
    
    # 增大分子的指数，使正相关参数影响更明显
    numerator = (power_kw ** 0.7) * (slump_mm ** 0.6) * (freq_hz ** 0.4)
    
    # 增大分母的指数，使负相关参数影响更明显
    denominator = (aggregate_size_mm ** 0.5) * (viscosity_pas ** 0.4)
    
    radius_cm = K * (numerator / denominator)
    
    # 限制在有效范围内
    radius_cm = max(20, min(60, radius_cm))
    
    # 只在调试模式下打印计算过程
    if __name__ == "__main__" and False:  # 设置为False关闭调试输出
        print(f"\n计算过程: K={K:.1f}, P={power_kw}, S={slump_mm}, f={freq_hz}, d={aggregate_size_mm}, μ={viscosity_pas}")
        print(f"计算结果: {radius_cm:.2f} cm")
    
    return radius_cm


def generate_strategy(material_params, env_params):
    """
    根据材料参数和环境参数生成振捣策略。
    :param material_params: dict, 混凝土材料参数
    :param env_params: dict, 环境参数
    :return: dict, 详细的振捣策略
    """
    print("\n正在生成振捣策略...")
    
    # 检查必要的环境参数，缺失则提示用户输入
    required_env_params = ["temperature", "humidity", "slump", "rebar_density"]
    param_names = {
        "temperature": "温度(°C)",
        "humidity": "湿度(%)",
        "slump": "坍落度(mm)",
        "rebar_density": "钢筋密度(0-1)"
    }
    defaults = {"temperature": 25, "humidity": 60, "slump": 180, "rebar_density": 0.3}
    
    for param in required_env_params:
        if param not in env_params or env_params[param] is None:
            try:
                value = float(input(f"\n请输入{param_names.get(param, param)}: "))
                env_params[param] = value
            except ValueError:
                print(f"\n输入无效，使用默认值 {defaults[param]}")
                env_params[param] = defaults[param]
    
    # 从材料参数中提取骨料类型和水灰比
    aggregate_type = material_params.get("aggregate_type", "碎石")
    water_cement_ratio = material_params.get("water_cement_ratio", 0.5)
    
    # 从材料参数中提取骨料最大粒径
    aggregate_size_mm = 20  # 默认值
    if "粗集料" in material_params and "规格" in material_params["粗集料"]:
        # 尝试从规格中提取粒径信息，例如"5-25"表示最大粒径为25mm
        try:
            size_str = material_params["粗集料"]["规格"]
            if "-" in size_str:
                aggregate_size_mm = float(size_str.split("-")[1])
        except (ValueError, IndexError):
            pass
    
    # 提取振捣棒功率
    power_kw = 2.0  # 默认振捣棒功率
    try:
        power_input = input("\n请输入振捣棒功率(kW, 范围1.0~3.0): ")
        if power_input.strip():
            power_kw = float(power_input)
            power_kw = max(1.0, min(3.0, power_kw))  # 限制在有效范围内
    except ValueError:
        print(f"\n输入无效，使用默认值 {power_kw} kW")
    
    # 估计混凝土黏度系数
    viscosity_pas = 50  # 默认值
    if water_cement_ratio < 0.4:
        viscosity_pas = 80
    elif water_cement_ratio < 0.5:
        viscosity_pas = 60
    elif water_cement_ratio < 0.6:
        viscosity_pas = 40
    else:
        viscosity_pas = 30
    
    # 计算基础振捣频率
    base_freq = 180  # 基础频率
    if aggregate_type == "卵石":
        base_freq -= 10
    if env_params["slump"] < 160:
        base_freq += 10
    if env_params["slump"] > 200:
        base_freq -= 10
    if env_params["rebar_density"] > 0.4:
        base_freq += 5
    base_freq = max(120, min(220, base_freq))
    
    # 计算基础振捣时间
    base_time = 10
    if env_params["slump"] < 160:
        base_time += 4
    if env_params["slump"] > 200:
        base_time -= 2
    if water_cement_ratio < 0.42:
        base_time += 2
    base_time = max(6, min(20, base_time))
    
    # 计算基础振捣深度
    base_depth = 40
    if env_params["humidity"] < 55:
        base_depth += 5
    if env_params["humidity"] > 70:
        base_depth -= 3
    base_depth = max(20, min(60, base_depth))
    
    # 计算基础振捣半径
    base_radius = freq_to_radius(
        freq_hz=base_freq,
        power_kw=power_kw,
        slump_mm=env_params["slump"],
        aggregate_size_mm=aggregate_size_mm,
        viscosity_pas=viscosity_pas,
        temperature=env_params["temperature"]
    )
    
    # 混凝板尺寸默认值
    board_width = 3.0  # 默认宽度 3 米
    board_length = 4.0  # 默认长度 4 米
    board_thickness = 30  # 默认厚度 30 厘米
    
    # 计算混凝板尺寸
    try:
        width_input = input("\n请输入混凝板宽度(m): ")
        if width_input.strip():
            board_width = float(width_input)
        
        length_input = input("\n请输入混凝板长度(m): ")
        if length_input.strip():
            board_length = float(length_input)
        
        thickness_input = input("\n请输入混凝板厚度(cm): ")
        if thickness_input.strip():
            board_thickness = float(thickness_input)
    except ValueError:
        print(f"\n输入无效，使用默认值 {board_width}m x {board_length}m x {board_thickness}cm")
    
    # 根据板尺寸和振捣半径计算最佳点位布局
    spacing = base_radius * 1.8 / 100  # 转换为米，使用1.8倍半径作为间距
    
    # 计算行数和列数
    rows = max(2, int(board_length / spacing))
    cols = max(2, int(board_width / spacing))
    
    # 生成点位布局
    points = []
    for i in range(rows):
        for j in range(cols):
            # 计算当前点位的坐标
            x = j * spacing
            y = i * spacing
            
            # 根据位置调整振捣参数
            # 1. 调整频率 - 增加更多变化
            
            # 计算到板中心的距离比例
            center_x = board_width / 2
            center_y = board_length / 2
            dist_to_center = np.sqrt(((x - center_x) / board_width) ** 2 + ((y - center_y) / board_length) ** 2)
            
            # 边缘点位频率更高
            if i == 0 or i == rows-1 or j == 0 or j == cols-1:
                freq_adjustment = 20
            # 中心点位频率略低
            elif dist_to_center < 0.2:
                freq_adjustment = -15
            # 中间区域频率有波动
            else:
                # 使用正弦波产生频率波动，模拟不同区域的频率需求
                wave_x = np.sin(x * 5) * 10
                wave_y = np.cos(y * 3) * 10
                freq_adjustment = int(wave_x + wave_y)
                
                # 根据到中心的距离再进行调整
                freq_adjustment += int((dist_to_center * 30))
            
            # 限制频率范围
            point_freq = max(120, min(220, base_freq + freq_adjustment))
            
            # 2. 调整时间 - 边缘点位时间略长
            time_adjustment = 0
            if i == 0 or i == rows-1 or j == 0 or j == cols-1:
                time_adjustment = 2
            point_time = min(20, base_time + time_adjustment)
            
            # 3. 调整深度 - 根据板厚度调整
            point_depth = min(board_thickness - 5, base_depth)  # 保留底部安全距离
            
            # 4. 计算点位的振捣半径
            point_radius = freq_to_radius(
                freq_hz=point_freq,
                power_kw=power_kw,
                slump_mm=env_params["slump"],
                aggregate_size_mm=aggregate_size_mm,
                viscosity_pas=viscosity_pas,
                temperature=env_params["temperature"]
            )
            
            # 添加点位信息
            points.append({
                "id": len(points) + 1,
                "x": round(x, 2),
                "y": round(y, 2),
                "freq_hz": point_freq,
                "time_s": point_time,
                "depth_cm": point_depth,
                "radius_cm": point_radius
            })
    
    # 生成最终策略
    strategy = {
        "board_info": {
            "width_m": board_width,
            "length_m": board_length,
            "thickness_cm": board_thickness
        },
        "material_info": {
            "aggregate_type": aggregate_type,
            "water_cement_ratio": water_cement_ratio,
            "aggregate_size_mm": aggregate_size_mm,
            "viscosity_pas": viscosity_pas
        },
        "environment_info": env_params,
        "vibration_params": {
            "power_kw": power_kw,
            "base_freq_hz": base_freq,
            "base_time_s": base_time,
            "base_depth_cm": base_depth,
            "base_radius_cm": base_radius
        },
        "points": points,
        "total_points": len(points),
        "estimated_time_min": round(sum(p["time_s"] for p in points) / 60, 1)  # 估计总时间(分钟)
    }
    
    # 打印策略摘要
    print(f"\n生成的振捣策略:")
    print(f"  - 板尺寸: {board_width}m x {board_length}m x {board_thickness}cm")
    print(f"  - 振捣点数: {len(points)} 点 ({cols} 列 x {rows} 行)")
    print(f"  - 基础频率: {base_freq} Hz")
    print(f"  - 基础时间: {base_time} 秒/点")
    print(f"  - 基础深度: {base_depth} cm")
    print(f"  - 基础半径: {base_radius:.2f} cm")
    print(f"  - 估计总时间: {strategy['estimated_time_min']} 分钟")
    
    return strategy

if __name__ == "__main__":
    # 测试振捣策略生成函数
    print("\n=== 测试振捣策略生成 ===")
    material_params = {
        "aggregate_type": "碎石", 
        "water_cement_ratio": 0.45,
        "粗集料": {
            "规格": "5-25",
            "试验编号": "BC2208003", 
            "材料比例": 2.98, 
            "每方用量(kg)": {"\u7406\u8bba": 998, "\u5b9e\u9645": 962}
        }
    }
    env_params = {"humidity": 60, "temperature": 25, "slump": 180, "rebar_density": 0.3}
    
    # 调用振捣策略生成函数
    strategy = generate_strategy(material_params, env_params)
    
    # 打印点位详情
    print("\n=== 振捣点位详情 ===\n")
    for i, point in enumerate(strategy["points"]):
        if i < 5:  # 只打印前5个点位
            print(f"\u70b9位 {point['id']}: ({point['x']}, {point['y']})")
            print(f"  - 频率: {point['freq_hz']} Hz")
            print(f"  - 时间: {point['time_s']} 秒")
            print(f"  - 深度: {point['depth_cm']} cm")
            print(f"  - 半径: {point['radius_cm']:.2f} cm\n")
    
    if len(strategy["points"]) > 5:
        print(f"... 共 {len(strategy['points'])} 个点位")
