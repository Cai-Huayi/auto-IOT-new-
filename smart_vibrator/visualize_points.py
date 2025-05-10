#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
振捣点位可视化工具
生成三维图形展示振捣点位布局
"""

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import LinearSegmentedColormap
import json
import sys
import os
import matplotlib
from vibration_strategy import generate_strategy

# 设置matplotlib支持中文
# Ubuntu字体设置
def setup_matplotlib_fonts():
    """设置matplotlib支持中文显示，兼容Ubuntu和Windows"""
    import platform
    system = platform.system()
    
    if system == 'Linux':
        # Ubuntu上常用的中文字体
        matplotlib.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei', 'WenQuanYi Micro Hei', 'DejaVu Sans', 'Ubuntu', 'SimHei', 'sans-serif']
        # 尝试加载中文字体
        try:
            from matplotlib.font_manager import fontManager
            fontManager.addfont('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc')
        except:
            print("\n警告: 无法加载中文字体，可能需要安装文泉驿正黑字体")
            print("  请运行: sudo apt-get install fonts-wqy-zenhei fonts-wqy-microhei")
    else:
        # Windows上常用的中文字体
        matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans', 'Arial Unicode MS', 'sans-serif']
    
    matplotlib.rcParams['font.family'] = 'sans-serif'
    matplotlib.rcParams['axes.unicode_minus'] = False  # 正确显示负号
    
    # 设置全局编码
    import sys
    if sys.getdefaultencoding() != 'utf-8':
        print(f"\n警告: 系统默认编码不是utf-8, 当前为: {sys.getdefaultencoding()}")

# 调用字体设置函数
setup_matplotlib_fonts()

def visualize_vibration_points(strategy, save_path=None):
    """
    可视化振捣点位布局
    :param strategy: 振捣策略字典
    :param save_path: 可选，保存图像的路径
    """
    # 提取板尺寸
    board_width = strategy['board_info']['width_m']
    board_length = strategy['board_info']['length_m']
    board_thickness = strategy['board_info']['thickness_cm'] / 100  # 转换为米

    # 提取点位信息
    points = strategy['points']
    x_coords = [p['x'] for p in points]
    y_coords = [p['y'] for p in points]
    
    # 提取频率作为颜色映射
    frequencies = [p['freq_hz'] for p in points]
    min_freq = min(frequencies)
    max_freq = max(frequencies)
    
    # 提取半径作为点大小
    radii = [p['radius_cm'] / 10 for p in points]  # 缩小点大小以便显示
    
    # 创建图形
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # 创建自定义颜色映射：从蓝色(低频)到红色(高频)
    colors = [(0, 0, 1), (0, 1, 1), (0, 1, 0), (1, 1, 0), (1, 0, 0)]
    cmap_name = 'frequency_colormap'
    cm = LinearSegmentedColormap.from_list(cmap_name, colors, N=100)
    
    # 绘制混凝土板
    # 底面
    xx, yy = np.meshgrid([0, board_width], [0, board_length])
    zz = np.zeros(xx.shape)
    ax.plot_surface(xx, yy, zz, alpha=0.3, color='gray')
    
    # 顶面
    ax.plot_surface(xx, yy, np.ones(xx.shape) * board_thickness, alpha=0.3, color='gray')
    
    # 侧面1
    xx, zz = np.meshgrid([0, board_width], [0, board_thickness])
    yy = np.zeros(xx.shape)
    ax.plot_surface(xx, yy, zz, alpha=0.3, color='gray')
    
    # 侧面2
    yy = np.ones(xx.shape) * board_length
    ax.plot_surface(xx, yy, zz, alpha=0.3, color='gray')
    
    # 侧面3
    yy, zz = np.meshgrid([0, board_length], [0, board_thickness])
    xx = np.zeros(yy.shape)
    ax.plot_surface(xx, yy, zz, alpha=0.3, color='gray')
    
    # 侧面4
    xx = np.ones(yy.shape) * board_width
    ax.plot_surface(xx, yy, zz, alpha=0.3, color='gray')
    
    # 绘制振捣点位
    # 计算点的z坐标 (振捣深度)
    z_coords = [board_thickness - (p['depth_cm'] / 100) / 2 for p in points]  # 振捣棒插入深度的一半
    
    # 绘制散点图
    sc = ax.scatter(x_coords, y_coords, z_coords, 
                    c=frequencies, cmap=cm, 
                    s=radii, alpha=0.7, 
                    vmin=min_freq, vmax=max_freq)
    
    # 添加颜色条
    cbar = plt.colorbar(sc, ax=ax, pad=0.1)
    cbar.set_label('振捣频率 (Hz)')
    
    # 绘制振捣棒示意图（为前5个点）
    for i in range(min(5, len(points))):
        x, y = points[i]['x'], points[i]['y']
        z_top = board_thickness
        z_bottom = board_thickness - points[i]['depth_cm'] / 100
        ax.plot([x, x], [y, y], [z_top, z_bottom], 'k-', linewidth=2)
    
    # 设置坐标轴标签
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.set_zlabel('Z (m)')
    
    # 设置坐标轴范围
    ax.set_xlim([0, board_width])
    ax.set_ylim([0, board_length])
    ax.set_zlim([0, board_thickness])
    
    # 添加标题和信息
    plt.title(f'混凝土振捣点位布局 ({strategy["total_points"]}个点位)')
    
    # 添加信息文本
    info_text = (
        f"板尺寸: {board_width}m × {board_length}m × {board_thickness*100:.1f}cm\n"
        f"点位数量: {strategy['total_points']} ({len(set(x_coords))} × {len(set(y_coords))})\n"
        f"基础频率: {strategy['vibration_params']['base_freq_hz']} Hz\n"
        f"基础半径: {strategy['vibration_params']['base_radius_cm']:.2f} cm\n"
        f"估计总时间: {strategy['estimated_time_min']:.1f} 分钟"
    )
    plt.figtext(0.02, 0.02, info_text, fontsize=10, bbox=dict(facecolor='white', alpha=0.7))
    
    # 调整视角
    ax.view_init(elev=20, azim=225)
    
    # 保存图像
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图像已保存至: {save_path}")
    
    # 显示图像
    plt.tight_layout()
    plt.show()

def main():
    """主函数"""
    # 检查是否提供了策略文件
    if len(sys.argv) > 1:
        strategy_file = sys.argv[1]
        try:
            with open(strategy_file, 'r', encoding='utf-8') as f:
                strategy = json.load(f)
            visualize_vibration_points(strategy)
        except Exception as e:
            print(f"读取策略文件时出错: {e}")
            return
    else:
        # 如果没有提供策略文件，则生成新的策略
        print("未提供策略文件，将生成新的振捣策略...")
        
        # 设置默认参数
        material_params = {
            "aggregate_type": "碎石", 
            "water_cement_ratio": 0.45,
            "粗集料": {
                "规格": "5-25",
                "试验编号": "BC2208003", 
                "材料比例": 2.98, 
                "每方用量(kg)": {"理论": 998, "实际": 962}
            }
        }
        env_params = {"humidity": 60, "temperature": 25, "slump": 180, "rebar_density": 0.3}
        
        # 生成策略
        strategy = generate_strategy(material_params, env_params)
        
        # 保存策略到文件
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        os.makedirs(output_dir, exist_ok=True)
        strategy_file = os.path.join(output_dir, "vibration_strategy.json")
        
        with open(strategy_file, 'w', encoding='utf-8') as f:
            json.dump(strategy, f, ensure_ascii=False, indent=2)
        print(f"策略已保存至: {strategy_file}")
        
        # 可视化策略
        image_file = os.path.join(output_dir, "vibration_points.png")
        visualize_vibration_points(strategy, save_path=image_file)

if __name__ == "__main__":
    main()
