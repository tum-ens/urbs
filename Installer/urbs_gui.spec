# -*- mode: python -*-

block_cipher = None


a = Analysis(['..\\gui\\gui.py'],
             pathex=['..', '..\\gui'],
             binaries=[],
             datas=[],
             hiddenimports=['pyomo.common.plugins',
                            'pyomo.opt.plugins',
                            'pyomo.core.plugins',
                            'pyomo.dataportal.plugins',
                            'pyomo.duality.plugins',
                            'pyomo.checker.plugins',
                            'pyomo.repn.plugins',
                            'pyomo.pysp.plugins',
                            'pyomo.neos.plugins',
                            'pyomo.solvers.plugins',
                            'pyomo.gdp.plugins',
                            'pyomo.mpec.plugins',
                            'pyomo.dae.plugins',
                            'pyomo.bilevel.plugins',
                            'pyomo.scripting.plugins',
                            'pyomo.network.plugins',
                            'pandas._libs.skiplist'
             ],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='urbs_gui',
          debug=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name='urbs_gui')
