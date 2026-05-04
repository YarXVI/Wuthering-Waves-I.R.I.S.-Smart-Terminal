# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 配置：打包 launcher.py
生成独立的 Aimis.exe 启动器
"""

import sys
from pathlib import Path
import os

block_cipher = None

# 固定路径
ROOT = Path("E:/agent办公室/工程区/agent-core")

a = Analysis(
    [str(ROOT / 'launcher.py')],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        (str(ROOT / 'agent_core'), 'agent_core'),
        (str(ROOT / 'server'), 'server'),
        (str(ROOT / 'config'), 'config'),
        (str(ROOT / '.env'), '.env'),
        (str(ROOT / '.env.example'), '.env.example'),
    ],
    hiddenimports=[
        'uvicorn',
        'fastapi',
        'pydantic',
        'websockets',
        'agent_core',
        'server',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Aimis',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
