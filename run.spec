# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Collect all MySQL Connector submodules
mysql_hidden_imports = collect_submodules('mysql.connector')
mysql_datas = collect_data_files('mysql.connector')

a = Analysis(
    ['run.py'],
    pathex=['C:\\laragon\\www\\papeleria_app'],
    binaries=[],
    datas=[
        ('app/templates', 'app/templates'),
        ('app/static', 'app/static'),
        *mysql_datas  # Agregar archivos de datos de MySQL
    ],
    hiddenimports=[
        'pyimod02_importers',
        'asyncio.DefaultEventLoopPolicy',
        'multiprocessing',
        *mysql_hidden_imports,
        'mysql.connector',
        'mysql.connector.connection',
        'mysql.connector.locales',
        'mysql.connector.pooling',
        'mysql.connector.plugins',
        'mysql.connector.plugins.mysql_native_password',
        'blinker',
        'Brotli',
        'cffi',
        'click',
        'colorama',
        'cssselect2',
        'Flask',
        'Flask_JSON',
        'Flask_Login',
        'Flask_WTF',
        'fonttools',
        'itsdangerous',
        'Jinja2',
        'MarkupSafe',
        'pdfkit',
        'pillow',
        'pycparser',
        'pydyf',
        'pyphen',
        'tinycss2',
        'tinyhtml5',
        'weasyprint',
        'webencodings',
        'Werkzeug',
        'WTForms',
        'zopfli'
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='run',
    debug=True,
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
)