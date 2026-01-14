"""
移动锯齿模块
AI辅助生成: 实现沿轨道移动的危险障碍
"""

import pygame
from typing import TYPE_CHECKING

from ...settings import TILE_SIZE
from ...core.resource_manager import ResourceManager

if TYPE_CHECKING:
    from ..player import Player


class MovingSaw:
    """
    移动锯齿
    
    沿固定轨道来回移动的危险障碍，碰到即伤害玩家。
    """
    
    def __init__(self, x: float, y: float, move_range: int = 4, vertical: bool = False):
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # 移动参数
        self.move_range = move_range * TILE_SIZE
        self.speed = 3.0
        self.direction = 1
        self.vertical = vertical  # 是否垂直移动
        
        # 动画
        self.frame = 0
        self.animation_timer = 0.0
        
        self.active = True
        self._load_sprites()
    
    def _load_sprites(self) -> None:
        """加载锯齿精灵"""
        rm = ResourceManager()
        self.frames = []
        for i in range(1, 5):
            img = rm.load_image(f'obstacles/saw_{i}.png')
            if img:
                self.frames.append(img)
    
    def update(self, dt: float) -> None:
        """更新锯齿位置和动画"""
        # 移动
        if self.vertical:
            self.y += self.speed * self.direction
            if self.y >= self.start_y + self.move_range:
                self.direction = -1
            elif self.y <= self.start_y:
                self.direction = 1
        else:
            self.x += self.speed * self.direction
            if self.x >= self.start_x + self.move_range:
                self.direction = -1
            elif self.x <= self.start_x:
                self.direction = 1
        
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
        # 动画
        self.animation_timer += dt
        if self.animation_timer >= 0.05:
            self.animation_timer = 0.0
            self.frame = (self.frame + 1) % len(self.frames) if self.frames else 0
    
    def check_player_collision(self, player: 'Player') -> bool:
        """检查玩家是否碰到锯齿"""
        return player.rect.colliderect(self.rect)
    
    def render(self, screen: pygame.Surface, camera_offset: tuple) -> None:
        """渲染锯齿"""
        if not self.active:
            return
        
        render_x = int(self.x - camera_offset[0])
        render_y = int(self.y - camera_offset[1])
        
        if self.frames and self.frame < len(self.frames):
            screen.blit(self.frames[self.frame], (render_x, render_y))
        else:
            # 备用：画一个圆
            pygame.draw.circle(screen, (150, 150, 160), 
                             (render_x + 16, render_y + 16), 14)
