"""
滚动尖球模块
AI辅助生成: 实现沿平台滚动的危险敌人

滚动尖球不能被踩，接触即伤害玩家。
"""

import pygame
from typing import TYPE_CHECKING, List

from .enemy import Enemy
from ...settings import TILE_SIZE
from ...core.resource_manager import ResourceManager

if TYPE_CHECKING:
    from ..player import Player


class SpikeBall(Enemy):
    """
    滚动尖球类
    
    沿平台滚动的危险敌人，不能被踩死。
    接触任何部位都会伤害玩家。
    """
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, TILE_SIZE, TILE_SIZE)
        
        self.speed = 3.0  # 滚动较快
        self.score_value = 0  # 不能被杀死，没有分数
        self.can_be_stomped = False  # 不能被踩
        
        # 滚动动画
        self.roll_frame = 0
        self.roll_timer = 0.0
        self.roll_speed = 0.05  # 动画速度
        
        self._load_sprites()
    
    def _load_sprites(self) -> None:
        """加载滚动尖球精灵"""
        rm = ResourceManager()
        
        frames = []
        for i in range(1, 5):
            img = rm.load_image(f'enemies/spikeball_{i}.png')
            if img:
                frames.append(img)
        
        if frames:
            self.add_animation('roll', frames)
            self.play_animation('roll')
    
    def _update_behavior(self, dt: float) -> None:
        """更新滚动行为"""
        # 更新滚动动画速度基于移动速度
        self.animation_speed = abs(self.velocity_x) * 3
    
    def on_player_collision(self, player: 'Player') -> bool:
        """尖球碰撞总是伤害玩家"""
        if self.is_dead:
            return False
        return True  # 总是伤害玩家
    
    def _on_stomped(self) -> None:
        """不能被踩"""
        pass
