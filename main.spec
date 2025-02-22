# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src\\main.py'],
    pathex=[os.path.abspath("src")],
    binaries=[],
    datas=[('resources\\colibri.ico', 'resources'),(os.path.join("resources", "codigos_municipios", "codigos_departamentos.xlsx"), os.path.join("resources", "codigos_municipios")),
    (os.path.join("resources", "codigos_municipios", "codigos_municipios_dian.xlsx"), os.path.join("resources", "codigos_municipios")),
    (os.path.join("resources", "users", "users.xlsx"), os.path.join("resources", "users")),
    (os.path.join("resources", "colibri.png"), "resources")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
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
    icon='resources\\colibri.ico' 

)
