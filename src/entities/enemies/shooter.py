"""
发射怪模块
AI辅助生成: 实现会发射子弹的敌人

发射怪是固定的炮塔类敌人，会周期性向玩家发射子弹。
"""

import pygame
import math
from typing import TYPE_CHECKING, List, Optional

from .enemy import Enemy
from ...settings import TILE_SIZE, GRAVITY
from ...core.resource_manager import ResourceManager

if TYPE_CHECKING:
    from ..player import Player


class Bullet:
    """子弹类"""
    
    def __init__(self, x: float, y: float, direction: int):
        self.x = x
        self.y = y
        self.speed = 5.0
        self.direction = direction
        self.active = True
        self.width = 12
        self.height = 12
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # 加载图片
        rm = ResourceManager()
        self.image = rm.load_image('enemies/bullet.png')
    
    def update(self, dt: float) -> None:
        """更新子弹位置"""
        self.x += self.speed * self.direction
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
    
    def check_collision(self, tiles: List[pygame.Rect]) -> bool:
        """检查是否碰到墙"""
        for tile in tiles:
            if self.rect.colliderect(tile):
                return True
        return False
    
    def render(self, screen: pygame.Surface, camera_offset: tuple) -> None:
        """渲染子弹"""
        if self.image:
            render_x = int(self.x - camera_offset[0])
            render_y = int(self.y - camera_offset[1])
            screen.blit(self.image, (render_x, render_y))


class Shooter(Enemy):
    """
    发射怪类
    
    固定位置的炮塔敌人，会周期性发射子弹。
    不能被踩死，只能用星星无敌状态击杀。
    """
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, TILE_SIZE, TILE_SIZE)
        
        self.speed = 0  # 不移动
        self.score_value = 300
        self.can_be_stomped = False  # 不能被踩
        
        # 发射相关
        self.shoot_timer = 0.0
        self.shoot_interval = 2.0
        self.shoot_direction = -1  # 默认向左发射
        self.is_shooting = False
        self.shoot_animation_timer = 0.0
        
        # 子弹列表
        self.bullets: List[Bullet] = []
        
        # 目标玩家引用
        self.target_player: Optional['Player'] = None
        
        self._load_sprites()
    
    def _load_sprites(self) -> None:
        """加载发射怪精灵"""
        rm = ResourceManager()
        
        idle_img = rm.load_image('enemies/shooter_idle.png')
        shoot_img = rm.load_image('enemies/shooter_shoot.png')
        
        if idle_img:
            self.add_animation('idle', [idle_img])
        if shoot_img:
            self.add_animation('shoot', [shoot_img])
        
        self.play_animation('idle')
    
    def set_target(self, player: 'Player') -> None:
        """设置目标玩家"""
        self.target_player = player
    
    def _update_behavior(self, dt: float) -> None:
        """更新发射行为"""
        # 更新朝向（面向玩家）
        if self.target_player:
            if self.target_player.x < self.x:
                self.shoot_direction = -1
                self.facing_right = False
            else:
                self.shoot_direction = 1
                self.facing_right = True
        
        # 发射计时
        self.shoot_timer += dt
        
        if self.shoot_timer >= self.shoot_interval:
            self._shoot()
            self.shoot_timer = 0.0
        
        # 发射动画
        if self.is_shooting:
            self.shoot_animation_timer += dt
            if self.shoot_animation_timer >= 0.2:
                self.is_shooting = False
                self.shoot_animation_timer = 0.0
                self.play_animation('idle')
        
        # 更新子弹
        for bullet in self.bullets[:]:
            bullet.update(dt)
            # 超出范围移除
            if abs(bullet.x - self.x) > 400:
                self.bullets.remove(bullet)
    
    def _shoot(self) -> None:
        """发射子弹"""
        bullet_x = self.x + (self.width if self.shoot_direction > 0 else -12)
        bullet_y = self.y + self.height // 2 - 6
        
        bullet = Bullet(bullet_x, bullet_y, self.shoot_direction)
        self.bullets.append(bullet)
        
        self.is_shooting = True
        self.play_animation('shoot')
    
    def update_bullets(self, tiles: List[pygame.Rect]) -> None:
        """更新子弹（检查墙壁碰撞）"""
        for bullet in self.bullets[:]:
            if bullet.check_collision(tiles):
                self.bullets.remove(bullet)
    
    def check_bullet_hit_player(self, player: 'Player') -> bool:
        """检查子弹是否击中玩家"""
        for bullet in self.bullets[:]:
            if bullet.rect.colliderect(player.rect):
                self.bullets.remove(bullet)
                return True
        return False
    
    def _on_stomped(self) -> None:
        """不能被踩"""
        pass
    
    def render(self, screen: pygame.Surface, camera_offset: tuple = (0, 0)) -> None:
        """渲染发射怪和子弹"""
        super().render(screen, camera_offset)
        
        # 渲染子弹
        for bullet in self.bullets:
            bullet.render(screen, camera_offset)
