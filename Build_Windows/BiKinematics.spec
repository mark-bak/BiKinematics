# -*- mode: python ; coding: utf-8 -*-

from kivy_deps import sdl2, glew

block_cipher = None

a = Analysis(['C:\\Users\\Mark\\Documents\\Important\\Programming\\BiKinematics\\BiKinematics.py'],
             pathex=['C:\\Users\\Mark\\Documents\\Important\\Programming\\BiKinematics\\Build_Windows',
             'C:\\Users\\Mark\\Documents\\Important\\Programming\\BiKinematics\\.env\\Lib\\site-packages'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz, Tree('C:\\Users\\Mark\\Documents\\Important\\Programming\\BiKinematics'),
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
          name='BiKinematics',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
