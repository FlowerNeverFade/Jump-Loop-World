"""
跳跃怪模块
AI辅助生成: 实现会跳跃的敌人

跳跃怪会周期性跳跃，跳跃高度较高，难以预测。
"""

import pygame
from typing import TYPE_CHECKING

from .enemy import Enemy
from ...settings import TILE_SIZE, GRAVITY, MAX_FALL_SPEED
from ...core.resource_manager import ResourceManager

if TYPE_CHECKING:
    from ..player import Player


class Jumper(Enemy):
    """
    跳跃怪类
    
    会周期性跳跃的敌人，跳跃高度高，移动速度快。
    """
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, TILE_SIZE, TILE_SIZE)
        
        self.speed = 1.5
        self.score_value = 200
        
        # 跳跃相关
        self.jump_timer = 0.0
        self.jump_interval = 1.5  # 跳跃间隔
        self.jump_power = -15  # 跳跃力度
        self.is_jumping = False
        
        # 动画
        self.animation_speed = 8.0
        self._load_sprites()
    
    def _load_sprites(self) -> None:
        """加载跳跃怪精灵"""
        rm = ResourceManager()
        
        idle_img = rm.load_image('enemies/jumper_idle.png')
        jump_img = rm.load_image('enemies/jumper_jump.png')
        
        if idle_img:
            self.add_animation('idle', [idle_img])
        if jump_img:
            self.add_animation('jump', [jump_img])
        
        self.play_animation('idle')
    
    def _update_behavior(self, dt: float) -> None:
        """更新跳跃行为"""
        self.jump_timer += dt
        
        if self.on_ground and self.jump_timer >= self.jump_interval:
            # 跳跃
            self.velocity_y = self.jump_power
            self.is_jumping = True
            self.jump_timer = 0.0
            self.play_animation('jump')
        
        if self.on_ground and self.is_jumping:
            self.is_jumping = False
            self.play_animation('idle')
    
    def _on_stomped(self) -> None:
        """被踩踏时的行为"""
        self.velocity_x = 0
        self.velocity_y = 0
