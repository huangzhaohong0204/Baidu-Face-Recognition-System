# -*- coding: utf-8 -*-
from PIL import Image
import os


def get_file_content(file_path):
    """读取本地图片并返回二进制数据（适配百度API要求）"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"图片文件不存在：{file_path}")

    # 校验图片格式（支持jpg/png/bmp）
    try:
        img = Image.open(file_path)
        img.verify()  # 验证图片完整性
    except Exception as e:
        raise ValueError(f"图片格式错误：{file_path}，仅支持jpg/png/bmp格式") from e

    with open(file_path, 'rb') as fp:
        return fp.read()


def check_image_size(file_path, max_size_mb=4):
    """校验图片大小（百度API要求≤4M）"""
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if file_size_mb > max_size_mb:
        raise ValueError(f"图片过大：{file_path}，大小{file_size_mb:.2f}MB，最大支持4MB")
    return True