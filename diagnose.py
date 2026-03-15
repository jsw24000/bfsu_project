#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断工具 - 排查图像识别失败的问题
"""

import sys
import os
import requests
import json
from config import BAIDU_API_KEY, BAIDU_API_SECRET, BAIDU_TOKEN_URL

def print_header(title):
    """打印标题"""
    print(f"\n{'='*60}")
    print(f"【{title}】")
    print(f"{'='*60}")

def check_network():
    """检查网络连接"""
    print_header("1. 网络连接检查")
    
    try:
        response = requests.get("https://www.baidu.com", timeout=5)
        print("✓ 网络连接正常")
        return True
    except Exception as e:
        print(f"✗ 网络连接失败: {str(e)}")
        return False

def check_api_credentials():
    """检查API密钥有效性"""
    print_header("2. 百度API密钥检查")
    
    print(f"API_KEY: {BAIDU_API_KEY[:10]}...（已掩盖）")
    print(f"API_SECRET: {BAIDU_API_SECRET[:10]}...（已掩盖）")
    
    if not BAIDU_API_KEY or not BAIDU_API_SECRET:
        print("✗ API密钥配置不完整")
        return False
    
    print("\n尝试获取访问令牌...")
    try:
        params = {
            'grant_type': 'client_credentials',
            'client_id': BAIDU_API_KEY,
            'client_secret': BAIDU_API_SECRET
        }
        
        response = requests.get(BAIDU_TOKEN_URL, params=params, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        
        if 'access_token' in result:
            print("✓ API密钥有效，成功获得访问令牌")
            print(f"  - Token过期时间: {result.get('expires_in', 'unknown')} 秒")
            return True
        else:
            error_msg = result.get('error_description', result.get('error', '未知错误'))
            print(f"✗ API密钥无效: {error_msg}")
            print(f"\n完整响应: {json.dumps(result, ensure_ascii=False)}")
            return False
    
    except requests.exceptions.Timeout:
        print("✗ 连接超时，无法连接到百度API")
        return False
    except Exception as e:
        print(f"✗ 获取令牌失败: {str(e)}")
        return False

def check_image_file(image_path):
    """检查图像文件"""
    print_header("3. 图像文件检查")
    
    print(f"图像路径: {image_path}")
    
    if not os.path.exists(image_path):
        print("✗ 文件不存在")
        return False
    
    try:
        file_size = os.path.getsize(image_path)
        print(f"✓ 文件存在")
        print(f"  - 文件大小: {file_size} 字节")
        
        # 检查文件扩展名
        valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp']
        ext = os.path.splitext(image_path)[1].lower()
        
        if ext in valid_extensions:
            print(f"  - 文件格式: {ext} ✓")
            return True
        else:
            print(f"  - 文件格式: {ext} ✗ (不支持)")
            print(f"    支持的格式: {', '.join(valid_extensions)}")
            return False
    
    except Exception as e:
        print(f"✗ 无法读取文件: {str(e)}")
        return False

def test_image_recognition(image_path):
    """测试图像识别"""
    print_header("4. 图像识别测试")
    
    if not os.path.exists(image_path):
        print("✗ 图像文件不存在，跳过识别测试")
        return False
    
    try:
        from baidu_api import BaiduAPIClient
        client = BaiduAPIClient()
        
        print(f"正在识别图像: {image_path}")
        result = client.recognize_image(image_path)
        
        if result['success']:
            print(f"✓ 图像识别成功")
            print(f"  - 检测到对象数: {len(result['results'])}")
            
            if result['results']:
                print("  - 检测到的对象:")
                for i, obj in enumerate(result['results'][:5], 1):  # 显示前5个
                    print(f"    {i}. {obj}")
        else:
            print(f"✗ 图像识别失败: {result['error']}")
            if 'error_code' in result:
                print(f"  - 错误代码: {result['error_code']}")
            return False
        
        return True
    
    except Exception as e:
        print(f"✗ 识别过程异常: {str(e)}")
        return False

def main():
    """主诊断流程"""
    print("\n" + "="*60)
    print("玩具出口合规审查系统 - 诊断工具")
    print("="*60)
    
    results = []
    
    # 1. 检查网络
    results.append(("网络连接", check_network()))
    
    if not results[0][1]:
        print("\n【诊断结果】")
        print("✗ 网络连接失败，无法继续测试")
        print("\n【解决方案】")
        print("  1. 检查互联网连接")
        print("  2. 检查DNS设置")
        print("  3. 尝试翻墙（如果在国内）")
        return
    
    # 2. 检查API密钥
    results.append(("API密钥有效性", check_api_credentials()))
    
    if not results[1][1]:
        print("\n【诊断结果】")
        print("✗ API密钥无效或无法连接到百度API")
        print("\n【解决方案】")
        print("  1. 验证config.py中的BAIDU_API_KEY和BAIDU_API_SECRET")
        print("  2. 确保已在百度智能云注册并创建了应用")
        print("  3. 检查API的调用配额是否已用完")
        print("  4. 尝试重新生成API密钥")
        return
    
    # 3. 检查示例图像
    print_header("5. 测试示例")
    test_image = input("请输入要测试的图像文件路径 (或按Enter跳过): ").strip()
    
    if test_image:
        results.append(("图像文件有效性", check_image_file(test_image)))
        
        if results[2][1]:
            results.append(("图像识别", test_image_recognition(test_image)))
    
    # 打印总结
    print_header("诊断总结")
    for check_name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"  {check_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n【结论】")
        print("✓ 所有诊断检查都已通过！")
        print("  系统应该能够正常识别图像。")
        print("  如果仍然遇到问题，请查看详细的错误日志。")
    else:
        print("\n【结论】")
        print("✗ 有一些检查失败，请根据上面的建议解决。")

if __name__ == "__main__":
    main()
