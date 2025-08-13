# -*- mode: python ; coding: utf-8 -*-

import sys
import os

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 应用程序信息
app_name = 'LLM代理服务'
app_version = '1.0.0'
app_description = 'LLM代理服务GUI应用程序'

# 主程序入口
main_script = 'start_gui.py'

# 需要包含的数据文件
datas = [
    ('config.ini', '.'),
    ('app_icon.png', '.'),
]

# 需要包含的Python模块
hiddenimports = [
    'tkinter',
    'configparser',
    'threading',
    'subprocess',
    'fastapi',
    'uvicorn',
    'httpx',
    'pydantic',
]

# 打包配置
a = Analysis(
    [main_script],
    pathex=[current_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 设置可执行文件
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico',  # 如果有.ico图标文件
)

# 收集所有文件
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=app_name,
)