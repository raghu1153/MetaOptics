# -*- mode: python ; coding: utf-8 -*-
# MetaOptics 3.0 — PyInstaller build spec
# Updated: About.PNG and Instructions.PNG removed (replaced by native UI)
# Kept: Cross.png, Fin.png, logo.ico

a = Analysis(
    ['metaOptics.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('Cross.png',  '.'),
        ('Fin.png',    '.'),
        ('logo.ico',   '.'),
        ('metaData.py',    '.'),
        ('gdsModule.py',   '.'),
    ],
    hiddenimports=[
        'gdstk',
        'xlrd',
        'scipy.interpolate',
        'PIL.ImageTk',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'PyQt5', 'PyQt6', 'PySide2', 'PySide6',
        'scipy.io', 'scipy.sparse', 'scipy.stats', 'scipy.signal',
        'scipy.spatial', 'scipy.optimize', 'scipy.integrate',
        'scipy.ndimage', 'scipy.linalg', 'scipy.fft', 'scipy.fftpack',
        'scipy.cluster', 'scipy.constants', 'scipy.datasets',
        'scipy.misc', 'scipy.odr', 'scipy.special',
        'matplotlib.testing', 'matplotlib.tests',
        'matplotlib.backends.backend_qt5agg',
        'matplotlib.backends.backend_qt6agg',
        'matplotlib.backends.backend_gtk3agg',
        'matplotlib.backends.backend_gtk4agg',
        'matplotlib.backends.backend_webagg',
        'matplotlib.backends.backend_wxagg',
        'matplotlib.backends.backend_nbagg',
        'numpy.testing', 'numpy.tests',
        'tkinter.test', 'test', 'unittest',
        'pytest', 'nose',
        'IPython', 'jupyter', 'notebook',
        'pandas', 'sympy',
    ],
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
    name='MetaOptics',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # no terminal window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['logo.ico'],
)
