"""
蘑菇怪模块
AI辅助生成: 实现蘑菇小怪敌人

蘑菇怪是最基础的敌人类型，简单地左右巡逻，可被踩扁。
"""

import pygame
from typing import TYPE_CHECKING

from .enemy import Enemy
from ...settings import TILE_SIZE
from ...core.resource_manager import ResourceManager

if TYPE_CHECKING:
    from ..player import Player


class Goomba(Enemy):
    """
    蘑菇小怪类 (Mushling)
    
    游戏中最基础的敌人，简单地左右巡逻。
    被踩踏后会变成扁平状态然后消失。
    
    Attributes:
        squash_timer: 被踩扁后的计时器
    """
    
    def __init__(self, x: float, y: float):
        """
        初始化蘑菇怪
        
        Args:
            x: 初始X坐标
            y: 初始Y坐标
        """
        super().__init__(x, y, TILE_SIZE, TILE_SIZE)
        
        self.speed = 1.0
        self.score_value = 100
        
        # 被踩扁状态
        self.squash_timer = 0.0
        self.squash_duration = 0.3
        self.is_squashed = False
        
        # 动画速度 - 敌人动画稍慢
        self.animation_speed = 4.0
        
        # 加载精灵
        self._load_sprites()
        
        # 开始行走动画
        self.play_animation('walk')
    
    def _load_sprites(self) -> None:
        """加载蘑菇怪精灵"""
        rm = ResourceManager()
        sprites = rm.load_enemy_sprites('mushling')
        
        self.add_animation('walk', sprites['walk'])
        self.squashed_image = sprites['squashed']
    
    def _update_behavior(self, dt: float) -> None:
        """
        更新蘑菇怪特有行为
        
        蘑菇怪的行为很简单，就是来回巡逻
        """
        pass  # 基础巡逻行为在基类中处理
    
    def _on_stomped(self) -> None:
        """被踩踏时变成扁平状态"""
        self.is_squashed = True
        self.velocity_x = 0
        self.velocity_y = 0
        # 设置扁平图像
        self.set_image(self.squashed_image)
    
    def _update_death(self, dt: float) -> None:
        """更新死亡状态（显示扁平图像）"""
        if self.is_squashed:
            self.squash_timer += dt
            if self.squash_timer >= self.squash_duration:
                self.active = False
        else:
            super()._update_death(dt)
    
    def render(self, screen: pygame.Surface, camera_offset: tuple = (0, 0)) -> None:
        """渲染蘑菇怪"""
        if not self.active:
            return
        
        if self.is_squashed:
            # 渲染扁平图像
            if self.squashed_image:
                render_x = int(self.x - camera_offset[0])
                render_y = int(self.y + self.height - 12 - camera_offset[1])  # 调整Y位置
                img = self.squashed_image if self.facing_right else pygame.transform.flip(self.squashed_image, True, False)
                screen.blit(img, (render_x, render_y))
        else:
            super().render(screen, camera_offset)
