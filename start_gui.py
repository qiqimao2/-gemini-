#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM代理服务GUI启动器
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入并启动GUI
from gui_app import main

if __name__ == "__main__":
    main()