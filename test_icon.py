#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试图标是否正确加载
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

def test_icon_display():
    """测试图标显示"""
    root = tk.Tk()
    root.title("图标测试")
    root.geometry("400x300")
    
    # 设置窗口图标
    try:
        root.iconbitmap('app_icon.ico')
        print("✅ ICO图标加载成功")
    except Exception as e:
        print(f"❌ ICO图标加载失败: {e}")
        try:
            # 尝试使用PNG
            icon_image = Image.open('app_icon.png')
            icon_photo = ImageTk.PhotoImage(icon_image)
            root.iconphoto(True, icon_photo)
            print("✅ PNG图标加载成功")
        except Exception as e2:
            print(f"❌ PNG图标也加载失败: {e2}")
    
    # 在界面中显示图片
    try:
        img = Image.open('app_icon.png')
        # 调整图片大小以适应界面
        img = img.resize((200, 200), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        
        label = ttk.Label(root, image=photo)
        label.image = photo  # 保持引用
        label.pack(pady=20)
        
        info_label = ttk.Label(root, text="图片已成功加载到程序中！", font=("Arial", 12))
        info_label.pack()
        
    except Exception as e:
        error_label = ttk.Label(root, text=f"图片加载失败: {e}", font=("Arial", 12))
        error_label.pack(pady=50)
    
    root.mainloop()

if __name__ == "__main__":
    test_icon_display()