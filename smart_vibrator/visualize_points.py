#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
振捣点位可视化工具
生成三维图形展示振捣点位布局，支持分层显示
"""

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import LinearSegmentedColormap
import json
import sys
import os
import matplotlib
import pandas as pd  # 导入pandas用于生成Excel文件
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

def generate_vibration_excel(strategy, save_path=None):
    """
    生成振捣点位的Excel表格
    :param strategy: 振捣策略字典
    :param save_path: 保存图像的路径，用于确定Excel保存位置
    :return: Excel文件保存路径
    """
    try:
        # 提取板厚度
        board_thickness = strategy['board_info']['thickness_cm'] / 100  # 转换为米
        
        # 提取点位信息
        points = strategy['points']
        
        # 创建数据列表
        data = []
        for point in points:
            # 计算z坐标（从板顶面向下的深度）
            z = board_thickness - point['depth_cm'] / 200  # 取插入深度的一半作为振捣点的z坐标
            
            # 添加点位数据
            data.append({
                '振捣编号': point['id'],
                '振捣点位 (x,y,z)': f"({point['x']:.2f}, {point['y']:.2f}, {z:.2f})",
                'x': point['x'],
                'y': point['y'],
                'z': z,
                '振捣时间 (s)': point['time_s'],
                '插入深度 (m)': point['depth_cm'] / 100,  # 转换为米
                '振捣频率 (hz)': point['freq_hz'],
                '振捣半径 (cm)': point['radius_cm']
            })
        
        # 创建DataFrame
        df = pd.DataFrame(data)
        
        # 选择要导出的列和顺序
        df_export = df[['振捣编号', '振捣点位 (x,y,z)', '振捣时间 (s)', '插入深度 (m)', '振捣频率 (hz)', '振捣半径 (cm)']]
        
        # 确定保存路径
        excel_path = None
        if save_path:
            # 从图像保存路径获取目录和基本文件名
            save_dir = os.path.dirname(save_path)
            base_name = os.path.splitext(os.path.basename(save_path))[0]
            excel_path = os.path.join(save_dir, f"{base_name}_参数表.xlsx")
        else:
            # 如果未提供保存路径，使用默认路径
            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
            os.makedirs(output_dir, exist_ok=True)
            excel_path = os.path.join(output_dir, "振捣参数表.xlsx")
        
        # 保存Excel文件
        try:
            df_export.to_excel(excel_path, sheet_name='实时质量日志', index=False)
            print(f"振捣参数表已保存至: {excel_path}")
            return excel_path
        except ImportError as e:
            print(f"警告: Excel文件生成失败，缺少必要的库: {e}")
            print("请安装openpyxl库: sudo apt-get install python3-openpyxl 或 pip3 install openpyxl")
            return None
        except Exception as e:
            print(f"警告: Excel文件生成失败: {e}")
            return None
    except Exception as e:
        print(f"警告: 准备Excel数据时发生错误: {e}")
        return None

def visualize_vibration_points(strategy, save_path=None):
    """
    可视化振捣点位布局，支持分层显示
    :param strategy: 振捣策略字典
    :param save_path: 可选，保存图像的路径
    """
    # 提取板尺寸
    board_width = strategy['board_info']['width_m']
    board_length = strategy['board_info']['length_m']
    board_thickness = strategy['board_info']['thickness_cm'] / 100  # 转换为米

    # 计算分层信息
    layer_height = 0.3  # 每层30厘米
    num_layers = max(1, int(np.ceil(board_thickness / layer_height)))  # 至少1层，向上取整
    
    # 实际层高(可能会调整)
    actual_layer_height = board_thickness / num_layers
    
    print(f"\n板厚: {board_thickness*100:.1f}cm, 分为{num_layers}层, 每层约{actual_layer_height*100:.1f}cm")
    
    # 提取点位信息
    points = strategy['points']
    
    # 创建图形
    fig = plt.figure(figsize=(14, 10))
    
    # 创建颜色映射：从蓝色(低频)到红色(高频)
    colors = [(0, 0, 1), (0, 1, 1), (0, 1, 0), (1, 1, 0), (1, 0, 0)]
    cmap_name = 'frequency_colormap'
    cm = LinearSegmentedColormap.from_list(cmap_name, colors, N=100)
    
    # 提取频率范围
    frequencies = [p['freq_hz'] for p in points]
    min_freq = min(frequencies)
    max_freq = max(frequencies)
    
    # 创建子图网格以显示不同层次
    if num_layers <= 2:
        # 1或2层使用1x2布局
        grid_cols = 2
        grid_rows = 1
    elif num_layers <= 4:
        # 3或4层使用2x2布局
        grid_cols = 2
        grid_rows = 2
    else:
        # 5或6层使用2x3布局
        grid_cols = 3
        grid_rows = 2
    
    # 对于更多层，保持2x3布局但可能需要多个图
    num_pages = max(1, int(np.ceil(num_layers / (grid_rows * grid_cols))))
    
    for page in range(num_pages):
        if page > 0:
            # 如果有多个页面，创建新图形
            fig = plt.figure(figsize=(14, 10))
        
        # 计算当前页面要显示的层数
        start_layer = page * grid_rows * grid_cols
        end_layer = min(num_layers, (page + 1) * grid_rows * grid_cols)
        current_page_layers = end_layer - start_layer
        
        # 对每一层创建一个子图
        for layer_idx in range(start_layer, end_layer):
            # 计算子图位置
            subplot_idx = layer_idx - start_layer + 1
            ax = fig.add_subplot(grid_rows, grid_cols, subplot_idx, projection='3d')
            
            # 计算当前层的z范围
            z_min = layer_idx * actual_layer_height
            z_max = min(board_thickness, (layer_idx + 1) * actual_layer_height)
            
            # 绘制当前层的混凝土板表示（半透明立方体）
            # 底面
            xx, yy = np.meshgrid([0, board_width], [0, board_length])
            zz = np.ones(xx.shape) * z_min
            ax.plot_surface(xx, yy, zz, alpha=0.2, color='gray')
            
            # 顶面
            ax.plot_surface(xx, yy, np.ones(xx.shape) * z_max, alpha=0.2, color='gray')
            
            # 侧面1
            xx, zz = np.meshgrid([0, board_width], [z_min, z_max])
            yy = np.zeros(xx.shape)
            ax.plot_surface(xx, yy, zz, alpha=0.2, color='gray')
            
            # 侧面2
            yy = np.ones(xx.shape) * board_length
            ax.plot_surface(xx, yy, zz, alpha=0.2, color='gray')
            
            # 侧面3
            yy, zz = np.meshgrid([0, board_length], [z_min, z_max])
            xx = np.zeros(yy.shape)
            ax.plot_surface(xx, yy, zz, alpha=0.2, color='gray')
            
            # 侧面4
            xx = np.ones(yy.shape) * board_width
            ax.plot_surface(xx, yy, zz, alpha=0.2, color='gray')
            
            # 筛选当前层的振捣点
            layer_points = []
            for point in points:
                # 计算振捣棒插入深度
                vibration_depth = point['depth_cm'] / 100  # 转换为米
                
                # 振捣棒顶部和底部的位置
                rod_top = board_thickness
                rod_bottom = board_thickness - vibration_depth
                
                # 如果振捣棒与当前层相交，则包含该点
                if (rod_bottom <= z_max and rod_bottom >= z_min) or \
                   (rod_top <= z_max and rod_top >= z_min) or \
                   (rod_bottom <= z_min and rod_top >= z_max):
                    layer_points.append(point)
            
            if layer_points:
                # 提取当前层点位的坐标和属性
                x_coords = [p['x'] for p in layer_points]
                y_coords = [p['y'] for p in layer_points]
                
                # 计算振捣棒在当前层的z坐标 (与层中点对齐)
                z_coords = [(z_min + z_max) / 2 for _ in layer_points]
                
                # 提取频率作为颜色
                frequencies = [p['freq_hz'] for p in layer_points]
                
                # 提取半径作为点大小
                radii = [p['radius_cm'] / 5 for p in layer_points]  # 缩小点大小以便显示
                
                # 绘制散点图
                sc = ax.scatter(x_coords, y_coords, z_coords, 
                                c=frequencies, cmap=cm, 
                                s=radii, alpha=0.8, 
                                vmin=min_freq, vmax=max_freq)
                
                # 绘制振捣棒
                for i, point in enumerate(layer_points):
                    x, y = point['x'], point['y']
                    # 计算振捣棒与当前层的交点
                    z_top = min(z_max, board_thickness)
                    z_bottom = max(z_min, board_thickness - point['depth_cm'] / 100)
                    ax.plot([x, x], [y, y], [z_top, z_bottom], 'k-', linewidth=1.5)
            
            # 设置轴标签和范围
            ax.set_xlabel('X (m)')
            ax.set_ylabel('Y (m)')
            ax.set_zlabel('Z (m)')
            
            ax.set_xlim([0, board_width])
            ax.set_ylim([0, board_length])
            ax.set_zlim([z_min, z_max])
            
            # 设置标题
            layer_title = f'层 {layer_idx+1}/{num_layers} (Z: {z_min*100:.1f}-{z_max*100:.1f}cm)'
            if layer_points:
                layer_title += f', {len(layer_points)}个点位'
            else:
                layer_title += ', 无点位'
            ax.set_title(layer_title)
            
            # 调整视角
            ax.view_init(elev=30, azim=225)
        
        # 添加颜色条
        cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])  # [left, bottom, width, height]
        cbar = fig.colorbar(sc, cax=cbar_ax)
        cbar.set_label('振捣频率 (Hz)')
        
        # 添加整体标题
        if num_pages > 1:
            fig.suptitle(f'混凝土振捣点位分层布局 - 页 {page+1}/{num_pages}', fontsize=16)
        else:
            fig.suptitle(f'混凝土振捣点位分层布局 ({strategy["total_points"]}个点位)', fontsize=16)
        
        # 添加信息文本
        info_text = (
            f"板尺寸: {board_width}m × {board_length}m × {board_thickness*100:.1f}cm\n"
            f"分层数: {num_layers}层 (每层约{actual_layer_height*100:.1f}cm)\n"
            f"点位数量: {strategy['total_points']} ({len(set([p['x'] for p in points]))} × {len(set([p['y'] for p in points]))})\n"
            f"基础频率: {strategy['vibration_params']['base_freq_hz']} Hz\n"
            f"基础半径: {strategy['vibration_params']['base_radius_cm']:.2f} cm\n"
            f"估计总时间: {strategy['estimated_time_min']:.1f} 分钟"
        )
        fig.text(0.02, 0.02, info_text, fontsize=10, bbox=dict(facecolor='white', alpha=0.7))
        
        # 调整布局
        plt.tight_layout(rect=[0, 0.05, 0.9, 0.95])
        
        # 保存图像
        if save_path and page == 0:
            base_path, ext = os.path.splitext(save_path)
            if num_pages > 1:
                current_save_path = f"{base_path}_page{page+1}{ext}"
            else:
                current_save_path = save_path
            plt.savefig(current_save_path, dpi=300, bbox_inches='tight')
            print(f"图像已保存至: {current_save_path}")
        elif save_path and page > 0:
            base_path, ext = os.path.splitext(save_path)
            current_save_path = f"{base_path}_page{page+1}{ext}"
            plt.savefig(current_save_path, dpi=300, bbox_inches='tight')
            print(f"图像已保存至: {current_save_path}")
    
    # 显示图像
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
