#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web应用 - 玩具出口合规审查系统
"""

from flask import Flask, render_template, request, jsonify
import os
import json
from werkzeug.utils import secure_filename
from main import ToyComplianceChecker

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制上传文件大小为16MB
app.config['UPLOAD_FOLDER'] = 'uploads'

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

# 创建上传目录
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 初始化合规检查器
checker = ToyComplianceChecker()

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check_image():
    """处理图片审查请求"""
    try:
        # 检查是否有文件上传
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': '未找到上传的图片'})
        
        file = request.files['image']
        
        # 检查文件名是否为空
        if file.filename == '':
            return jsonify({'success': False, 'error': '未选择文件'})
        
        # 检查文件类型
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': '不支持的文件格式，请上传 PNG、JPG、JPEG、GIF 或 BMP 格式的图片'})
        
        # 保存文件
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 执行合规检查
        result = checker.check_image(filepath)
        
        # 转换为前端需要的格式
        if result.get('success'):
            response = {
                'success': True,
                'can_export': result.get('overall_compliant', False),
                'detected_objects': result.get('detected_objects', []),
                'violations': [
                    {
                        'rule': v.get('type', '未知'),
                        'reason': v.get('reason', '未提供原因')
                    }
                    for v in result.get('violations', [])
                ],
                'suggestions': [v.get('suggestion', '') for v in result.get('violations', []) if v.get('suggestion')],
                'detailed_checks': {
                    'no_forbidden_animals': result.get('summary', {}).get('animals_check', True),
                    'no_female_representation': result.get('summary', {}).get('female_image_check', True),
                    'no_religious_symbols': result.get('summary', {}).get('religion_check', True),
                    'color_compliance': True  # 暂时默认通过，后续可以增强
                }
            }
        else:
            response = result
        
        # 清理上传的文件（可选）
        # os.remove(filepath)
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'success': False, 'error': f'处理失败: {str(e)}'})

if __name__ == '__main__':
    print("玩具出口合规审查系统 - Web服务")
    print("请在浏览器中访问: http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
