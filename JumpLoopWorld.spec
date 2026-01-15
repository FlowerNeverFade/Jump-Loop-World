# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Jump Loop World
# 用于将游戏打包成单个可执行文件

import os

block_cipher = None

# 获取当前目录
spec_dir = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    ['main.py'],
    pathex=[spec_dir],
    binaries=[],
    datas=[
        ('assets', 'assets'),      # 包含所有游戏资源（精灵、音频）
        ('config', 'config'),      # 包含配置文件
    ],
    hiddenimports=[
        # pygame 相关
        'pygame',
        'pygame.mixer',
        'pygame.font',
        'pygame.image',
        'pygame.transform',
        'pygame.draw',
        'pygame.display',
        'pygame.event',
        'pygame.time',
        'pygame.key',
        'pygame.mouse',
        'pygame.rect',
        'pygame.surface',
        'pygame.sprite',
        'pygame.math',
        # 项目模块
        'src',
        'src.game',
        'src.settings',
        'src.core',
        'src.core.audio_manager',
        'src.core.event_system',
        'src.core.key_bindings',
        'src.core.player_config',
        'src.core.resource_manager',
        'src.core.roguelike_data',
        'src.core.save_manager',
        'src.core.state_machine',
        'src.entities',
        'src.entities.entity',
        'src.entities.player',
        'src.entities.enemies',
        'src.entities.enemies.enemy',
        'src.entities.enemies.flapper',
        'src.entities.enemies.ghost',
        'src.entities.enemies.giant',
        'src.entities.enemies.goomba',
        'src.entities.enemies.jumper',
        'src.entities.enemies.koopa',
        'src.entities.enemies.shooter',
        'src.entities.enemies.spikeball',
        'src.entities.items',
        'src.entities.items.item',
        'src.entities.items.coin',
        'src.entities.items.mushroom',
        'src.entities.obstacles',
        'src.entities.obstacles.laser',
        'src.entities.obstacles.saw',
        'src.entities.obstacles.spring',
        'src.factories',
        'src.factories.entity_factory',
        'src.factories.level_factory',
        'src.graphics',
        'src.graphics.sprite_generator',
        'src.levels',
        'src.levels.camera',
        'src.levels.hardcore_level',
        'src.levels.level',
        'src.levels.tiles',
        'src.states',
        'src.states.game_over_state',
        'src.states.game_state',
        'src.states.menu_state',
        'src.states.pause_state',
        'src.states.play_state',
        'src.states.save_select_state',
        'src.states.settings_state',
        'src.states.shop_state',
        'src.ui',
        'src.ui.button',
        'src.ui.hud',
        'src.ui.menu',
        'src.ui.slider',
        'src.ui.ui_manager',
        # 标准库
        'json',
        'random',
        'math',
        'datetime',
        'typing',
        'os',
        'sys',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'unittest',
        'test',
        'tests',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='JumpLoopWorld',
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
    icon=None,  # 如果有图标文件，可以在这里指定，如：icon='assets/icon.ico'
)
