#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统测试脚本 - 验证所有组件是否正确安装和配置
"""

import sys
import json
import os

def test_imports():
    """测试依赖包导入"""
    print("【测试1】验证依赖包...")
    try:
        import requests
        print("  ✓ requests 已安装")
        return True
    except ImportError:
        print("  ✗ requests 未安装")
        print("    请运行: pip install -r requirements.txt")
        return False

def test_config():
    """测试配置文件"""
    print("\n【测试2】验证配置文件...")
    try:
        from config import BAIDU_API_KEY, BAIDU_API_SECRET
        print("  ✓ 配置文件加载成功")
        
        if BAIDU_API_KEY and BAIDU_API_SECRET:
            print(f"  ✓ API Key 已配置: {BAIDU_API_KEY[:6]}...")
            print(f"  ✓ API Secret 已配置: {BAIDU_API_SECRET[:6]}...")
            return True
        else:
            print("  ✗ API密钥未配置")
            return False
    except Exception as e:
        print(f"  ✗ 配置文件读取失败: {e}")
        return False

def test_rules():
    """测试规则文件"""
    print("\n【测试3】验证规则文件...")
    try:
        with open('rule.json', 'r', encoding='utf-8') as f:
            rules = json.load(f)
        
        print(f"  ✓ rule.json 加载成功")
        print(f"  ✓ 规则版本: {rules.get('version', '未知')}")
        print(f"  ✓ 共包含 {rules.get('total_count', 0)} 条规则")
        
        # 检查主要规则类别
        categories = [
            'religion_taboo', 'figure_pattern_taboo', 'color_taboo',
            'arabic_expression', 'festival_compliance', 'material_compliance',
            'function_compliance', 'import_compliance'
        ]
        
        found_count = 0
        for cat in categories:
            if cat in rules:
                count = rules[cat].get('count', 0)
                print(f"    • {cat}: {count} 条")
                found_count += 1
        
        print(f"  ✓ 检查到 {found_count}/{len(categories)} 个规则类别")
        return found_count > 0
    
    except Exception as e:
        print(f"  ✗ 规则文件读取失败: {e}")
        return False

def test_modules():
    """测试核心模块"""
    print("\n【测试4】验证核心模块...")
    
    try:
        from baidu_api import BaiduAPIClient
        print("  ✓ baidu_api 模块加载成功")
    except Exception as e:
        print(f"  ✗ baidu_api 模块加载失败: {e}")
        return False
    
    try:
        from rules_checker import RulesChecker
        print("  ✓ rules_checker 模块加载成功")
    except Exception as e:
        print(f"  ✗ rules_checker 模块加载失败: {e}")
        return False
    
    try:
        from main import ToyComplianceChecker
        print("  ✓ main 模块加载成功")
    except Exception as e:
        print(f"  ✗ main 模块加载失败: {e}")
        return False
    
    return True

def test_api_connection():
    """测试API连接"""
    print("\n【测试5】验证百度API连接...")
    try:
        from baidu_api import BaiduAPIClient
        client = BaiduAPIClient()
        token = client.get_access_token()
        
        if token:
            print(f"  ✓ 成功获取访问令牌")
            print(f"    Token (前16位): {token[:16]}...")
            return True
        else:
            print(f"  ✗ 无法获取访问令牌")
            return False
    except Exception as e:
        print(f"  ✗ API连接测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("玩具出口合规审查系统 - 环境检测")
    print("=" * 60 + "\n")
    
    results = {
        '依赖包': test_imports(),
        '配置文件': test_config(),
        '规则文件': test_rules(),
        '核心模块': test_modules(),
        'API连接': test_api_connection()
    }
    
    print("\n" + "=" * 60)
    print("【检测结果汇总】")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results.items():
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("✓ 所有检测均已通过！")
        print("\n你可以现在开始使用系统，运行以下命令:")
        print("  python main.py              # 进入交互模式")
        print("  python main.py check <图片> # 审查单个图片")
        print("  python main.py batch <目录> # 批量审查目录")
        return 0
    else:
        print("✗ 检测失败，请根据上述提示进行修复:")
        print("  1. 确保已运行: pip install -r requirements.txt")
        print("  2. 检查config.py中的API密钥是否正确")
        print("  3. 确认rule.json文件存在")
        print("  4. 检查网络连接是否正常")
        return 1

if __name__ == '__main__':
    sys.exit(main())
