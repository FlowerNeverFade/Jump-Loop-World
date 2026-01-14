"""
激光障碍物模块
AI辅助生成: 实现周期性发射激光的障碍物
"""

import pygame
from typing import TYPE_CHECKING

from ...settings import TILE_SIZE
from ...core.resource_manager import ResourceManager

if TYPE_CHECKING:
    from ..player import Player


class Laser:
    """
    激光发射器
    
    周期性发射激光，碰到激光会伤害玩家。
    """
    
    def __init__(self, x: float, y: float, direction: int = 1):
        self.x = x
        self.y = y
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        self.direction = direction  # 1=右, -1=左
        self.beam_length = TILE_SIZE * 8
        
        # 状态: 'off', 'charging', 'on'
        self.state = 'off'
        self.timer = 0.0
        self.off_duration = 2.0
        self.charge_duration = 0.5
        self.on_duration = 1.5
        
        self.active = True
        self._load_sprites()
    
    def _load_sprites(self) -> None:
        """加载激光精灵"""
        rm = ResourceManager()
        self.emitter_off = rm.load_image('obstacles/laser_emitter_off.png')
        self.emitter_charging = rm.load_image('obstacles/laser_emitter_charging.png')
        self.emitter_on = rm.load_image('obstacles/laser_emitter_on.png')
        self.beam_image = rm.load_image('obstacles/laser_beam.png')
    
    def update(self, dt: float) -> None:
        """更新激光状态"""
        self.timer += dt
        
        if self.state == 'off':
            if self.timer >= self.off_duration:
                self.state = 'charging'
                self.timer = 0.0
        elif self.state == 'charging':
            if self.timer >= self.charge_duration:
                self.state = 'on'
                self.timer = 0.0
        elif self.state == 'on':
            if self.timer >= self.on_duration:
                self.state = 'off'
                self.timer = 0.0
    
    def get_beam_rect(self) -> pygame.Rect:
        """获取激光束的碰撞矩形"""
        if self.state != 'on':
            return pygame.Rect(0, 0, 0, 0)
        
        if self.direction > 0:
            return pygame.Rect(self.x + self.width, self.y + 12, self.beam_length, 8)
        else:
            return pygame.Rect(self.x - self.beam_length, self.y + 12, self.beam_length, 8)
    
    def check_player_collision(self, player: 'Player') -> bool:
        """检查玩家是否碰到激光"""
        if self.state != 'on':
            return False
        
        beam_rect = self.get_beam_rect()
        return player.rect.colliderect(beam_rect)
    
    def render(self, screen: pygame.Surface, camera_offset: tuple) -> None:
        """渲染激光"""
        if not self.active:
            return
        
        render_x = int(self.x - camera_offset[0])
        render_y = int(self.y - camera_offset[1])
        
        # 渲染发射器
        emitter_img = self.emitter_off
        if self.state == 'charging':
            emitter_img = self.emitter_charging
        elif self.state == 'on':
            emitter_img = self.emitter_on
        
        if emitter_img:
            screen.blit(emitter_img, (render_x, render_y))
        
        # 渲染激光束
        if self.state == 'on' and self.beam_image:
            beam_x = render_x + self.width if self.direction > 0 else render_x - self.beam_length
            beam_y = render_y + 12
            
            # 绘制激光束
            beam_rect = pygame.Rect(beam_x, beam_y, self.beam_length, 8)
            pygame.draw.rect(screen, (255, 50, 50, 200), beam_rect)
            pygame.draw.rect(screen, (255, 200, 200), (beam_x, beam_y + 2, self.beam_length, 4))
