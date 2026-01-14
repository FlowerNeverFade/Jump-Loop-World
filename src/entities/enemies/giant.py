"""
巨型怪模块
AI辅助生成: 实现需要多次踩踏才能消灭的敌人

巨型怪体型是普通敌人的两倍，需要踩3次才能消灭。
"""

import pygame
from typing import TYPE_CHECKING

from .enemy import Enemy
from ...settings import TILE_SIZE, GRAVITY, MAX_FALL_SPEED
from ...core.resource_manager import ResourceManager
from ...core.event_system import EventSystem, GameEvent

if TYPE_CHECKING:
    from ..player import Player


class Giant(Enemy):
    """
    巨型怪类
    
    体型巨大的敌人，需要踩3次才能消灭。
    每次被踩会变色并短暂加速。
    """
    
    def __init__(self, x: float, y: float):
        # 巨型怪是2x2格子大小
        super().__init__(x, y, TILE_SIZE * 2, TILE_SIZE * 2)
        
        self.speed = 0.6  # 移动较慢
        self.score_value = 500
        
        # 生命值
        self.health = 3
        self.max_health = 3
        
        # 受伤后的加速
        self.rage_timer = 0.0
        self.rage_duration = 2.0
        self.rage_speed_multiplier = 2.0
        
        self._load_sprites()
    
    def _load_sprites(self) -> None:
        """加载巨型怪精灵"""
        rm = ResourceManager()
        
        normal_img = rm.load_image('enemies/giant_normal.png')
        hurt1_img = rm.load_image('enemies/giant_hurt1.png')
        hurt2_img = rm.load_image('enemies/giant_hurt2.png')
        
        if normal_img:
            self.add_animation('normal', [normal_img])
        if hurt1_img:
            self.add_animation('hurt1', [hurt1_img])
        if hurt2_img:
            self.add_animation('hurt2', [hurt2_img])
        
        self.play_animation('normal')
    
    def _update_behavior(self, dt: float) -> None:
        """更新巨型怪行为"""
        # 更新狂暴状态
        if self.rage_timer > 0:
            self.rage_timer -= dt
            if self.rage_timer <= 0:
                self.speed_multiplier = 1.0
    
    def on_stomp(self, player: 'Player') -> bool:
        """被踩踏时减少生命值"""
        if self.is_dead:
            return False
        
        self.health -= 1
        
        if self.health <= 0:
            # 彻底死亡
            self.is_dead = True
            self._on_stomped()
            EventSystem().emit(GameEvent.ENEMY_STOMP, {'score': self.score_value})
            return True
        else:
            # 受伤但未死
            self._on_hurt()
            # 给玩家部分分数
            EventSystem().emit(GameEvent.ENEMY_STOMP, {'score': self.score_value // 3})
            return True
    
    def _on_hurt(self) -> None:
        """受伤但未死时的行为"""
        # 切换受伤贴图
        if self.health == 2:
            self.play_animation('hurt1')
        elif self.health == 1:
            self.play_animation('hurt2')
        
        # 进入狂暴状态
        self.rage_timer = self.rage_duration
        self.speed_multiplier = self.rage_speed_multiplier
        
        # 反向移动
        self.direction *= -1
    
    def _on_stomped(self) -> None:
        """彻底死亡时的行为"""
        self.velocity_x = 0
        self.velocity_y = 0
