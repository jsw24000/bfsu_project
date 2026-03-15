#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整系统测试脚本 - 快速诊断和演示
"""

import os
import sys

def test_environment():
    """测试环境配置"""
    print("\n" + "="*60)
    print("【环境检查】")
    print("="*60)
    
    # 检查Python版本
    print(f"Python版本: {sys.version.split()[0]}")
    
    # 检查必要的包
    required_packages = ['requests', 'json', 'base64']
    missing_packages = []
    
    for package in ['requests']:
        try:
            __import__(package)
            print(f"✓ {package} 已安装")
        except ImportError:
            print(f"✗ {package} 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n需要安装: pip install {' '.join(missing_packages)}")
        return False
    
    return True

def test_demo_mode():
    """测试演示模式"""
    print("\n" + "="*60)
    print("【演示模式测试】")
    print("="*60)
    
    try:
        from config import DEMO_MODE
        from main import ToyComplianceChecker
        
        if DEMO_MODE:
            print("🎮 演示模式已启用")
            checker = ToyComplianceChecker()
            
            # 创建测试图像文件（占位符）
            test_image = "demo_toy.jpg"
            
            # 创建一个空的图像文件用于演示
            with open(test_image, 'wb') as f:
                f.write(b'\xff\xd8\xff')  # JPEG header
            
            print(f"\n✓ 创建测试图像: {test_image}")
            
            # 运行合规检查
            print("\n开始审查...")
            result = checker.check_image(test_image)
            
            # 打印报告
            checker.print_report(result)
            
            # 清理测试文件
            if os.path.exists(test_image):
                os.remove(test_image)
                print(f"\n✓ 清理临时文件: {test_image}")
            
            return True
        else:
            print("演示模式未启用")
            return False
    
    except Exception as e:
        print(f"✗ 演示模式测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_api_connection():
    """测试API连接"""
    print("\n" + "="*60)
    print("【API连接测试】")
    print("="*60)
    
    try:
        import requests
        from config import BAIDU_TOKEN_URL, DEMO_MODE
        
        if DEMO_MODE:
            print("演示模式已启用，跳过API测试")
            return True
        
        print("检查网络连接...")
        response = requests.get("https://www.baidu.com", timeout=5)
        print(f"✓ 网络连接正常 (HTTP {response.status_code})")
        return True
    
    except Exception as e:
        print(f"✗ 网络连接失败: {str(e)}")
        return False

def test_rules_loading():
    """测试规则加载"""
    print("\n" + "="*60)
    print("【规则加载测试】")
    print("="*60)
    
    try:
        from rules_checker import RulesChecker
        
        checker = RulesChecker()
        rules = checker.rules
        
        if not rules:
            print("✗ 规则文件为空")
            return False
        
        print(f"✓ 规则加载成功")
        print(f"  - 宗教禁忌: {rules.get('religion_taboo', {}).get('count', 0)}")
        print(f"  - 图案禁忌: {rules.get('figure_pattern_taboo', {}).get('count', 0)}")
        print(f"  - 颜色禁忌: {rules.get('color_taboo', {}).get('count', 0)}")
        print(f"  - 阿拉伯语表达: {rules.get('arabic_expression', {}).get('count', 0)}")
        
        return True
    
    except Exception as e:
        print(f"✗ 规则加载失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("\n" + "="*70)
    print(" "*15 + "玩具出口合规审查系统 - 完整测试")
    print("="*70)
    
    results = []
    
    # 1. 环境检查
    results.append(("环境检查", test_environment()))
    
    if not results[0][1]:
        print("\n【错误】环境不满足要求，请先安装必要的包")
        return
    
    # 2. 规则加载
    results.append(("规则加载", test_rules_loading()))
    
    # 3. API连接
    results.append(("API连接", test_api_connection()))
    
    # 4. 演示模式
    results.append(("演示模式", test_demo_mode()))
    
    # 打印总结
    print("\n" + "="*60)
    print("【测试总结】")
    print("="*60)
    
    for test_name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"  {test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n✓ 所有测试通过！系统准备就绪 🎉")
        print("\n【下一步】")
        print("  1. 准备玩具图片文件")
        print("  2. 运行: python main.py")
        print("  3. 或运行诊断: python diagnose.py")
    else:
        print("\n✗ 有些测试失败")
        print("\n【建议】")
        print("  1. 查看上面的错误信息")
        print("  2. 参考 TROUBLESHOOTING.md 获取帮助")
        print("  3. 如果没有API密钥，在 config.py 中设置 DEMO_MODE = True")

if __name__ == "__main__":
    main()
