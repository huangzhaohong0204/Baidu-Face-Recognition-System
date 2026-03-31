# -*- coding: utf-8 -*-
import requests
import base64
import os
from dotenv import load_dotenv
from utils.image_utils import get_file_content, check_image_size

# 加载.env配置文件
load_dotenv(dotenv_path="config/.env")

# 1. 配置核心参数（从.env读取）
API_KEY = os.getenv("BAIDU_API_KEY")
SECRET_KEY = os.getenv("BAIDU_SECRET_KEY")


# -------------------------- 工具函数：获取AccessToken --------------------------
def get_access_token():
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": API_KEY,
        "client_secret": SECRET_KEY
    }
    response = requests.post(url, params=params)
    if response.status_code != 200:
        raise Exception(f"获取AccessToken失败：{response.text}")
    return response.json()["access_token"]


# -------------------------- 核心功能：人脸1:1比对（已修复逻辑bug） --------------------------
def face_match(face1_path, face2_path):
    # 校验图片大小
    check_image_size(face1_path)
    check_image_size(face2_path)

    # 读取图片并转Base64
    face1_base64 = base64.b64encode(get_file_content(face1_path)).decode("utf-8")
    face2_base64 = base64.b64encode(get_file_content(face2_path)).decode("utf-8")

    # 获取AccessToken
    access_token = get_access_token()

    # 接口请求URL
    url = f"https://aip.baidubce.com/rest/2.0/face/v3/match?access_token={access_token}"

    # 构建请求参数
    payload = [
        {"image": face1_base64, "image_type": "BASE64"},
        {"image": face2_base64, "image_type": "BASE64"}
    ]
    headers = {"Content-Type": "application/json"}

    # 发送POST请求
    response = requests.post(url, json=payload, headers=headers)
    result = response.json()

    # 🔴 修复点：只有error_code不等于0时，才抛异常；等于0是成功
    if result.get("error_code", 0) != 0:
        raise Exception(f"人脸比对失败：{result.get('error_msg', '未知错误')}（错误码：{result.get('error_code')}）")

    # 解析结果
    score = result["result"]["score"]
    return {
        "比对状态": "通过 ✅（同一人）" if score >= 80 else "不通过 ❌（非同一人）",
        "相似度得分": f"{score:.2f}",
        "判定阈值": "80分以上为同一人",
        "说明": "本项目基于百度人脸识别API实现，验证两张人脸是否为同一人"
    }


# -------------------------- 主程序测试 --------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("🔥 百度人脸识别系统（人脸比对版） 🔥")
    print("=" * 60)

    # 测试路径（对应images文件夹里的两张人脸照片）
    face1_img = "images/face.jpg"
    face2_img = "images/face.jpg"  # 同一张照片测试，相似度100%

    try:
        print("\n📷 正在进行人脸1:1比对...")
        match_result = face_match(face1_img, face2_img)

        for k, v in match_result.items():
            print(f"  {k}：{v}")

    except Exception as e:
        print(f"\n❌ 程序异常：{e}")