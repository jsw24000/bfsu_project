#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sys
from typing import Dict, Any
from baidu_api import BaiduAPIClient
from rules_checker import RulesChecker

class ToyComplianceChecker:
    """玩具出口合规检查系统"""
    
    def __init__(self):
        self.baidu_client = BaiduAPIClient()
        self.rules_checker = RulesChecker()
        self.last_results = None
    
    def check_image(self, image_path: str) -> Dict[str, Any]:
        """
        审查单个玩具图片
        
        参数：
            image_path: 图片本地路径
        
        返回：合规检查报告
        """
        print(f"\n【开始审查】处理图片: {image_path}")
        print("-" * 60)
        
        # 第一步：使用百度API识别图片
        print("【步骤1】调用百度图像识别API...")
        api_result = self.baidu_client.recognize_image(image_path)
        
        if not api_result['success']:
            print(f"【错误】图像识别失败: {api_result['error']}")
            return {
                'success': False,
                'error': api_result['error'],
                'image_path': image_path
            }
        
        print(f"【成功】识别完成，检测到 {len(api_result['results'])} 个对象")
        
        # 第二步：应用合规规则检查
        print("【步骤2】应用合规规则检查...")
        analysis = self.rules_checker.analyze_image_recognition(api_result['results'])
        
        # 添加图片路径和API返回结果
        analysis['success'] = True
        analysis['image_path'] = image_path
        analysis['api_response'] = api_result
        
        self.last_results = analysis
        
        return analysis
    
    def print_report(self, analysis_result: Dict[str, Any]) -> None:
        """打印可读的合规报告"""
        if not analysis_result.get('success', False):
            error = analysis_result.get('error', '未知错误')
            print(f"\n【审查失败】{error}")
            
            # 打印诊断建议
            if 'error_code' in analysis_result:
                print(f"\n【诊断信息】")
                print(f"  - 错误代码: {analysis_result['error_code']}")
            
            if '无法获取' in error:
                print("\n【可能的原因】")
                print("  1. API密钥或密钥无效")
                print("  2. 网络连接无法访问百度API")
                print("  3. 百度API账户配额已用完")
            elif '找不到文件' in error:
                print("\n【可能的原因】")
                print("  1. 图像文件路径不正确")
                print("  2. 文件已被删除或移动")
            elif '超时' in error:
                print("\n【可能的原因】")
                print("  1. 网络连接缓慢")
                print("  2. 百度API服务器响应缓慢")
            
            return
        
        report = self.rules_checker.generate_compliance_report(analysis_result)
        print("\n" + report)
    
    def save_report(self, analysis_result: Dict[str, Any], output_file: str = None) -> str:
        """
        保存审查报告为JSON和TXT格式
        
        返回：保存的文件路径
        """
        if not analysis_result.get('success', False):
            return None
        
        # 生成输出文件名
        if output_file is None:
            image_name = os.path.splitext(os.path.basename(analysis_result['image_path']))[0]
            output_file = f"compliance_report_{image_name}.json"
        
        # 保存JSON报告
        json_output = {
            'image': analysis_result['image_path'],
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'compliance': {
                'overall_compliant': analysis_result['overall_compliant'],
                'score': analysis_result['compliance_score'],
                'summary': analysis_result['summary']
            },
            'detected_objects': analysis_result['detected_objects'],
            'violations': analysis_result['violations']
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_output, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 报告已保存: {output_file}")
        
        # 保存文本报告
        txt_output = output_file.replace('.json', '.txt')
        report_text = self.rules_checker.generate_compliance_report(analysis_result)
        with open(txt_output, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        print(f"✓ 文本报告已保存: {txt_output}")
        
        return output_file
    
    def batch_check(self, image_directory: str) -> Dict[str, Any]:
        """
        批量审查目录中的所有图片
        
        参数：
            image_directory: 包含图片的目录路径
        
        返回：批量审查结果汇总
        """
        supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
        image_files = []
        
        # 查找所有支持的图片格式
        for file in os.listdir(image_directory):
            if file.lower().endswith(supported_formats):
                full_path = os.path.join(image_directory, file)
                if os.path.isfile(full_path):
                    image_files.append(full_path)
        
        if not image_files:
            print(f"【警告】目录 {image_directory} 中未找到图片文件")
            return {
                'total': 0,
                'results': []
            }
        
        print(f"\n【批量审查】找到 {len(image_files)} 个图片文件")
        
        batch_results = {
            'total': len(image_files),
            'compliant_count': 0,
            'non_compliant_count': 0,
            'results': []
        }
        
        for i, image_path in enumerate(image_files, 1):
            print(f"\n[{i}/{len(image_files)}] 处理: {os.path.basename(image_path)}")
            
            result = self.check_image(image_path)
            
            if result.get('success', False):
                if result['overall_compliant']:
                    batch_results['compliant_count'] += 1
                    status = "✓ 合规"
                else:
                    batch_results['non_compliant_count'] += 1
                    status = "✗ 不合规"
                
                print(f"  结果: {status} (评分: {result['compliance_score']}/100)")
            else:
                print(f"  结果: ✗ 处理失败 ({result.get('error', '未知错误')})")
            
            batch_results['results'].append(result)
        
        return batch_results
    
    def interactive_mode(self):
        """交互式审查模式"""
        print("\n" + "=" * 60)
        print("玩具出口合规审查系统 - 交互模式")
        print("=" * 60)
        print("\n命令列表:")
        print("  check <图片路径>  - 审查单个图片")
        print("  batch <目录路径>  - 批量审查目录中的图片")
        print("  report            - 显示上次审查报告")
        print("  save              - 保存上次审查报告")
        print("  help              - 显示帮助信息")
        print("  exit              - 退出程序")
        print("-" * 60 + "\n")
        
        while True:
            try:
                user_input = input("请输入命令> ").strip()
                
                if not user_input:
                    continue
                
                parts = user_input.split(maxsplit=1)
                command = parts[0].lower()
                arg = parts[1] if len(parts) > 1 else None
                
                if command == 'exit':
                    print("感谢使用！再见。")
                    break
                
                elif command == 'check':
                    if not arg:
                        print("【错误】请提供图片路径")
                        continue
                    
                    if not os.path.exists(arg):
                        print(f"【错误】文件不存在: {arg}")
                        continue
                    
                    result = self.check_image(arg)
                    self.print_report(result)
                
                elif command == 'batch':
                    if not arg:
                        print("【错误】请提供目录路径")
                        continue
                    
                    if not os.path.isdir(arg):
                        print(f"【错误】目录不存在: {arg}")
                        continue
                    
                    batch_results = self.batch_check(arg)
                    print("\n【批量审查汇总】")
                    print(f"  总计: {batch_results['total']} 个")
                    print(f"  合规: {batch_results['compliant_count']} 个")
                    print(f"  不合规: {batch_results['non_compliant_count']} 个")
                
                elif command == 'report':
                    if self.last_results:
                        self.print_report(self.last_results)
                    else:
                        print("【提示】还未进行任何审查")
                
                elif command == 'save':
                    if self.last_results:
                        self.save_report(self.last_results)
                    else:
                        print("【提示】没有要保存的报告")
                
                elif command == 'help':
                    print("功能说明:")
                    print("  • check: 对单个玩具图片进行合规审查")
                    print("  • batch: 对目录中的所有图片进行批量审查")
                    print("  • report: 查看上次审查的详细报告")
                    print("  • save: 将报告保存为JSON和TXT文件")
                
                else:
                    print(f"【错误】未知命令: {command}。输入 'help' 查看帮助。")
            
            except KeyboardInterrupt:
                print("\n\n已中断。")
                break
            except Exception as e:
                print(f"【错误】{str(e)}")

def main():
    """主程序入口"""
    import logging
    logging.getLogger().setLevel(logging.INFO)  # 显示INFO级别以上的日志
    
    checker = ToyComplianceChecker()
    
    # 检查是否启用了演示模式
    from config import DEMO_MODE
    if DEMO_MODE:
        print("\n" + "="*70)
        print("【演示模式已启用】系统将使用本地模拟数据")
        print("如果需要使用真实百度API，请在 config.py 中设置 DEMO_MODE = False")
        print("="*70 + "\n")
    
    # 如果提供了命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == 'check' and len(sys.argv) > 2:
            print("\n" + "="*70)
            print("【玩具出口合规审查】")
            print("="*70)
            image_path = sys.argv[2]
            if os.path.exists(image_path):
                result = checker.check_image(image_path)
                checker.print_report(result)
                if result.get('success'):
                    checker.save_report(result)
            else:
                print(f"【错误】文件不存在: {image_path}")
                print(f"\n【提示】请使用完整路径，例如:")
                print(f"  python main.py check C:\\toys\\example.jpg")
        
        elif sys.argv[1].lower() == 'batch' and len(sys.argv) > 2:
            directory = sys.argv[2]
            if os.path.isdir(directory):
                batch_results = checker.batch_check(directory)
            else:
                print(f"【错误】目录不存在: {directory}")
        
        elif sys.argv[1].lower() == 'diagnose':
            print("运行诊断工具...")
            os.system("python diagnose.py")
        
        elif sys.argv[1].lower() in ['-h', '--help', 'help']:
            print("\n玩具出口合规审查系统 - 使用帮助")
            print("="*70)
            print("\n命令用法:")
            print("  python main.py                        - 进入交互模式")
            print("  python main.py check <图片路径>      - 审查单个图片")
            print("  python main.py batch <目录路径>      - 批量审查")
            print("  python main.py diagnose               - 运行诊断工具")
            print("\n示例:")
            print("  python main.py check toy.jpg")
            print("  python main.py batch toys/")
            print("\n【诊断帮助】")
            print("  如果遇到问题，运行:")
            print("  python diagnose.py")
        
        else:
            print(f"【错误】未知命令: {sys.argv[1]}")
            print("运行 'python main.py -h' 查看帮助")
    
    else:
        # 进入交互模式
        checker.interactive_mode()

if __name__ == '__main__':
    main()
