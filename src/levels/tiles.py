"""
瓦片模块
AI辅助生成: 实现关卡中的瓦片类

此模块包含各种类型的瓦片：地面、砖块、问号块、管道等。
瓦片是构成关卡的基本元素。
"""

import pygame
from enum import Enum, auto
from typing import Optional, TYPE_CHECKING, Tuple

from ..settings import TILE_SIZE
from ..core.resource_manager import ResourceManager
from ..core.event_system import EventSystem, GameEvent

if TYPE_CHECKING:
    from ..entities.player import Player


class TileType(Enum):
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
    EMPTY_BLOCK = 11


class Tile:
    """
    瓦片基类
    
    关卡中的基本构建块，具有碰撞属性和渲染功能。
    
    Attributes:
        x: X坐标（像素）
        y: Y坐标（像素）
        tile_type: 瓦片类型
        solid: 是否为实体（可碰撞）
        image: 瓦片图像
        rect: 碰撞矩形
    """
    
    def __init__(self, grid_x: int, grid_y: int, tile_type: TileType):
        """
        初始化瓦片
        
        Args:
            grid_x: 网格X坐标
            grid_y: 网格Y坐标
            tile_type: 瓦片类型
        """
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.x = grid_x * TILE_SIZE
        self.y = grid_y * TILE_SIZE
        self.tile_type = tile_type
        
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        
        # 碰撞属性
        self.solid = True
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # 图像
        self.image: Optional[pygame.Surface] = None
        
        # 加载图像
        self._load_image()
    
    def _load_image(self) -> None:
        """加载瓦片图像"""
        rm = ResourceManager()
        
        image_map = {
            TileType.GROUND: 'tiles/ground.png',
            TileType.BRICK: 'tiles/brick.png',
            TileType.EMPTY_BLOCK: 'tiles/empty_block.png',
            TileType.SPIKE: 'tiles/spike.png',
            TileType.PLATFORM: 'tiles/platform.png',
            TileType.FLAG: 'tiles/flag.png',
        }
        
        if self.tile_type in image_map:
            self.image = rm.load_image(image_map[self.tile_type])
    
    def update(self, dt: float) -> None:
        """更新瓦片状态（子类可重写）"""
        pass
    
    def render(self, screen: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)) -> None:
        """
        渲染瓦片
        
        Args:
            screen: 渲染目标
            camera_offset: 摄像机偏移
        """
        if self.image is None:
            return
        
        render_x = self.x - camera_offset[0]
        render_y = self.y - camera_offset[1]
        
        # 简单的视口剔除
        if render_x + self.width < 0 or render_x > screen.get_width():
            return
        if render_y + self.height < 0 or render_y > screen.get_height():
            return
        
        screen.blit(self.image, (render_x, render_y))
    
    def on_hit_from_below(self, player: 'Player') -> None:
        """被玩家从下方顶到时调用"""
        pass


class BrickTile(Tile):
    """
    砖块瓦片
    
    可以被大状态玩家打碎的砖块。
    """
    
    def __init__(self, grid_x: int, grid_y: int):
        super().__init__(grid_x, grid_y, TileType.BRICK)
        self.broken = False
    
    def on_hit_from_below(self, player: 'Player') -> None:
        """被顶时的行为"""
        from ..entities.player import PlayerState
        
        if player.state == PlayerState.BIG or player.state == PlayerState.INVINCIBLE:
            # 大状态可以打碎砖块
            self.break_brick()
        else:
            # 小状态只是震动效果（可选实现）
            pass
    
    def on_hit_from_above(self, player: 'Player') -> None:
        """被下砸时的行为"""
        # 下砸可以直接打碎砖块（无视玩家状态）
        if player.is_ground_pounding:
            self.break_brick()
    
    def break_brick(self) -> None:
        """打碎砖块"""
        if self.broken:
            return
        self.broken = True
        self.solid = False
        self.image = None
        EventSystem().emit(GameEvent.BRICK_BREAK, {
            'x': self.x, 'y': self.y
        })


class QuestionTile(Tile):
    """
    问号方块
    
    包含道具的特殊方块，被顶后会弹出道具并变成空方块。
    
    Attributes:
        contains: 方块内容 ('coin', 'mushroom', 'star')
        hit: 是否已被击中
    """
    
    def __init__(self, grid_x: int, grid_y: int, contains: str = 'coin'):
        super().__init__(grid_x, grid_y, TileType.QUESTION)
        
        self.contains = contains
        self.hit = False
        
        # 动画
        self.animation_frames = []
        self.animation_index = 0
        self.animation_timer = 0.0
        self.animation_speed = 4.0
        
        # 加载动画
        self._load_animation()
    
    def _load_image(self) -> None:
        """重写以跳过基类图像加载"""
        pass
    
    def _load_animation(self) -> None:
        """加载问号块动画"""
        rm = ResourceManager()
        tiles = rm.load_tile_sprites()
        self.animation_frames = tiles['question_block']
        self.empty_image = tiles['empty_block']
        
        if self.animation_frames:
            self.image = self.animation_frames[0]
    
    def update(self, dt: float) -> None:
        """更新动画"""
        if self.hit:
            return  # 被击中后停止动画
        
        if not self.animation_frames:
            return
        
        self.animation_timer += dt * self.animation_speed
        if self.animation_timer >= 1.0:
            self.animation_timer -= 1.0
            self.animation_index = (self.animation_index + 1) % len(self.animation_frames)
            self.image = self.animation_frames[self.animation_index]
    
    def on_hit_from_below(self, player: 'Player') -> None:
        """被顶时弹出道具"""
        if self.hit:
            return
        
        self.hit = True
        self.image = self.empty_image
        
        EventSystem().emit(GameEvent.BLOCK_HIT, {
            'x': self.x,
            'y': self.y,
            'contains': self.contains
        })
    
    def get_spawn_position(self) -> Tuple[float, float]:
        """获取道具生成位置"""
        return (self.x, self.y - TILE_SIZE)


class PipeTile(Tile):
    """
    管道瓦片
    
    装饰性瓦片，可作为障碍物。
    """
    
    def __init__(self, grid_x: int, grid_y: int, is_top: bool = True, is_left: bool = True):
        self.is_top = is_top
        self.is_left = is_left
        
        if is_top:
            tile_type = TileType.PIPE_TOP_LEFT if is_left else TileType.PIPE_TOP_RIGHT
        else:
            tile_type = TileType.PIPE_BODY_LEFT if is_left else TileType.PIPE_BODY_RIGHT
        
        super().__init__(grid_x, grid_y, tile_type)
    
    def _load_image(self) -> None:
        """加载管道图像"""
        rm = ResourceManager()
        pipe_full = rm.load_image('tiles/pipe.png')
        
        # 管道精灵是64x64，需要裁剪
        if self.is_top and self.is_left:
            self.image = pipe_full.subsurface((0, 0, 32, 32))
        elif self.is_top and not self.is_left:
            self.image = pipe_full.subsurface((32, 0, 32, 32))
        elif not self.is_top and self.is_left:
            self.image = pipe_full.subsurface((0, 32, 32, 32))
        else:
            self.image = pipe_full.subsurface((32, 32, 32, 32))


class SpikeTile(Tile):
    """
    尖刺瓦片
    
    困难模式的陷阱，接触即死。可以闪烁隐藏。
    
    Attributes:
        blinks: 是否会闪烁（困难模式）
        visible: 当前是否可见
    """
    
    def __init__(self, grid_x: int, grid_y: int, blinks: bool = False):
        super().__init__(grid_x, grid_y, TileType.SPIKE)
        
        self.blinks = blinks
        self.visible = True
        self.blink_timer = 0.0
        self.blink_interval = 1.0  # 闪烁间隔
        
        # 加载闪烁图像
        if blinks:
            rm = ResourceManager()
            self.blink_image = rm.load_image('tiles/spike_blink.png')
    
    def update(self, dt: float) -> None:
        """更新闪烁状态"""
        if not self.blinks:
            return
        
        self.blink_timer += dt
        if self.blink_timer >= self.blink_interval:
            self.blink_timer = 0
            self.visible = not self.visible
            self.solid = self.visible  # 不可见时也不碰撞
    
    def render(self, screen: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)) -> None:
        """渲染（考虑闪烁）"""
        if self.blinks and not self.visible:
            # 半透明渲染
            if hasattr(self, 'blink_image') and self.blink_image:
                render_x = self.x - camera_offset[0]
                render_y = self.y - camera_offset[1]
                screen.blit(self.blink_image, (render_x, render_y))
            return
        
        super().render(screen, camera_offset)


class MovingPlatform(Tile):
    """
    移动平台
    
    困难模式的移动平台，左右或上下移动。
    
    Attributes:
        move_range: 移动范围
        move_speed: 移动速度
        direction: 移动方向
        horizontal: 是否水平移动
    """
    
    def __init__(self, grid_x: int, grid_y: int, move_range: int = 3, 
                 horizontal: bool = True):
        super().__init__(grid_x, grid_y, TileType.PLATFORM)
        
        self.width = 96  # 平台更宽
        self.height = 16
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        self.start_x = self.x
        self.start_y = self.y
        self.move_range = move_range * TILE_SIZE
        self.move_speed = 1.0
        self.direction = 1
        self.horizontal = horizontal
    
    def update(self, dt: float) -> None:
        """更新平台位置"""
        if self.horizontal:
            self.x += self.move_speed * self.direction
            
            if self.x >= self.start_x + self.move_range:
                self.direction = -1
            elif self.x <= self.start_x:
                self.direction = 1
        else:
            self.y += self.move_speed * self.direction
            
            if self.y >= self.start_y + self.move_range:
                self.direction = -1
            elif self.y <= self.start_y:
                self.direction = 1
        
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
