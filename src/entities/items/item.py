"""
道具基类模块
AI辅助生成: 定义所有道具的基类

此模块提供Item抽象基类，所有道具类型都继承自此类。
道具包括金币、蘑菇、星星等。
"""

import pygame
from abc import abstractmethod
from typing import TYPE_CHECKING, List

from ..entity import AnimatedEntity
from ...settings import GRAVITY, MAX_FALL_SPEED, TILE_SIZE
from ...core.event_system import EventSystem, GameEvent

if TYPE_CHECKING:
    from ..player import Player


class Item(AnimatedEntity):
    """
    道具抽象基类
    
    定义道具的通用行为和属性。
    
    Attributes:
        score_value: 收集获得的分数
        collected: 是否已被收集
        auto_collect: 是否自动收集（如金币）
        moves: 道具是否会移动
    """
    
    def __init__(self, x: float, y: float, width: int = 24, height: int = 24):
        """
        初始化道具
        
        Args:
            x: 初始X坐标
            y: 初始Y坐标
            width: 宽度
            height: 高度
        """
        super().__init__(x, y, width, height)
        
        self.score_value = 0
        self.collected = False
        self.auto_collect = True  # 默认接触即收集
        self.moves = False  # 默认不移动
        
        # 从方块弹出时的动画
        self.spawning = False
        self.spawn_start_y = y
        self.spawn_target_y = y - TILE_SIZE
        self.spawn_timer = 0.0
        self.spawn_duration = 0.3
    
    def spawn_from_block(self, block_y: float) -> None:
        """
        从方块中弹出
        
        AI辅助生成: 实现道具从问号块弹出的动画效果
        
        Args:
            block_y: 方块的Y坐标
        """
        self.spawning = True
        self.spawn_start_y = block_y
        self.spawn_target_y = block_y - self.height
        self.y = block_y
        self.spawn_timer = 0.0
    
    def update(self, dt: float) -> None:
        """更新道具状态"""
        if not self.active or self.collected:
            return
        
        # 弹出动画
        if self.spawning:
            self.spawn_timer += dt
            progress = min(self.spawn_timer / self.spawn_duration, 1.0)
            # 使用缓动函数
            eased = 1 - (1 - progress) ** 2
            self.y = self.spawn_start_y + (self.spawn_target_y - self.spawn_start_y) * eased
            
            if progress >= 1.0:
                self.spawning = False
                self.y = self.spawn_target_y
            
            self.update_rect()
            return
        
        # 移动逻辑（某些道具如蘑菇会移动）
        if self.moves:
            self._update_movement(dt)
        
        # 更新动画
        self.update_animation(dt)
        self.update_rect()
    
    def _update_movement(self, dt: float) -> None:
        """更新移动逻辑（子类可重写）"""
        pass
    
    def apply_collision(self, tiles: List[pygame.Rect]) -> None:
        """应用与瓦片的碰撞"""
        if not self.moves or self.spawning:
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
            elif min_overlap == overlap_left:
                self.x = tile.left - self.width
                self.facing_right = False
            elif min_overlap == overlap_right:
                self.x = tile.right
                self.facing_right = True
            
            self.update_rect()
    
    def on_collect(self, player: 'Player') -> None:
        """
        被收集时调用
        
        Args:
            player: 收集的玩家
        """
        if self.collected:
            return
        
        self.collected = True
        self.active = False
        self._apply_effect(player)
        
        EventSystem().emit(GameEvent.ITEM_COLLECT, {
            'item_type': self.__class__.__name__,
            'score': self.score_value
        })
    
    @abstractmethod
    def _apply_effect(self, player: 'Player') -> None:
        """
        应用道具效果（子类实现）
        
        Args:
            player: 收集的玩家
        """
        pass
