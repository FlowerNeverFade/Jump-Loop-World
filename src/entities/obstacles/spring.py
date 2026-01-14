"""
弹簧障碍物模块
AI辅助生成: 实现弹跳平台

踩上弹簧会将玩家弹起。
"""

import pygame
from typing import TYPE_CHECKING

from ...settings import TILE_SIZE
from ...core.resource_manager import ResourceManager

if TYPE_CHECKING:
    from ..player import Player


class Spring:
    """
    弹簧类
    
    踩上去会将玩家弹起的平台。
    """
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # 弹跳力度
        self.bounce_power = -20
        
        # 状态
        self.is_compressed = False
        self.compress_timer = 0.0
        self.compress_duration = 0.2
        
        self.active = True
        
        self._load_sprites()
    
    def _load_sprites(self) -> None:
        """加载弹簧精灵"""
        rm = ResourceManager()
        self.idle_image = rm.load_image('obstacles/spring_idle.png')
        self.compressed_image = rm.load_image('obstacles/spring_compressed.png')
        self.current_image = self.idle_image
    
    def update(self, dt: float) -> None:
        """更新弹簧状态"""
        if self.is_compressed:
            self.compress_timer += dt
            if self.compress_timer >= self.compress_duration:
                self.is_compressed = False
                self.compress_timer = 0.0
                self.current_image = self.idle_image
    
    def check_player_collision(self, player: 'Player') -> bool:
        """检查玩家碰撞并弹起"""
        if not self.active:
            return False
        
        # 检查玩家是否从上方落下
        if player.rect.colliderect(self.rect) and player.velocity_y > 0:
            # 玩家底部接近弹簧顶部
            if player.rect.bottom <= self.rect.top + 16:
                # 弹起玩家
                player.velocity_y = self.bounce_power
                player.is_jumping = True
                player.on_ground = False
                
                # 压缩弹簧
                self.is_compressed = True
                self.compress_timer = 0.0
                self.current_image = self.compressed_image
                
                return True
        return False
    
    def render(self, screen: pygame.Surface, camera_offset: tuple) -> None:
        """渲染弹簧"""
        if not self.active or not self.current_image:
            return
        
        render_x = int(self.x - camera_offset[0])
        render_y = int(self.y - camera_offset[1])
        screen.blit(self.current_image, (render_x, render_y))
