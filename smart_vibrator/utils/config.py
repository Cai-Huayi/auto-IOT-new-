"""
config.py
系统配置模块，集中管理系统参数。
"""

def get_config():
    """
    返回系统配置项字典。
    """
    config = {
        "report_save_path": "data/reports/",
        "camera": {
            "resolution": (1280, 720),
            "device_index": 0
        },
        "cloud_upload_url": "",  # 可留空，后续补充
        "sensor_refresh_interval": 2  # 单位：秒
    }
    return config

if __name__ == "__main__":
    print(get_config())
