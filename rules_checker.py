import json
from typing import Dict, List, Any, Tuple
from difflib import SequenceMatcher
from config import RULE_FILE

class RulesChecker:
    """玩具出口合规规则检查器"""
    
    def __init__(self, rule_file: str = RULE_FILE):
        self.rule_file = rule_file
        self.rules = self._load_rules()
        self.taboo_animals = self._extract_taboo_animals()
        self.taboo_colors = self._extract_taboo_colors()
        self.female_rules = self._extract_female_rules()
        self.religion_rules = self._extract_religion_rules()
        self.general_taboo_rules = self._extract_general_taboo_rules()
        self.warnings = []

    def _extract_female_rules(self) -> List[Dict[str, Any]]:
        """提取女性形象相关规则"""
        rules = []
        for item in self.rules.get('figure_pattern_taboo', {}).get('data', []):
            if item.get('sub_category') == '女性形象' and item.get('compliance') == 'non_compliant':
                rules.append(item)
        return rules

    def _extract_religion_rules(self) -> List[Dict[str, Any]]:
        """提取宗教禁忌相关规则"""
        return self.rules.get('religion_taboo', {}).get('data', [])

    def _extract_general_taboo_rules(self) -> List[Dict[str, Any]]:
        """提取可用于图像文本语义匹配的通用禁忌规则"""
        rule_sections = [
            'material_compliance',
            'function_compliance',
            'import_compliance',
            'arabic_expression',
            'festival_compliance'
        ]
        result = []
        for section in rule_sections:
            for item in self.rules.get(section, {}).get('data', []):
                if item.get('compliance') == 'non_compliant':
                    result.append(item)
        return result
    
    def _load_rules(self) -> Dict[str, Any]:
        """加载规则JSON文件"""
        try:
            with open(self.rule_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"【错误】规则文件未找到: {self.rule_file}")
            return {}
        except json.JSONDecodeError:
            print(f"【错误】规则文件格式错误: {self.rule_file}")
            return {}
    
    def _extract_taboo_animals(self) -> Dict[str, Dict[str, str]]:
        """从规则中提取禁忌动物列表"""
        taboo_animals = {}
        
        if 'figure_pattern_taboo' in self.rules:
            for item in self.rules['figure_pattern_taboo'].get('data', []):
                if item.get('sub_category') == '禁忌动物':
                    content_cn = item.get('content_cn', '')
                    # 提取动物名称
                    animal_name = self._extract_animal_name(content_cn)
                    if animal_name:
                        taboo_animals[animal_name] = {
                            'id': item.get('id'),
                            'reason': item.get('reason_cn', ''),
                            'suggest': item.get('suggest_cn', ''),
                            'compliance': item.get('compliance', '')
                        }
        
        return taboo_animals
    
    def _extract_animal_name(self, content: str) -> str:
        """从内容字符串中提取动物名称"""
        # 提取常见的禁忌动物名称
        animals = {
            '小猪': '猪',
            '猪': '猪',
            '小狗': '狗',
            '狗': '狗',
            '犬': '狗'
        }
        
        for key, value in animals.items():
            if key in content:
                return value
        
        return None
    
    def _extract_taboo_colors(self) -> Dict[str, Dict[str, str]]:
        """从规则中提取禁忌颜色"""
        taboo_colors = {}
        
        if 'color_taboo' in self.rules:
            for item in self.rules['color_taboo'].get('data', []):
                if item.get('compliance') == 'non_compliant':
                    content_cn = item.get('content_cn', '')
                    color_info = self._extract_color_info(content_cn, item)
                    if color_info:
                        color_name = color_info['name']
                        taboo_colors[color_name] = {
                            'id': item.get('id'),
                            'reason': item.get('reason_cn', ''),
                            'suggest': item.get('suggest_cn', ''),
                            'rgb': color_info.get('rgb'),
                            'compliance': item.get('compliance', '')
                        }
        
        return taboo_colors
    
    def _extract_color_info(self, content: str, item: Dict) -> Dict[str, Any]:
        """从内容中提取颜色信息"""
        color_mapping = {
            '纯红': {'name': '纯红', 'rgb': (255, 0, 0)},
            '亮黄': {'name': '亮黄', 'rgb': (255, 255, 0)},
            'RGB:255,0,0': {'name': '纯红', 'rgb': (255, 0, 0)},
            'RGB:255,255,0': {'name': '亮黄', 'rgb': (255, 255, 0)},
        }
        
        # 尝试从content中匹配颜色
        for color_key, color_value in color_mapping.items():
            if color_key in content:
                return color_value
        
        # 从content_cn中提取
        if '红' in content:
            return {'name': '红色', 'rgb': (255, 0, 0)}
        elif '黄' in content:
            return {'name': '黄色', 'rgb': (255, 255, 0)}
        
        return None
    
    def similarity(self, a: str, b: str) -> float:
        """计算两个字符串的相似度"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def _contains_keyword(self, text: str, candidates: List[str]) -> bool:
        """判断文本是否包含任一关键词"""
        text_lower = text.lower()
        for candidate in candidates:
            if candidate and candidate.lower() in text_lower:
                return True
        return False
    
    def check_animals(self, recognized_objects: List[str]) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        检查识别的对象中是否包含禁忌动物
        
        返回：(是否合规, 违规项列表)
        """
        violations = []
        
        for obj in recognized_objects:
            for taboo_animal, info in self.taboo_animals.items():
                similarity = self.similarity(obj, taboo_animal)
                if similarity > 0.6:  # 相似度阈值
                    violations.append({
                        'type': '禁忌动物',
                        'detected': obj,
                        'taboo': taboo_animal,
                        'confidence': similarity,
                        'reason': info['reason'],
                        'suggestion': info['suggest'],
                        'severity': 'HIGH'
                    })
        
        is_compliant = len(violations) == 0
        return is_compliant, violations
    
    def check_female_image(self, recognized_objects: List[str]) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        检查是否有女性形象（网络/卡通人物等）
        
        返回：(是否合规, 违规项列表)
        """
        violations = []
        female_keywords = ['女', '女性', '女卡', '女孩', '少女', '女人', 'woman', 'female', 'girl', '妇女', '面部', '无头巾']
        
        for obj in recognized_objects:
            for keyword in female_keywords:
                if keyword.lower() in obj.lower():
                    female_rule = self.female_rules[0] if self.female_rules else {}
                    violations.append({
                        'type': '女性形象',
                        'detected': obj,
                        'reason': female_rule.get('reason_cn', '违反沙特保守文化规范'),
                        'suggestion': female_rule.get('suggest_cn', '替换为伊斯兰几何花纹/沙漠椰枣树图案'),
                        'severity': 'HIGH'
                    })
                    break
        
        is_compliant = len(violations) == 0
        return is_compliant, violations
    
    def check_religion_symbols(self, recognized_objects: List[str]) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        检查是否有宗教符号
        """
        violations = []
        religion_keywords = ['清真寺', '穆斯林', '伊斯兰', '古兰经', '先知', '礼拜', '阿拉', 'mosque', 'muslim', '天房', '朝圣']
        
        for obj in recognized_objects:
            for keyword in religion_keywords:
                if keyword.lower() in obj.lower():
                    religion_rule = self.religion_rules[0] if self.religion_rules else {}
                    violations.append({
                        'type': '宗教符号警告',
                        'detected': obj,
                        'reason': religion_rule.get('reason_cn', '玩具上可能包含宗教相关符号或文字，需进一步审核'),
                        'suggestion': religion_rule.get('suggest_cn', '确认是否违反伊斯兰宗教规范'),
                        'severity': 'MEDIUM'
                    })
                    break

        is_compliant = len(violations) == 0
        return is_compliant, violations

    def check_colors(self, recognized_objects: List[str]) -> Tuple[bool, List[Dict[str, Any]]]:
        """检查是否包含禁忌颜色"""
        violations = []
        color_alias = {
            '纯红': ['红', '纯红', '鲜红', '深红', '火红', '大红'],
            '亮黄': ['黄', '亮黄', '鲜黄', '金黄', '明黄']
        }

        for obj in recognized_objects:
            for taboo_color, info in self.taboo_colors.items():
                aliases = color_alias.get(taboo_color, [taboo_color])
                if self._contains_keyword(obj, aliases):
                    violations.append({
                        'type': '禁忌颜色',
                        'detected': obj,
                        'taboo': taboo_color,
                        'reason': info.get('reason', '颜色不符合目标市场要求'),
                        'suggestion': info.get('suggest', '调整为合规配色'),
                        'severity': 'HIGH'
                    })
                    break

        is_compliant = len(violations) == 0
        return is_compliant, violations

    def check_general_taboo_keywords(self, recognized_objects: List[str]) -> Tuple[bool, List[Dict[str, Any]]]:
        """检查材质/功能/标签/表达等通用禁忌关键词"""
        violations = []

        for obj in recognized_objects:
            obj_lower = obj.lower()
            for item in self.general_taboo_rules:
                content = item.get('content_cn', '')
                candidates = [word for word in ['pvc', '邻苯二甲酸酯', '古兰经', '诵经', '闪光', '5hz', '阿拉伯语', '未提供saso', '魔鬼', '最美', '唯一', '绝对'] if word]
                if any(keyword in obj_lower for keyword in [c.lower() for c in candidates]) and any(keyword in content.lower() for keyword in [c.lower() for c in candidates]):
                    violations.append({
                        'type': item.get('sub_category', '通用禁忌'),
                        'detected': obj,
                        'reason': item.get('reason_cn', '命中规则库中的禁忌项'),
                        'suggestion': item.get('suggest_cn', '请根据规则库建议修改'),
                        'severity': 'MEDIUM'
                    })
                    break
        
        is_compliant = len(violations) == 0
        return is_compliant, violations
    
    def analyze_image_recognition(self, recognition_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析百度API的识别结果
        
        返回完整的合规检查报告
        """
        # 提取识别的对象和置信度
        detected_objects = []
        for result in recognition_results:
            if isinstance(result, dict):
                name = result.get('name', '')
                score = result.get('score', 0)
                if name:
                    detected_objects.append({
                        'name': name,
                        'confidence': score
                    })
        
        object_names = [obj['name'] for obj in detected_objects]
        
        # 执行各项检查
        animals_compliant, animal_violations = self.check_animals(object_names)
        female_compliant, female_violations = self.check_female_image(object_names)
        religion_compliant, religion_violations = self.check_religion_symbols(object_names)
        colors_compliant, color_violations = self.check_colors(object_names)
        general_compliant, general_violations = self.check_general_taboo_keywords(object_names)
        
        # 综合评估
        all_violations = animal_violations + female_violations + religion_violations + color_violations + general_violations
        overall_compliant = animals_compliant and female_compliant and religion_compliant and colors_compliant and general_compliant
        
        # 计算合规评分 (0-100)
        if len(object_names) > 0:
            violation_count = len(all_violations)
            compliance_score = max(0, 100 - (violation_count * 30))
        else:
            compliance_score = 100  # 如果无法识别，暂时认为合规
        
        report = {
            'overall_compliant': overall_compliant,
            'compliance_score': compliance_score,
            'detected_objects': detected_objects,
            'violations': all_violations,
            'summary': {
                'animals_check': animals_compliant,
                'female_image_check': female_compliant,
                'religion_check': religion_compliant,
                'color_check': colors_compliant,
                'general_taboo_check': general_compliant
            }
        }
        
        return report
    
    def generate_compliance_report(self, analysis_result: Dict[str, Any]) -> str:
        """
        生成可读的合规报告
        """
        report_text = []
        report_text.append("=" * 60)
        report_text.append("玩具出口合规审查报告（沙特SASO标准）")
        report_text.append("=" * 60)
        
        # 整体合规状态
        status = "✓ 合规" if analysis_result['overall_compliant'] else "✗ 不合规"
        report_text.append(f"\n【整体审查结果】{status}")
        report_text.append(f"【合规评分】{analysis_result['compliance_score']}/100")
        
        # 检测的对象
        if analysis_result['detected_objects']:
            report_text.append("\n【识别的图片元素】")
            for obj in analysis_result['detected_objects']:
                report_text.append(f"  • {obj['name']} (置信度: {obj['confidence']:.2%})")
        
        # 违规项详情
        if analysis_result['violations']:
            report_text.append("\n【发现的问题】")
            for i, violation in enumerate(analysis_result['violations'], 1):
                report_text.append(f"\n  问题 {i}: {violation['type']}")
                report_text.append(f"    检测到: {violation.get('detected', '')}")
                report_text.append(f"    原因: {violation['reason']}")
                report_text.append(f"    建议: {violation['suggestion']}")
                report_text.append(f"    严重程度: {violation['severity']}")
        else:
            report_text.append("\n【审查结论】未发现违规项")
        
        # 合规项总结
        summary = analysis_result['summary']
        report_text.append("\n【检查项总结】")
        report_text.append(f"  禁忌动物检查: {'✓ 通过' if summary['animals_check'] else '✗ 未通过'}")
        report_text.append(f"  女性形象检查: {'✓ 通过' if summary['female_image_check'] else '✗ 未通过'}")
        report_text.append(f"  宗教符号检查: {'✓ 通过' if summary['religion_check'] else '✗ 未通过'}")
        report_text.append(f"  禁忌颜色检查: {'✓ 通过' if summary.get('color_check', True) else '✗ 未通过'}")
        report_text.append(f"  通用禁忌检查: {'✓ 通过' if summary.get('general_taboo_check', True) else '✗ 未通过'}")
        
        # 建议
        if not analysis_result['overall_compliant']:
            report_text.append("\n【后续操作建议】")
            report_text.append("  1. 根据上述发现的问题修改玩具设计")
            report_text.append("  2. 移除所有禁忌元素")
            report_text.append("  3. 确保符合沙特SASO 2902儿童安全认证标准")
            report_text.append("  4. 重新提交审查前进行质量检验")
        else:
            report_text.append("\n【备注】该玩具初步通过图像识别检查，但仍需进行")
            report_text.append("平面设计、材质、工艺等全面评估。")
        
        report_text.append("\n" + "=" * 60)
        
        return "\n".join(report_text)
