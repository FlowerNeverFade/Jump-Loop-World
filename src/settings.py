"""
游戏配置常量模块
AI辅助生成: 包含所有游戏配置参数，便于统一管理和修改

此模块定义了游戏的核心配置参数，包括：
- 屏幕尺寸和帧率
- 物理参数（重力、跳跃力等）
- 颜色定义
- 难度配置
- 资源路径
"""

import os
import sys

# ==================== 屏幕设置 ====================
SCREEN_WIDTH = 800          # 屏幕宽度（像素）
SCREEN_HEIGHT = 480         # 屏幕高度（像素）- 调整为更适合平台游戏的比例
FPS = 60                    # 帧率
TITLE = "Jump Loop World"  # 游戏标题

# ==================== 瓦片设置 ====================
TILE_SIZE = 32              # 瓦片大小（像素）
PLAYER_WIDTH = 32           # 玩家宽度
PLAYER_HEIGHT = 48          # 玩家高度

# ==================== 物理参数 ====================
GRAVITY = 0.8               # 重力加速度
MAX_FALL_SPEED = 15         # 最大下落速度
JUMP_POWER = -14            # 跳跃力（负值向上）
PLAYER_SPEED = 5            # 玩家最大移动速度
PLAYER_ACCELERATION = 0.5   # 玩家加速度（惯性系统）
FRICTION = 0.85             # 地面摩擦系数
AIR_FRICTION = 0.92         # 空中摩擦系数（空中控制较弱）

# ==================== 难度配置 ====================
class DifficultySettings:
    """
    难度配置类
    AI辅助生成: 使用策略模式封装不同难度的参数配置
    """
    
    # 简单模式配置
    EASY = {
        'name': '简单模式',
        'enemy_speed_multiplier': 1.0,      # 敌人速度倍率
        'enemy_count_multiplier': 1.0,      # 敌人数量倍率
        'platform_static': True,             # 平台是否静态
        'platform_blink': False,             # 平台是否闪烁
        'has_traps': False,                  # 是否有陷阱
        'item_spawn_rate': 1.0,              # 道具生成率
        'time_limit': 300,                   # 时间限制（秒）
        'player_lives': 5,                   # 玩家生命数
    }
    
    # 困难模式配置
    HARD = {
        'name': '困难模式',
        'enemy_speed_multiplier': 2.0,      # 敌人速度2倍
        'enemy_count_multiplier': 1.5,      # 敌人数量1.5倍
        'platform_static': False,            # 平台会移动
        'platform_blink': True,              # 平台会闪烁
        'has_traps': True,                   # 有隐藏陷阱
        'item_spawn_rate': 0.5,              # 道具减少50%
        'time_limit': 180,                   # 时间更紧张
        'player_lives': 3,                   # 生命更少
    }
    
    # 变态模式配置
    HARDCORE = {
        'name': '变态模式',
        'enemy_speed_multiplier': 2.5,      # 敌人速度2.5倍
        'enemy_count_multiplier': 2.0,      # 敌人数量2倍
        'platform_static': False,            # 平台会移动
        'platform_blink': True,              # 平台会闪烁
        'has_traps': True,                   # 有隐藏陷阱
        'item_spawn_rate': 0.3,              # 道具减少70%
        'time_limit': 120,                   # 时间更紧张
        'player_lives': 3,                   # 生命更少
    }


# ==================== 颜色定义 ====================
class Colors:
    """
    游戏颜色常量
    AI辅助生成: 统一管理游戏中使用的颜色
    """
    # 基础颜色
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (229, 37, 33)
    GREEN = (58, 166, 85)
    BLUE = (0, 57, 166)
    YELLOW = (255, 215, 0)
    
    # 天空渐变色
    SKY_TOP = (135, 206, 235)
    SKY_BOTTOM = (176, 224, 230)
    
    # UI颜色
    UI_BACKGROUND = (40, 40, 60)
    UI_TEXT = (255, 255, 255)
    UI_HIGHLIGHT = (255, 200, 100)
    UI_BUTTON = (80, 80, 120)
    UI_BUTTON_HOVER = (100, 100, 150)
    
    # 玩家颜色
    PLAYER_RED_HAT = (229, 37, 33)
    PLAYER_GREEN_HAT = (58, 166, 85)
    PLAYER_SKIN = (255, 204, 153)
    PLAYER_OUTFIT = (0, 57, 166)
    PLAYER_SHOES = (107, 62, 38)
    
    # 敌人颜色
    MUSHLING_CAP = (160, 82, 45)
    MUSHLING_BODY = (255, 222, 173)
    SHELLBACK_SHELL = (34, 139, 34)
    SHELLBACK_BODY = (255, 255, 153)
    
    # 方块颜色
    GROUND_BROWN = (139, 69, 19)
    BRICK_TAN = (205, 133, 63)
    QUESTION_GOLD = (255, 215, 0)
    PIPE_GREEN = (34, 139, 34)


# ==================== 资源路径 ====================
APP_NAME = "JumpLoopWorld"

def get_base_dir() -> str:
    """获取资源基准目录（支持 PyInstaller 打包）。"""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_user_data_dir(app_name: str = APP_NAME) -> str:
    """获取用户数据目录（存档/配置使用）。"""
    base_dir = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or os.path.expanduser("~")
    return os.path.join(base_dir, app_name)

# 获取项目根目录
BASE_DIR = get_base_dir()
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
SPRITES_DIR = os.path.join(ASSETS_DIR, 'sprites')
LEVELS_DIR = os.path.join(ASSETS_DIR, 'levels')

# 音频目录
# 说明：首次运行时若缺少音频文件，会由 AudioManager 自动生成简单的 wav 资源
AUDIO_DIR = os.path.join(ASSETS_DIR, 'audio')
SFX_DIR = os.path.join(AUDIO_DIR, 'sfx')
MUSIC_DIR = os.path.join(AUDIO_DIR, 'music')

# 默认音量（0.0 - 1.0）
DEFAULT_MUSIC_VOLUME = 0.35
DEFAULT_SFX_VOLUME = 0.65

# 精灵子目录
PLAYER_SPRITES_DIR = os.path.join(SPRITES_DIR, 'player')
ENEMY_SPRITES_DIR = os.path.join(SPRITES_DIR, 'enemies')
TILE_SPRITES_DIR = os.path.join(SPRITES_DIR, 'tiles')
ITEM_SPRITES_DIR = os.path.join(SPRITES_DIR, 'items')


# ==================== 游戏状态 ====================
class GameStates:
    """游戏状态枚举"""
    MENU = 'menu'
    PLAYING = 'playing'
    PAUSED = 'paused'
    GAME_OVER = 'game_over'
    VICTORY = 'victory'


# ==================== 实体类型 ====================
class EntityTypes:
    """实体类型枚举"""
    PLAYER = 'player'
    GOOMBA = 'goomba'
    KOOPA = 'koopa'
    FLAPPER = 'flapper'
    COIN = 'coin'
    MUSHROOM = 'mushroom'
    STAR = 'star'


# ==================== 瓦片类型 ====================
class TileTypes:
    """瓦片类型枚举"""
    EMPTY = 0
    GROUND = 1
    BRICK = 2
    QUESTION = 3
    PIPE_TOP_LEFT = 4
    PIPE_TOP_RIGHT = 5
    PIPE_BODY_LEFT = 6
    PIPE_BODY_RIGHT = 7
    SPIKE = 8
    PLATFORM = 9
    FLAG = 10
