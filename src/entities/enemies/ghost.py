"""
幽灵怪模块
AI辅助生成: 实现可以穿墙的敌人

幽灵怪可以穿过墙壁，会追踪玩家位置。
"""

import pygame
import math
from typing import TYPE_CHECKING, Optional

from .enemy import Enemy
from ...settings import TILE_SIZE
from ...core.resource_manager import ResourceManager

if TYPE_CHECKING:
    from ..player import Player


class Ghost(Enemy):
    """
    幽灵怪类
    
    可以穿过墙壁的敌人，会缓慢追踪玩家位置。
    只有在玩家不看它时才会移动（类似Weeping Angel机制）。
    """
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, TILE_SIZE, TILE_SIZE)
        
        self.speed = 1.0
        self.score_value = 250
        
        # 幽灵特性
        self.can_pass_walls = True  # 可以穿墙
        self.chase_speed = 2.0  # 追踪速度
        self.target_player: Optional['Player'] = None
        
        # 动画帧
        self.animation_frame = 0
        self.animation_timer = 0.0
        
        # 是否被玩家看着（面向幽灵方向）
        self.is_being_watched = False
        
        self._load_sprites()
    
    def _load_sprites(self) -> None:
        """加载幽灵精灵"""
        rm = ResourceManager()
        
        frames = []
        for i in range(1, 3):
            img = rm.load_image(f'enemies/ghost_{i}.png')
            if img:
                frames.append(img)
        
        if frames:
            self.add_animation('float', frames)
            self.play_animation('float')
    
    def set_target(self, player: 'Player') -> None:
        """设置目标玩家"""
        self.target_player = player
    
    def _update_behavior(self, dt: float) -> None:
        """更新幽灵行为"""
        if not self.target_player:
            return
        
        # 检查玩家是否面向幽灵
        player = self.target_player
        ghost_on_left = self.x < player.x
        player_facing_ghost = (ghost_on_left and not player.facing_right) or \
                              (not ghost_on_left and player.facing_right)
        
        self.is_being_watched = player_facing_ghost
        
        # 只有不被看着时才移动
        if not self.is_being_watched:
            # 追踪玩家
            dx = player.x - self.x
            dy = player.y - self.y
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist > 0:
                # 归一化并移动
                self.velocity_x = (dx / dist) * self.chase_speed
                self.velocity_y = (dy / dist) * self.chase_speed
        else:
            # 被看着时停止
            self.velocity_x = 0
            self.velocity_y = 0
        
        # 更新朝向
        if self.target_player:
            self.facing_right = self.x < self.target_player.x
    
    def apply_collision(self, tiles) -> None:
        """幽灵可以穿墙，不需要碰撞检测"""
        # 只更新位置，不检测墙壁碰撞
        self.update_rect()
        self.on_ground = True  # 幽灵总是"在地面上"（不受重力影响）
    
    def update(self, dt: float) -> None:
        """重写更新，幽灵不受重力影响"""
        if not self.active:
            return
        
        if self.is_dead:
            self._update_death(dt)
            return
        
        # 更新转向冷却
        if self.turn_cooldown > 0:
            self.turn_cooldown -= dt
        
        # 不应用重力，直接使用行为中计算的速度
        self._update_behavior(dt)
        
        # 更新位置
        next_x = self.x + self.velocity_x
        next_y = self.y + self.velocity_y
        
        # 避免进入安全区域（如出生点）
        if getattr(self, "safe_zones", None):
            for zone in self.safe_zones:
                if zone.contains(next_x, next_y, self.width, self.height):
                    push_dir = zone.get_push_direction(self.x, self.width)
                    # 直接推到安全区外侧，并让其横向远离安全区
                    if push_dir > 0:
                        next_x = zone.x + zone.width + 2
                    else:
                        next_x = zone.x - self.width - 2
                    self.velocity_x = push_dir * max(abs(self.velocity_x), 0.5)
                    break
        
        self.x = next_x
        self.y = next_y
        
        self.update_rect()
        self.update_animation(dt)
    
    def _on_stomped(self) -> None:
        """被踩踏时消失"""
        self.velocity_x = 0
        self.velocity_y = 0
    
    def render(self, screen: pygame.Surface, camera_offset: tuple = (0, 0)) -> None:
        """渲染幽灵（半透明效果）"""
        if not self.active:
            return
        
        render_x = int(self.x - camera_offset[0])
        render_y = int(self.y - camera_offset[1])
        
        current_image = self.get_current_image()
        if current_image:
            # 被看着时更透明
            alpha = 100 if self.is_being_watched else 180
            current_image = current_image.copy()
            current_image.set_alpha(alpha)
            screen.blit(current_image, (render_x, render_y))
