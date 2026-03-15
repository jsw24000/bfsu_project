#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速诊断脚本 - 运行完整的系统诊断
"""

import os
import sys

if __name__ == "__main__":
    print("玩具出口合规审查系统 - 快速诊断\n")
    
    # 导入诊断工具
    import diagnose
    
    # 运行诊断
    diagnose.main()
