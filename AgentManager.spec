# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Agent Manager (Windows, one-directory bundle)."""

block_cipher = None

a = Analysis(
    ['gui_main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('.env.example', '.'),
        ('version.py',   '.'),
    ],
    hiddenimports=[
        # litellm pulls in many providers dynamically
        'litellm',
        'litellm.main',
        'litellm.utils',
        'litellm.integrations',
        'litellm.proxy',
        'tiktoken',
        'tiktoken_ext',
        'tiktoken_ext.openai_public',
        # pygame SDL backend
        'pygame',
        'pygame.mixer',
        'pygame.time',
        # PyQt6
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        # misc
        'jinja2',
        'dotenv',
        'pydantic',
        'httpx',
        'openai',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'scipy', 'PIL'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AgentManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # brak okna konsoli
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,              # można podać ścieżkę do .ico
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AgentManager',
)
