import requests
import json
import base64
import os
import time
from typing import Dict, List, Any
from config import (
    BAIDU_API_KEY, 
    BAIDU_API_SECRET, 
    BAIDU_TOKEN_URL, 
    BAIDU_IMAGE_RECOGNIZE_URL,
    BAIDU_IMAGE_RESULT_URL,
    DEMO_MODE
)
import logging

# 配置详细日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class BaiduAPIClient:
    """百度图像识别API客户端"""
    
    def __init__(self):
        self.api_key = BAIDU_API_KEY
        self.api_secret = BAIDU_API_SECRET
        self.access_token = None
        self.token_expire_time = 0
    
    def _parse_description(self, description: str) -> List[Dict[str, Any]]:
        """
        从AI返回的文本描述中提取对象、属性等信息
        
        由于百度的图像内容理解API返回的是自然语言描述，
        我们需要使用启发式方法和关键词匹配来提取相关信息
        """
        import re
        
        objects = []
        
        if not description:
            return objects
        
        # 定义关键词和对应的分数
        # 这些关键词用于识别玩具中的禁忌元素
        keyword_patterns = {
            # 禁忌动物
            '猪|小猪|猪形|猪玩具': {'name': '猪', 'score': 0.9, 'category': 'animal'},
            '狗|小狗|狗形|犬': {'name': '狗', 'score': 0.9, 'category': 'animal'},
            '兔子|小兔|兔形': {'name': '兔子', 'score': 0.85, 'category': 'animal'},
            '驴|毛驴': {'name': '驴', 'score': 0.85, 'category': 'animal'},
            
            # 女性形象
            '女性|女人|妇女|少女|女孩': {'name': '女性形象', 'score': 0.8, 'category': 'figure'},
            '露.*面|裸露|未着': {'name': '裸露皮肤', 'score': 0.85, 'category': 'figure'},
            
            # 禁忌颜色（仅做识别，合规性检查在rules_checker中)
            '纯红|深红|火红': {'name': '纯红色', 'score': 0.8, 'category': 'color'},
            '鲜黄|亮黄|金黄': {'name': '亮黄色', 'score': 0.8, 'category': 'color'},
            
            # 正面属性
            '毛绒|彩绒|绒毛': {'name': '毛绒玩具', 'score': 0.85, 'category': 'material'},
            '几何|花纹|图案|装饰': {'name': '图案装饰', 'score': 0.7, 'category': 'feature'},
            '伊斯兰|几何花纹|伊斯兰教': {'name': '伊斯兰几何花纹', 'score': 0.8, 'category': 'feature'},
            '骆驼|椰枣树|沙漠': {'name': '沙特本土元素', 'score': 0.75, 'category': 'feature'},

            # 材质/功能/标签相关（用于触发通用禁忌规则）
            'pvc|聚氯乙烯|邻苯二甲酸酯|塑化剂': {'name': 'PVC材质', 'score': 0.85, 'category': 'material'},
            '诵经|古兰经音乐|宗教音乐': {'name': '诵经音乐', 'score': 0.85, 'category': 'function'},
            '闪光|频闪|高频闪': {'name': '闪光频率', 'score': 0.8, 'category': 'function'},
            '阿拉伯语标签|无阿语|未标注阿语': {'name': '阿语标签缺失', 'score': 0.8, 'category': 'label'},
            'saso|认证|无认证|未提供认证': {'name': 'SASO认证信息', 'score': 0.75, 'category': 'certification'},
            '魔鬼|最美|唯一|绝对': {'name': '敏感宣传文案', 'score': 0.75, 'category': 'text'}
        }
        
        # 在描述中查找关键词
        found_keywords = set()
        for pattern, info in keyword_patterns.items():
            if re.search(pattern, description, re.IGNORECASE):
                if info['name'] not in found_keywords:
                    objects.append({
                        'name': info['name'],
                        'score': info['score'],
                        'category': info['category']
                    })
                    found_keywords.add(info['name'])
        
        # 如果没有找到任何关键词，至少返回一个通用的识别结果
        if not objects:
            objects.append({
                'name': '玩具',
                'score': 0.5,
                'category': 'general'
            })
        
        logging.debug(f"从描述中提取出的对象: {objects}")
        return objects
    
    def get_access_token(self) -> str:
        """获取百度API访问令牌"""
        import time
        
        # 如果token未过期，直接返回
        if self.access_token and time.time() < self.token_expire_time:
            logging.debug("访问令牌仍然有效，缓存返回")
            return self.access_token
        
        try:
            logging.info("开始获取新的访问令牌...")
            logging.debug(f"API密钥: {self.api_key[:10]}...（已掩盖）")
            
            params = {
                'grant_type': 'client_credentials',
                'client_id': self.api_key,
                'client_secret': self.api_secret
            }
            
            logging.debug(f"请求令牌URL: {BAIDU_TOKEN_URL}")
            response = requests.get(BAIDU_TOKEN_URL, params=params, timeout=10)
            response.raise_for_status()
            logging.debug(f"HTTP状态码: {response.status_code}")
            
            result = response.json()
            logging.debug(f"令牌响应: {result}")
            
            if 'access_token' in result:
                self.access_token = result['access_token']
                self.token_expire_time = int(time.time()) + result.get('expires_in', 2592000) - 300
                logging.info(f"✓ 成功获得访问令牌，有效期: {result.get('expires_in', 2592000)}秒")
                return self.access_token
            else:
                error_msg = result.get('error_description', result.get('error', '未知错误'))
                logging.error(f"获取token失败: {error_msg}")
                raise Exception(f"获取token失败: {error_msg}")
        
        except requests.exceptions.Timeout:
            error_msg = "连接超时，无法连接到百度API服务器（>10秒），请检查网络连接"
            logging.error(f"【错误】{error_msg}")
            return None
        except requests.exceptions.ConnectionError:
            error_msg = "无法连接到百度API服务器，请检查网络连接和URL是否正确"
            logging.error(f"【错误】{error_msg}")
            return None
        except Exception as e:
            error_msg = f"获取百度API访问令牌失败: {str(e)}"
            logging.error(f"【错误】{error_msg}")
            return None
    
    def recognize_image(self, image_path: str) -> Dict[str, Any]:
        """
        使用图像内容理解API识别图像内容（两步调用）
        
        第一步：提交图像，获取任务ID
        第二步：轮询获取任务结果
        
        如果启用了DEMO_MODE，将使用本地模拟数据代替真实API调用
        """
        try:
            logging.info(f"开始识别图像: {image_path}")
            
            # 演示模式处理
            if DEMO_MODE:
                logging.info("【演示模式】使用本地模拟数据")
                if not os.path.exists(image_path):
                    return {
                        'success': False,
                        'error': f'找不到文件: {image_path}',
                        'results': []
                    }
                
                # 根据文件名返回不同的模拟结果
                filename = os.path.basename(image_path).lower()
                
                # 模拟识别结果
                if 'pig' in filename or 'piggy' in filename:
                    demo_results = [
                        {'name': '猪', 'score': 0.95},
                        {'name': '毛绒玩具', 'score': 0.89}
                    ]
                elif 'dog' in filename:
                    demo_results = [
                        {'name': '狗', 'score': 0.92},
                        {'name': '玩具', 'score': 0.87}
                    ]
                elif 'rabbit' in filename or 'bunny' in filename:
                    demo_results = [
                        {'name': '兔子', 'score': 0.88},
                        {'name': '毛绒玩具', 'score': 0.91}
                    ]
                elif 'red' in filename:
                    demo_results = [
                        {'name': '红色', 'score': 0.85},
                        {'name': '毛绒玩具', 'score': 0.90}
                    ]
                else:
                    demo_results = [
                        {'name': '毛绒玩具', 'score': 0.92},
                        {'name': '伊斯兰几何花纹', 'score': 0.88}
                    ]
                
                logging.info(f"✓ 演示模式识别完成，检测到 {len(demo_results)} 个对象")
                return {
                    'success': True,
                    'results': demo_results,
                    'raw_response': {'error_code': 0, 'demo_mode': True}
                }
            
            # 真实API调用 - 第一步：读取图像并提交任务
            if not os.path.exists(image_path):
                error_msg = f'找不到文件: {image_path}'
                logging.error(f"【错误】{error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'results': []
                }
            
            logging.debug(f"文件存在，开始读取...")
            with open(image_path, 'rb') as f:
                image_content = f.read()
            
            logging.debug(f"图像文件大小: {len(image_content)} 字节")
            image_base64 = base64.b64encode(image_content).decode('utf-8')
            logging.debug(f"Base64编码完成，长度: {len(image_base64)}")
            
            # 获取访问令牌
            logging.info("获取百度API访问令牌...")
            access_token = self.get_access_token()
            if not access_token:
                error_msg = '无法获取百度API访问令牌'
                logging.error(f"【错误】{error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'results': []
                }
            
            # 第一步：提交任务请求
            logging.info("【步骤1】提交图像理解任务...")
            request_url = f"{BAIDU_IMAGE_RECOGNIZE_URL}?access_token={access_token}"
            
            # 重要：图像内容理解API要求 JSON 格式！
            headers = {
                'Content-Type': 'application/json'
            }
            
            # image 参数不需要 urlencode，直接用 base64 即可
            request_body = {
                'image': image_base64,
                'question': '这张玩具图片中有什么物体、动物、场景或其他内容？请详细列出所有识别到的内容。'
            }
            
            logging.debug(f"发送请求到: {BAIDU_IMAGE_RECOGNIZE_URL}")
            response = requests.post(
                request_url, 
                headers=headers, 
                json=request_body,  # 使用 json 参数而不是 data
                timeout=15
            )
            response.raise_for_status()
            
            request_result = response.json()
            logging.debug(f"任务请求响应: {json.dumps(request_result, ensure_ascii=False)}")
            
            # 检查是否成功（成功时没有 error_code 字段，只有 result.task_id）
            if 'error_code' in request_result and request_result.get('error_code') != 0:
                error_msg = request_result.get('error_msg', '提交任务失败')
                error_code = request_result.get('error_code')
                logging.error(f"【错误】提交任务失败: {error_msg} (错误代码: {error_code})")
                logging.error(f"完整响应: {json.dumps(request_result, ensure_ascii=False)}")
                return {
                    'success': False,
                    'error': error_msg,
                    'error_code': error_code,
                    'results': []
                }
            
            # 获取任务ID
            task_id = request_result.get('result', {}).get('task_id')
            if not task_id:
                error_msg = '无法获得任务ID'
                logging.error(f"【错误】{error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'results': []
                }
            
            logging.info(f"✓ 任务已提交，任务ID: {task_id}")
            
            # 第二步：轮询获取结果
            logging.info("【步骤2】轮询获取任务结果...")
            max_retries = 60  # 最多尝试60次
            retry_interval = 2  # 每次间隔2秒（总等待时间：2分钟）
            
            for attempt in range(max_retries):
                time.sleep(retry_interval)
                logging.debug(f"尝试获取结果 (第 {attempt + 1}/{max_retries} 次)...")
                
                get_result_url = f"{BAIDU_IMAGE_RESULT_URL}?access_token={access_token}"
                result_request_body = {'task_id': task_id}
                
                result_response = requests.post(
                    get_result_url, 
                    headers=headers,  # 使用相同的 JSON headers
                    json=result_request_body,  # 使用 json 参数
                    timeout=30  # 增加单个请求超时时间
                )
                result_response.raise_for_status()
                
                result = result_response.json()
                logging.debug(f"获取结果响应: {json.dumps(result, ensure_ascii=False)[:500]}...")
                
                # 检查是否有错误（成功时没有 error_code 字段）
                if 'error_code' in result and result.get('error_code') != 0:
                    error_msg = result.get('error_msg', '获取结果失败')
                    logging.error(f"【错误】获取结果失败: {error_msg}")
                    return {
                        'success': False,
                        'error': error_msg,
                        'error_code': result.get('error_code'),
                        'results': []
                    }
                
                # 检查任务状态（ret_code: 0=success, 1=processing）
                result_data = result.get('result', {})
                ret_code = result_data.get('ret_code')
                ret_msg = result_data.get('ret_msg', 'unknown')
                logging.debug(f"任务状态: ret_code={ret_code}, ret_msg={ret_msg}")
                
                if ret_code == 0:
                    # 任务完成，处理识别结果
                    logging.info("✓ 任务完成，处理识别结果...")
                    
                    description = result_data.get('description', '')
                    logging.debug(f"API返回描述: {description}")
                    
                    # 从description文本中提取对象信息
                    recognized_objects = self._parse_description(description)
                    
                    logging.info(f"✓ 识别完成，检测到 {len(recognized_objects)} 个对象/属性")
                    return {
                        'success': True,
                        'results': recognized_objects,
                        'raw_response': result,
                        'description': description
                    }
                
                elif ret_code == 1:
                    # 任务仍在处理中，继续轮询
                    logging.debug(f"任务仍在处理中，等待中...")
                    continue
                
                else:
                    error_msg = f"未知的任务状态: ret_code={ret_code}, ret_msg={ret_msg}"
                    logging.error(f"【错误】{error_msg}")
                    return {
                        'success': False,
                        'error': error_msg,
                        'results': []
                    }
            
            # 超时
            error_msg = f"任务处理超时（已等待 {max_retries * retry_interval} 秒，建议检查网络或稍后重试）"
            logging.error(f"【错误】{error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'results': []
            }
        
        except requests.exceptions.Timeout:
            error_msg = "API请求超时（>15秒），请检查网络连接或稍后重试"
            logging.error(f"【错误】{error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'results': []
            }
        except requests.exceptions.ConnectionError as e:
            error_msg = f"无法连接到百度API: {str(e)}，请检查网络连接"
            logging.error(f"【错误】{error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'results': []
            }
        except Exception as e:
            error_msg = f'API调用异常: {str(e)}'
            logging.error(f"【错误】{error_msg}")
            logging.exception("详细的异常堆栈:")
            return {
                'success': False,
                'error': error_msg,
                'results': []
            }
    
    def recognize_image_url(self, image_url: str) -> Dict[str, Any]:
        """
        识别URL图像内容
        """
        try:
            # 获取token
            access_token = self.get_access_token()
            if not access_token:
                return {
                    'success': False,
                    'error': '无法获取百度API访问令牌',
                    'results': []
                }
            
            # 调用API
            url = f"{BAIDU_IMAGE_RECOGNIZE_URL}?access_token={access_token}"
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'url': image_url
            }
            
            response = requests.post(url, headers=headers, data=data, timeout=15)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('error_code') == 0:
                # 成功识别
                results = result.get('result', [])
                return {
                    'success': True,
                    'results': results,
                    'raw_response': result
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error_msg', '图像识别失败'),
                    'error_code': result.get('error_code'),
                    'results': []
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'API调用异常: {str(e)}',
                'results': []
            }
