#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess

def build_executable():
    """使用PyInstaller打包应用程序"""
    
    # 确保使用Python 3.11
    python_cmd = "py -3.11"
    
    # 安装依赖
    print("正在安装依赖...")
    subprocess.run(f"{python_cmd} -m pip install -r requirements.txt", shell=True)
    
    # PyInstaller命令
    cmd = [
        python_cmd, "-m", "PyInstaller",
        "--onefile",  # 打包成单个文件
        "--windowed",  # 不显示控制台窗口
        "--name=LLM代理服务",  # 应用程序名称
        "--add-data=config.ini;.",  # 添加配置文件
        "--add-data=app_icon.png;.",  # 添加PNG图标文件
        "--add-data=app_icon.ico;.",  # 添加ICO图标文件
        "--hidden-import=tkinter",  # 隐藏导入
        "--hidden-import=configparser",
        "--hidden-import=threading",
        "--hidden-import=subprocess",
        "--hidden-import=PIL",  # 添加PIL支持
        "start_gui.py"
    ]
    
    print("正在打包应用程序...")
    print("执行命令:", " ".join(cmd))
    
    result = subprocess.run(" ".join(cmd), shell=True)
    
    if result.returncode == 0:
        print("\n✅ 打包成功！")
        print("可执行文件位置: dist\\LLM代理服务.exe")
        print("\n你可以将 dist 文件夹整个压缩发给其他人使用")
    else:
        print("\n❌ 打包失败，请检查错误信息")
        return False
    
    return True

if __name__ == "__main__":
    build_executable()