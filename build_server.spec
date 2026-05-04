# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 配置
打包 Aimis 后端服务
"""

import sys
from pathlib import Path

block_cipher = None

# 项目根目录
ROOT = Path(__file__).parent

# 收集需要包含的额外文件
datas = [
    (str(ROOT / 'agent_core'),
     'agent_core'),
    (str(ROOT / 'server'),
     'server'),
    (str(ROOT / 'config'),
     'config'),
    (str(ROOT / '.env'),
     '.env'),
]

a = Analysis(
    [str(ROOT / 'server' / 'main.py')],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'uvicorn',
        'fastapi',
        'pydantic',
        'websockets',
        'agent_core',
        'agent_core.*',
        'server.*',
        'server.routers.*',
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
    name='aimis-server',
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
