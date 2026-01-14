"""
蘑菇道具模块
AI辅助生成: 实现变大蘑菇道具

蘑菇道具会从问号块弹出并移动，玩家吃到后会变大。
"""

from typing import TYPE_CHECKING, List
import pygame

from .item import Item
from ...settings import TILE_SIZE, GRAVITY, MAX_FALL_SPEED
from ...core.resource_manager import ResourceManager

if TYPE_CHECKING:
    from ..player import Player


class Mushroom(Item):
    """
    蘑菇道具类
    
    从问号块弹出后会向一个方向移动。
    玩家收集后会变成大状态。
    
    Attributes:
        move_speed: 移动速度
    """
    
    def __init__(self, x: float, y: float):
        """
        初始化蘑菇道具
        
        Args:
            x: X坐标
            y: Y坐标
        """
        super().__init__(x, y, TILE_SIZE, TILE_SIZE)
        
        self.score_value = 1000
        self.auto_collect = True
        self.moves = True  # 蘑菇会移动
        
        # 移动参数
        self.move_speed = 2.0
        self.facing_right = True  # 默认向右移动
        
        # 加载精灵
        self._load_sprites()
    
    def _load_sprites(self) -> None:
        """加载蘑菇精灵"""
        rm = ResourceManager()
        items = rm.load_item_sprites()
        
        self.set_image(items['mushroom'])
    
    def _update_movement(self, dt: float) -> None:
        """更新蘑菇移动"""
        # 应用重力
        self.velocity_y += GRAVITY
        if self.velocity_y > MAX_FALL_SPEED:
            self.velocity_y = MAX_FALL_SPEED
        
        # 水平移动
        direction = 1 if self.facing_right else -1
        self.velocity_x = self.move_speed * direction
        
        # 更新位置
        self.x += self.velocity_x
        self.y += self.velocity_y
    
    def apply_collision(self, tiles: List[pygame.Rect]) -> None:
        """重写碰撞检测以处理转向"""
        if self.spawning:
            return
        
        self.on_ground = False
        self.update_rect()
        
        for tile in tiles:
            if not self.rect.colliderect(tile):
                continue
            
            overlap_left = self.rect.right - tile.left
            overlap_right = tile.right - self.rect.left
            overlap_top = self.rect.bottom - tile.top
            overlap_bottom = tile.bottom - self.rect.top
            
            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
            
            if min_overlap == overlap_top and self.velocity_y >= 0:
                self.y = tile.top - self.height
                self.velocity_y = 0
                self.on_ground = True
            elif min_overlap == overlap_left and self.facing_right:
                self.x = tile.left - self.width
                self.facing_right = False  # 转向
            elif min_overlap == overlap_right and not self.facing_right:
                self.x = tile.right
                self.facing_right = True  # 转向
            
            self.update_rect()
    
    def _apply_effect(self, player: 'Player') -> None:
        """应用变大效果"""
        player.power_up()


class Star(Item):
    """
    星星道具类
    
    收集后获得短暂无敌效果。
    星星会跳跃移动，比蘑菇更难捕捉。
    
    Attributes:
        bounce_power: 弹跳力度
    """
    
    def __init__(self, x: float, y: float):
        """
        初始化星星道具
        
        Args:
            x: X坐标
            y: Y坐标
        """
        super().__init__(x, y, 28, 28)
        
        self.score_value = 1000
        self.auto_collect = True
        self.moves = True
        
        # 弹跳参数
        self.bounce_power = -10
        self.move_speed = 3.0
        self.facing_right = True
        
        # 动画速度（闪烁）
        self.animation_speed = 10.0
        
        # 加载精灵
        self._load_sprites()
        
        # 开始闪烁动画
        self.play_animation('blink')
    
    def _load_sprites(self) -> None:
        """加载星星精灵"""
        rm = ResourceManager()
        items = rm.load_item_sprites()
        
        self.add_animation('blink', items['star'])
    
    def _update_movement(self, dt: float) -> None:
        """更新星星移动（跳跃）"""
        # 应用重力
        self.velocity_y += GRAVITY * 0.8  # 稍微降低重力使弹跳更高
        if self.velocity_y > MAX_FALL_SPEED:
            self.velocity_y = MAX_FALL_SPEED
        
        # 水平移动
        direction = 1 if self.facing_right else -1
        self.velocity_x = self.move_speed * direction
        
        # 更新位置
        self.x += self.velocity_x
        self.y += self.velocity_y
    
    def apply_collision(self, tiles: List[pygame.Rect]) -> None:
        """重写碰撞检测以实现弹跳"""
        if self.spawning:
            return
        
        self.update_rect()
        
        for tile in tiles:
            if not self.rect.colliderect(tile):
                continue
            
            overlap_left = self.rect.right - tile.left
            overlap_right = tile.right - self.rect.left
            overlap_top = self.rect.bottom - tile.top
            overlap_bottom = tile.bottom - self.rect.top
            
            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
            
            if min_overlap == overlap_top and self.velocity_y >= 0:
                self.y = tile.top - self.height
                self.velocity_y = self.bounce_power  # 弹跳
            elif min_overlap == overlap_bottom and self.velocity_y < 0:
                self.y = tile.bottom
                self.velocity_y = 0
            elif min_overlap == overlap_left and self.facing_right:
                self.x = tile.left - self.width
                self.facing_right = False
            elif min_overlap == overlap_right and not self.facing_right:
                self.x = tile.right
                self.facing_right = True
            
            self.update_rect()
    
    def _apply_effect(self, player: 'Player') -> None:
        """应用无敌效果"""
        player.become_invincible()
