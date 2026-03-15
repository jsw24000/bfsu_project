#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试脚本 - 直接测试百度API响应
"""

import requests
import json
import base64
from config import BAIDU_API_KEY, BAIDU_API_SECRET, BAIDU_TOKEN_URL, BAIDU_IMAGE_RECOGNIZE_URL
import sys

# 解决Windows编码问题
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_api_directly():
    """直接测试API调用"""
    print("="*70)
    print("【百度API直接测试】")
    print("="*70)
    
    # 第一步：获取访问令牌
    print("\n[步骤1] 获取访问令牌...")
    params = {
        'grant_type': 'client_credentials',
        'client_id': BAIDU_API_KEY,
        'client_secret': BAIDU_API_SECRET
    }
    
    try:
        response = requests.get(BAIDU_TOKEN_URL, params=params, timeout=10)
        token_result = response.json()
        print(f"令牌响应: {json.dumps(token_result, ensure_ascii=False)}")
        
        if 'access_token' not in token_result:
            print("✗ 无法获得访问令牌")
            return
        
        access_token = token_result['access_token']
        print(f"[OK] 成功获得令牌: {access_token[:20]}...")
    
    except Exception as e:
        print(f"[ERROR] 获取令牌失败: {str(e)}")
        return
    
    # 第二步：读取图像
    print("\n[步骤2] 读取图像...")
    image_path = "1.jpg"
    
    try:
        with open(image_path, 'rb') as f:
            image_content = f.read()
        
        image_base64 = base64.b64encode(image_content).decode('utf-8')
        print(f"[OK] 图像读取成功，大小: {len(image_content)} 字节")
        print(f"[OK] Base64 编码完成，长度: {len(image_base64)}")
    
    except Exception as e:
        print(f"[ERROR] 读取图像失败: {str(e)}")
        return
    
    # 第三步：调用图像识别API
    print("\n[步骤3] 调用图像识别API...")
    
    url = f"{BAIDU_IMAGE_RECOGNIZE_URL}?access_token={access_token}"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'image': image_base64
    }
    
    try:
        print(f"API URL: {BAIDU_IMAGE_RECOGNIZE_URL}")
        print(f"Request headers: {json.dumps(headers, ensure_ascii=False)}")
        print(f"Request data size: {len(str(data))} 字节")
        
        response = requests.post(url, headers=headers, data=data, timeout=15)
        print(f"\n[OK] 收到响应 (HTTP {response.status_code})")
        
        # 打印原始响应文本
        print(f"\n【原始响应文本】:")
        print(response.text[:1000])  # 显示前1000个字符
        
        # 尝试解析JSON
        result = response.json()
        print(f"\n【解析后的JSON】:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # 分析错误
        if result.get('error_code') == 0:
            print(f"\n[OK] API 调用成功!")
            print(f"识别到 {len(result.get('result', []))} 个对象")
            
            # 显示识别结果
            for i, item in enumerate(result.get('result', [])[:5], 1):
                print(f"  {i}. {item}")
        else:
            print(f"\n[ERROR] API 返回错误:")
            print(f"  错误代码: {result.get('error_code')}")
            print(f"  错误信息: {result.get('error_msg')}")
            
            # 其他可能的错误字段
            if 'error' in result:
                print(f"  详细错误: {result.get('error')}")
    
    except Exception as e:
        print(f"[ERROR] API 调用异常: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_directly()
