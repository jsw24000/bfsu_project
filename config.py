# ============================================================================
# 百度API配置
# ============================================================================
# 如果您还没有有效的百度API密钥，请在以下网址注册:
# https://console.bce.baidu.com/qianfan/ais/console/capabilities/ocr_general

BAIDU_API_KEY = "tSeuJWr3WH7oMa35Czi4H1lf"
BAIDU_API_SECRET = "DQK0MCzHJbMs5O5DzqDLE8AAfvKCDpA5"

# 演示模式: 如果上面的API密钥无效，可以设置为True来使用本地模式
# 在演示模式下，系统会生成虚拟的图像识别结果进行测试
DEMO_MODE = False  # 设置为False使用真实API

# API端点
BAIDU_TOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"
# 图像内容理解API - 分两步调用
# 第一步：提交请求，获取任务ID
BAIDU_IMAGE_RECOGNIZE_URL = "https://aip.baidubce.com/rest/2.0/image-classify/v1/image-understanding/request"
# 第二步：用任务ID获取识别结果
BAIDU_IMAGE_RESULT_URL = "https://aip.baidubce.com/rest/2.0/image-classify/v1/image-understanding/get-result"

# 规则文件路径
RULE_FILE = "rule.json"

# 审查配置
COMPLIANCE_THRESHOLD = 0.6  # 合规性评分阈值（0-1）
MAX_ANIMALS = 3  # 允许分析最多的动物数量
