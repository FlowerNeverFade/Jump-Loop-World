"""
乌龟壳怪模块
AI辅助生成: 实现乌龟壳敌人

乌龟壳怪可以被踩成壳状态，壳可以被踢动撞击其他敌人。
"""

import pygame
from typing import TYPE_CHECKING, List

from .enemy import Enemy
from ...settings import TILE_SIZE
from ...core.resource_manager import ResourceManager
from ...core.event_system import EventSystem, GameEvent

if TYPE_CHECKING:
    from ..player import Player


class Koopa(Enemy):
    """
    乌龟壳怪类 (Shellback)
    
    比蘑菇怪更复杂的敌人，被踩后会变成壳状态。
    壳状态下可以被踢动，滑动的壳会击杀接触到的敌人。
    
    Attributes:
        shell_mode: 是否处于壳模式
        shell_moving: 壳是否在滑动
        shell_speed: 壳滑动速度
    """
    
    def __init__(self, x: float, y: float):
        """
        初始化乌龟壳怪
        
        Args:
            x: 初始X坐标
            y: 初始Y坐标
        """
        # 乌龟比蘑菇怪高一点
        super().__init__(x, y, TILE_SIZE, int(TILE_SIZE * 1.25))
        
        # 调整碰撞体积 - 去掉头顶空白区域
        self.collision_width = TILE_SIZE - 4  # 28像素
        self.collision_height = TILE_SIZE  # 32像素（去掉头顶8像素）
        self.collision_offset_x = 2  # 居中
        self.collision_offset_y = 8  # 从头顶下移8像素
        
        # 更新碰撞矩形
        self.rect.width = self.collision_width
        self.rect.height = self.collision_height
        
        self.speed = 0.8
        self.score_value = 100
        
        # 壳状态
        self.shell_mode = False
        self.shell_moving = False
        self.shell_speed = 8.0  # 提高壳滑动速度
        self.shell_direction = 1
        
        # 壳模式计时器（静止一段时间后会恢复）
        self.shell_timer = 0.0
        self.shell_recover_time = 5.0  # 5秒后恢复
        
        # 壳滑动距离追踪（滑动一定距离后消失）
        self.shell_slide_distance = 0.0
        self.shell_max_distance = 800.0  # 最大滑动距离（像素），约25格
        self.shell_bounce_count = 0
        self.shell_max_bounces = 3  # 最多反弹3次后消失
        
        # 踢壳后的无敌时间（防止踢壳后立即被壳伤害）
        self.kick_grace_timer = 0.0
        self.kick_grace_duration = 0.5  # 踢壳后0.5秒内不会伤害玩家
        
        # 动画速度
        self.animation_speed = 5.0
        
        # 加载精灵
        self._load_sprites()
        
        # 开始行走动画
        self.play_animation('walk')
    
    def update_rect(self) -> None:
        """更新碰撞矩形位置（考虑偏移量）"""
        self.rect.x = int(self.x + self.collision_offset_x)
        self.rect.y = int(self.y + self.collision_offset_y)
    
    def _load_sprites(self) -> None:
        """加载乌龟壳怪精灵"""
        rm = ResourceManager()
        sprites = rm.load_enemy_sprites('shellback')
        
        self.add_animation('walk', sprites['walk'])
        self.shell_image = sprites['shell']
    
    def update(self, dt: float) -> None:
        """
        重写更新方法以正确处理壳模式
        壳模式需要在计算位置前设置正确的速度
        """
        if not self.active:
            return
        
        if self.is_dead:
            self._update_death(dt)
            return
        
        # 更新转向冷却
        if self.turn_cooldown > 0:
            self.turn_cooldown -= dt
        
        # 壳模式特殊处理
        if self.shell_mode:
            self._update_shell_mode(dt)
        
        # 应用重力
        from ...settings import GRAVITY, MAX_FALL_SPEED
        self.velocity_y += GRAVITY
        if self.velocity_y > MAX_FALL_SPEED:
            self.velocity_y = MAX_FALL_SPEED
        
        # 设置水平速度
        if self.shell_mode:
            # 壳模式：使用壳速度
            if self.shell_moving:
                self.velocity_x = self.shell_speed * self.shell_direction
                # 追踪滑动距离
                self.shell_slide_distance += abs(self.velocity_x)
                
                # 检查是否超过最大滑动距离或反弹次数
                if (self.shell_slide_distance >= self.shell_max_distance or 
                    self.shell_bounce_count >= self.shell_max_bounces):
                    self.kill()  # 壳消失
                    return
            else:
                self.velocity_x = 0
        else:
            # 正常模式：使用普通速度
            self.velocity_x = self.speed * self.direction * self.speed_multiplier
        
        # 检测是否会进入安全区域
        next_x = self.x + self.velocity_x
        if self._would_enter_safe_zone(next_x):
            self.direction *= -1
            if self.shell_mode and self.shell_moving:
                self.shell_direction *= -1
                self.shell_bounce_count += 1
                self.velocity_x = self.shell_speed * self.shell_direction
            else:
                self.velocity_x = self.speed * self.direction * self.speed_multiplier
            next_x = self.x + self.velocity_x
        
        # 更新位置
        self.x = next_x
        self.y += self.velocity_y
        
        # 更新朝向
        self.facing_right = self.direction > 0
        
        # 更新碰撞矩形
        self.update_rect()
        
        # 更新动画
        self.update_animation(dt)
    
    def _update_behavior(self, dt: float) -> None:
        """更新乌龟壳怪特有行为（保留以兼容基类）"""
        pass
    
    def _update_shell_mode(self, dt: float) -> None:
        """更新壳模式行为"""
        # 更新踢壳无敌计时器
        if self.kick_grace_timer > 0:
            self.kick_grace_timer -= dt
        
        if not self.shell_moving:
            # 壳静止，计时恢复
            self.shell_timer += dt
            if self.shell_timer >= self.shell_recover_time:
                # 恢复正常状态
                self.shell_mode = False
                self.shell_timer = 0
                self.height = int(TILE_SIZE * 1.25)  # 恢复高度
                # 恢复正常模式的碰撞参数
                self.collision_height = TILE_SIZE  # 32像素
                self.collision_offset_y = 8  # 从头顶下移8像素
                self.rect.height = self.collision_height
                self.update_rect()
                self.play_animation('walk')
    
    def _on_stomped(self) -> None:
        """被踩踏时的行为"""
        if not self.shell_mode:
            # 第一次踩踏：进入壳模式
            self.shell_mode = True
            self.shell_moving = False
            self.shell_timer = 0
            self.velocity_x = 0
            self.height = TILE_SIZE  # 缩小高度
            # 更新壳模式的碰撞参数
            self.collision_height = TILE_SIZE - 4  # 壳高度稍小
            self.collision_offset_y = 4  # 壳的偏移更小
            self.rect.height = self.collision_height
            self.set_image(self.shell_image)
            self.is_dead = False  # 不算死亡，只是变成壳
            self.update_rect()  # 更新碰撞矩形
            # 设置初始无敌时间，防止踩完后立即被伤害
            self.kick_grace_timer = self.kick_grace_duration
        elif not self.shell_moving:
            # 壳静止时被踩：开始滑动
            self.shell_moving = True
            self.shell_timer = 0
            self.kick_grace_timer = self.kick_grace_duration
        else:
            # 壳滑动时被踩：停止滑动
            self.shell_moving = False
    
    def on_stomp(self, player: 'Player') -> bool:
        """重写踩踏逻辑"""
        if self.is_dead:
            return False
        
        self._on_stomped()
        
        # 确定壳滑动方向（根据玩家位置）
        if self.shell_mode and self.shell_moving:
            player_center = player.x + player.width / 2
            self_center = self.x + self.width / 2
            self.shell_direction = 1 if player_center < self_center else -1
        
        # 只有完全击杀时才发送事件
        if not self.shell_mode:
            EventSystem().emit(GameEvent.ENEMY_STOMP, {'score': self.score_value})
        
        return True
    
    def kick_shell(self, from_left: bool) -> None:
        """
        踢壳
        
        Args:
            from_left: 是否从左边踢
        """
        if self.shell_mode and not self.shell_moving:
            self.shell_moving = True
            self.shell_direction = 1 if from_left else -1
            self.shell_timer = 0
            # 重置滑动距离和反弹次数
            self.shell_slide_distance = 0.0
            self.shell_bounce_count = 0
            # 设置踢壳无敌时间，防止踢壳后立即被伤害
            self.kick_grace_timer = self.kick_grace_duration
    
    def apply_collision(self, tiles: List[pygame.Rect]) -> None:
        """
        重写碰撞检测以正确处理壳反弹（考虑碰撞偏移）
        """
        if self.is_dead:
            return
        
        self.on_ground = False
        self.update_rect()
        
        # 标记是否发生水平碰撞
        hit_wall = False
        wall_on_left = False
        wall_on_right = False
        
        for tile in tiles:
            if not self.rect.colliderect(tile):
                continue
            
            # 计算重叠
            overlap_left = self.rect.right - tile.left
            overlap_right = tile.right - self.rect.left
            overlap_top = self.rect.bottom - tile.top
            overlap_bottom = tile.bottom - self.rect.top
            
            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
            
            if min_overlap == overlap_top and self.velocity_y >= 0:
                # 考虑碰撞偏移
                self.y = tile.top - self.collision_offset_y - self.collision_height
                self.velocity_y = 0
                self.on_ground = True
            elif min_overlap == overlap_bottom and self.velocity_y < 0:
                self.y = tile.bottom - self.collision_offset_y
                self.velocity_y = 0
            elif min_overlap == overlap_left:
                # 右边撞墙
                self.x = tile.left - self.collision_offset_x - self.collision_width - 1  # 额外1像素缓冲
                hit_wall = True
                wall_on_right = True
            elif min_overlap == overlap_right:
                # 左边撞墙
                self.x = tile.right - self.collision_offset_x + 1  # 额外1像素缓冲
                hit_wall = True
                wall_on_left = True
            
            self.update_rect()
        
        # 根据撞墙情况调整方向（有冷却时间防止抖动，但壳模式不受限）
        should_turn = hit_wall and (self.turn_cooldown <= 0 or (self.shell_mode and self.shell_moving))
        if should_turn:
            if wall_on_right and self.direction > 0:
                # 正在向右走，撞到右边的墙，转向左
                self.direction = -1
                self.turn_cooldown = self.turn_cooldown_duration
                if self.shell_mode and self.shell_moving:
                    self.shell_direction = -1
                    self.shell_bounce_count += 1
            elif wall_on_left and self.direction < 0:
                # 正在向左走，撞到左边的墙，转向右
                self.direction = 1
                self.turn_cooldown = self.turn_cooldown_duration
                if self.shell_mode and self.shell_moving:
                    self.shell_direction = 1
                    self.shell_bounce_count += 1
            elif wall_on_right:
                # 墙在右边但不是向右走，强制向左
                self.direction = -1
                self.turn_cooldown = self.turn_cooldown_duration
                if self.shell_mode and self.shell_moving:
                    self.shell_direction = -1
            elif wall_on_left:
                # 墙在左边但不是向左走，强制向右
                self.direction = 1
                self.turn_cooldown = self.turn_cooldown_duration
                if self.shell_mode and self.shell_moving:
                    self.shell_direction = 1
    
    def check_shell_collision(self, enemies: List['Enemy']) -> None:
        """
        检测滑动壳与其他敌人的碰撞
        
        AI辅助生成: 实现壳击杀其他敌人的逻辑
        
        Args:
            enemies: 敌人列表
        """
        if not self.shell_mode or not self.shell_moving:
            return
        
        for enemy in enemies:
            if enemy is self or not enemy.active or enemy.is_dead:
                continue
            
            if self.rect.colliderect(enemy.rect):
                enemy.kill()
    
    def on_player_collision(self, player: 'Player') -> bool:
        """重写玩家碰撞逻辑"""
        if self.is_dead:
            return False
        
        # 壳模式特殊处理
        if self.shell_mode:
            # 踢壳后的无敌时间内不会伤害玩家
            if self.kick_grace_timer > 0:
                return False
            
            # 检查是否从上方踩踏（宽松判定）
            player_bottom = player.y + player.height
            player_center_y = player.y + player.height / 2
            enemy_top = self.y
            enemy_center_y = self.y + self.height / 2
            
            is_falling = player.velocity_y > 0
            is_above = player_bottom < enemy_top + self.height * 0.6
            player_higher = player_center_y < enemy_center_y
            is_stomping = is_falling and (is_above or player_higher)
            
            if not self.shell_moving:
                # 静止的壳可以被踢或踩
                player_center = player.x + player.width / 2
                self_center = self.x + self.width / 2
                self.kick_shell(player_center < self_center)
                
                # 如果是踩踏，让玩家弹跳
                if is_stomping:
                    player.stomp_enemy()
                
                return False
            else:
                # 滑动的壳：如果从上方踩踏可以停止壳
                if is_stomping:
                    self.shell_moving = False
                    self.kick_grace_timer = self.kick_grace_duration
                    player.stomp_enemy()
                    return False
                else:
                    # 从侧面碰到滑动的壳会伤害玩家
                    return True
        
        # 正常状态使用基类逻辑
        return super().on_player_collision(player)
    
    def render(self, screen: pygame.Surface, camera_offset: tuple = (0, 0)) -> None:
        """渲染乌龟壳怪"""
        if not self.active:
            return
        
        render_x = int(self.x - camera_offset[0])
        render_y = int(self.y - camera_offset[1])
        
        if self.shell_mode:
            # 渲染壳图像
            if self.shell_image:
                screen.blit(self.shell_image, (render_x, render_y))
            
            # 绘制调试边框（壳模式用黄色表示可踢）
            from ..entity import Entity
            if Entity.show_debug_box:
                if self.shell_moving:
                    color = (255, 100, 100)  # 滑动中 - 红色（危险）
                else:
                    color = (255, 255, 0)  # 静止 - 黄色（可踢）
                debug_rect = pygame.Rect(render_x, render_y, self.width, self.height)
                pygame.draw.rect(screen, color, debug_rect, 2)
        else:
            super().render(screen, camera_offset)
