# -*- mode: python ; coding: utf-8 -*-

# necessary for MacOS?
import os 
#os.environ['LC_CTYPE'] = "en_US.UTF-8"

os.environ['LC_CTYPE'] = "en_US.UTF-8"
os.environ['LANG'] = "en_US.UTF-8"

#export LC_ALL=en_US.UTF-8
#export LANG=en_US.UTF-8

# work-around for https://github.com/pyinstaller/pyinstaller/issues/4064
import distutils
if distutils.distutils_path.endswith('__init__.py'):
    distutils.distutils_path = os.path.dirname(distutils.distutils_path)

from PyInstaller.utils.hooks import collect_data_files
from numpy import loadtxt
import ants
import shutil

block_cipher = None

#@TODO: This is stupid, but it works. It solves some issues with dependencies not properly included
hidden_imports = loadtxt("requirements.txt", comments="#", delimiter=",", unpack=False, dtype=str)
hidden_imports = [x.split("=")[0] for x in hidden_imports] + ["medpy", "ants", "sklearn", "scikit-learn", "statsmodels", "gevent", "distutils"]
hidden_imports = [x.lower() for x in hidden_imports]

print("hidden imports: ")
print(hidden_imports)

# copy dependencies and overwrite if already exists
if os.path.exists("./tmp_dependencies/"):
    shutil.rmtree("./tmp_dependencies/")
shutil.copytree("./diagnosis/", "./tmp_dependencies/diagnosis/")
shutil.copytree("./segmentation/", "./tmp_dependencies/segmentation/")

a = Analysis(['./main.py'],
             pathex=['.'],
             binaries=[],
             datas=[],
             hiddenimports=hidden_imports,
             hookspath=["./hooks/"],  # the most important part
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)


'''
# one large exe-file with everything included
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          #Tree("./stuff/"),
          Tree("./tmp_dependencies/"),
          a.zipfiles,
          a.datas,
          [],
          name='NeuroRADS',
          debug=True,  # should be set to False, but needed to debug on MacOSX
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
'''

# separate exe-file from dlls and everything else
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='NeuroRADS',
          debug=True,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               Tree("./tmp_dependencies/"),
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='NeuroRADS')
