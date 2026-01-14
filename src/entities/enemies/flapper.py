"""
飞行怪模块
AI辅助生成: 实现困难模式的飞行敌人

飞行怪是困难模式专属的敌人，在空中飞行，需要更精确的跳跃才能踩到。
"""

import pygame
import math
from typing import TYPE_CHECKING

from .enemy import Enemy
from ...settings import TILE_SIZE
from ...core.resource_manager import ResourceManager

if TYPE_CHECKING:
    from ..player import Player


class Flapper(Enemy):
    """
    飞行怪类
    
    困难模式专属敌人，在空中上下飞行。
    增加游戏难度，需要玩家精确跳跃。
    
    Attributes:
        fly_amplitude: 飞行振幅（上下移动的范围）
        fly_speed: 飞行速度（上下移动的频率）
        fly_timer: 飞行动画计时器
        base_y: 基准Y坐标
    """
    
    def __init__(self, x: float, y: float):
        """
        初始化飞行怪
        
        Args:
            x: 初始X坐标
            y: 初始Y坐标
        """
        super().__init__(x, y, TILE_SIZE, TILE_SIZE)
        
        self.speed = 1.5  # 水平移动速度
        self.score_value = 200  # 比普通敌人分数高
        
        # 飞行参数
        self.fly_amplitude = 50.0  # 上下飞行幅度
        self.fly_speed = 2.0       # 飞行频率
        self.fly_timer = 0.0
        self.base_y = y
        
        # 动画速度（翅膀扇动更快）
        self.animation_speed = 15.0
        
        # 加载精灵
        self._load_sprites()
        
        # 开始飞行动画
        self.play_animation('fly')
    
    def _load_sprites(self) -> None:
        """加载飞行怪精灵"""
        rm = ResourceManager()
        sprites = rm.load_enemy_sprites('flapper')
        
        self.add_animation('fly', sprites['fly'])
    
    def _update_behavior(self, dt: float) -> None:
        """更新飞行怪特有行为"""
        # 更新飞行计时器
        self.fly_timer += dt * self.fly_speed
        
        # 正弦波上下运动
        self.y = self.base_y + math.sin(self.fly_timer * math.pi) * self.fly_amplitude
    
    def update(self, dt: float) -> None:
        """
        重写更新方法
        
        飞行怪不受重力影响
        """
        if not self.active:
            return
        
        if self.is_dead:
            # 死亡时下落
            self.velocity_y += 0.5  # 轻微重力
            self.y += self.velocity_y
            self.death_timer += dt
            if self.death_timer >= self.death_duration or self.y > 1000:
                self.active = False
            return
        
        # 水平移动
        self.velocity_x = self.speed * self.direction * self.speed_multiplier
        self.x += self.velocity_x
        
        # 更新朝向
        self.facing_right = self.direction > 0
        
        # 更新飞行行为
        self._update_behavior(dt)
        
        # 更新碰撞矩形
        self.update_rect()
        
        # 更新动画
        self.update_animation(dt)
    
    def apply_collision(self, tiles: list) -> None:
        """
        重写碰撞检测
        
        飞行怪只检测水平方向的碰撞（墙壁转向）
        """
        if self.is_dead:
            return
        
        self.update_rect()
        
        for tile in tiles:
            if not self.rect.colliderect(tile):
                continue
            
            # 只处理水平碰撞
            overlap_left = self.rect.right - tile.left
            overlap_right = tile.right - self.rect.left
            
            if overlap_left < overlap_right:
                # 右边撞墙
                self.x = tile.left - self.width
                self.direction = -1
            else:
                # 左边撞墙
                self.x = tile.right
                self.direction = 1
            
            self.update_rect()
    
    def _on_stomped(self) -> None:
        """被踩踏时下落死亡"""
        self.velocity_y = -3  # 小幅弹起
        # 播放死亡动画或变暗效果可以在这里添加
    
    def on_player_collision(self, player: 'Player') -> bool:
        """重写玩家碰撞逻辑"""
        if self.is_dead:
            return False
        
        # 飞行怪可以从更大范围被踩
        player_bottom = player.y + player.height
        enemy_top = self.y
        
        # 如果玩家在下落且底部在敌人上半部分
        if player.velocity_y > 0 and player_bottom < enemy_top + self.height * 0.5:
            if self.on_stomp(player):
                player.stomp_enemy()
                return False
        
        return True
