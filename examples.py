#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用示例 - 展示如何以编程方式集成本系统
"""

from main import ToyComplianceChecker
import os
import json

def example_1_single_image_check():
    """示例1: 审查单个图片"""
    print("\n【示例1】审查单个玩具图片")
    print("-" * 60)
    
    checker = ToyComplianceChecker()
    
    # 使用你的图片路径替换这里
    image_path = "example_toy.jpg"
    
    if not os.path.exists(image_path):
        print(f"提示: 示例图片 {image_path} 不存在")
        print("      请提供实际的玩具图片路径")
        return
    
    # 执行审查
    result = checker.check_image(image_path)
    
    # 打印报告
    checker.print_report(result)
    
    # 保存报告
    checker.save_report(result)

def example_2_batch_check():
    """示例2: 批量审查目录中的图片"""
    print("\n【示例2】批量审查目录中的图片")
    print("-" * 60)
    
    checker = ToyComplianceChecker()
    
    # 修改为你的玩具图片目录
    toy_directory = "toys_to_check"
    
    if not os.path.exists(toy_directory):
        print(f"提示: 示例目录 {toy_directory} 不存在")
        print("      请创建该目录或提供有效路径，并放入玩具图片")
        return
    
    # 执行批量审查
    batch_results = checker.batch_check(toy_directory)
    
    # 打印汇总
    print("\n【批量审查结果汇总】")
    print(f"  总计: {batch_results['total']} 个")
    print(f"  合规: {batch_results['compliant_count']} 个")
    print(f"  不合规: {batch_results['non_compliant_count']} 个")
    
    # 保存所有结果
    summary_file = "batch_results_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(batch_results, f, ensure_ascii=False, indent=2)
    print(f"\n✓ 批量结果已保存: {summary_file}")

def example_3_programmatic_usage():
    """示例3: 编程方式集成系统"""
    print("\n【示例3】编程方式深度集成")
    print("-" * 60)
    
    from baidu_api import BaiduAPIClient
    from rules_checker import RulesChecker
    
    # 初始化模块
    baidu_client = BaiduAPIClient()
    rules_checker = RulesChecker()
    
    image_path = "example_toy.jpg"
    
    if not os.path.exists(image_path):
        print(f"提示: 示例图片 {image_path} 不存在")
        return
    
    # 步骤1: 使用百度API识别图片
    print("\n步骤1: 识别图片内容...")
    api_result = baidu_client.recognize_image(image_path)
    
    if api_result['success']:
        print(f"  识别到 {len(api_result['results'])} 个对象:")
        for obj in api_result['results'][:5]:  # 显示前5个
            name = obj.get('name', 'Unknown')
            score = obj.get('score', 0)
            print(f"    • {name} (置信度: {score:.2%})")
    else:
        print(f"  识别失败: {api_result['error']}")
        return
    
    # 步骤2: 应用合规规则
    print("\n步骤2: 应用合规规则...")
    analysis = rules_checker.analyze_image_recognition(api_result['results'])
    
    # 步骤3: 输出结果
    print(f"\n步骤3: 合规性检查结果")
    print(f"  整体合规状态: {'✓ 合规' if analysis['overall_compliant'] else '✗ 不合规'}")
    print(f"  合规评分: {analysis['compliance_score']}/100")
    
    if analysis['violations']:
        print(f"  发现的问题数: {len(analysis['violations'])}")
        for i, violation in enumerate(analysis['violations'], 1):
            print(f"    {i}. {violation['type']}: {violation['reason']}")

def example_4_custom_rule_extension():
    """示例4: 扩展自定义规则"""
    print("\n【示例4】自定义规则扩展")
    print("-" * 60)
    
    print("实现自定义规则检查的方法:")
    print("""
from rules_checker import RulesChecker

class CustomRulesChecker(RulesChecker):
    '''扩展的规则检查器'''
    
    def check_custom_pattern(self, recognized_objects):
        '''检查自定义模式'''
        violations = []
        
        # 你的自定义检查逻辑
        for obj in recognized_objects:
            if 'your_pattern' in obj.lower():
                violations.append({
                    'type': '自定义规则',
                    'detected': obj,
                    'reason': '自定义检查原因',
                    'severity': 'HIGH'
                })
        
        return len(violations) == 0, violations

# 使用自定义检查器
checker = CustomRulesChecker()
# ... 继续使用
    """)

def main():
    """运行示例"""
    print("\n" + "=" * 60)
    print("玩具审查系统 - 精选示例代码")
    print("=" * 60)
    
    examples = {
        '1': ('单个图片审查', example_1_single_image_check),
        '2': ('批量目录审查', example_2_batch_check),
        '3': ('编程深度集成', example_3_programmatic_usage),
        '4': ('自定义规则扩展', example_4_custom_rule_extension),
        '0': ('显示所有示例', None)
    }
    
    print("\n选择要运行的示例:")
    for key, (desc, _) in examples.items():
        print(f"  {key}. {desc}")
    print("  exit. 退出")
    
    while True:
        choice = input("\n请选择 (0-4): ").strip()
        
        if choice == 'exit':
            break
        elif choice == '0':
            for key in ['1', '2', '3', '4']:
                desc, func = examples[key]
                print(f"\n{'#' * 60}\n# {desc}\n{'#' * 60}")
                func()
        elif choice in examples:
            desc, func = examples[choice]
            if func:
                print(f"\n{'#' * 60}\n# {desc}\n{'#' * 60}")
                func()
        else:
            print("无效选择，请重试")

if __name__ == '__main__':
    main()
