"""
敌人基类模块
AI辅助生成: 定义所有敌人的基类

此模块提供Enemy抽象基类，所有敌人类型都继承自此类。
封装了敌人的通用行为如巡逻、被踩、死亡等。

设计模式: 模板方法模式 (Template Method Pattern)
基类定义算法骨架，子类实现具体步骤
"""

import pygame
from abc import abstractmethod
from typing import List, Tuple, Optional, TYPE_CHECKING

from ..entity import AnimatedEntity
from ...settings import GRAVITY, MAX_FALL_SPEED, TILE_SIZE
from ...core.event_system import EventSystem, GameEvent

if TYPE_CHECKING:
    from ..player import Player


class SafeZone:
    """
    安全区域类
    AI辅助生成: 定义敌人禁止进入的区域（如复活点）
    """
    
    def __init__(self, x: float, y: float, width: float, height: float):
        """
        初始化安全区域
        
        Args:
            x, y: 左上角坐标
            width, height: 区域尺寸
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
    
    def contains(self, x: float, y: float, width: float = 0, height: float = 0) -> bool:
        """检查某个点或矩形是否在安全区域内"""
        check_rect = pygame.Rect(x, y, max(1, width), max(1, height))
        return self.rect.colliderect(check_rect)
    
    def get_push_direction(self, x: float, width: float) -> int:
        """
        获取推离方向
        
        Args:
            x: 实体X坐标
            width: 实体宽度
            
        Returns:
            推离方向 (1=向右, -1=向左)
        """
        entity_center = x + width / 2
        zone_center = self.x + self.width / 2
        return 1 if entity_center < zone_center else -1


class Enemy(AnimatedEntity):
    """
    敌人抽象基类
    
    定义敌人的通用行为和属性，具体敌人类型需要继承此类。
    
    Attributes:
        speed: 移动速度
        direction: 移动方向 (1=右, -1=左)
        can_be_stomped: 是否可以被踩
        score_value: 击杀获得的分数
        is_dead: 是否已死亡
        death_timer: 死亡动画计时器
    """
    
    def __init__(self, x: float, y: float, width: int, height: int):
        """
        初始化敌人
        
        Args:
            x: 初始X坐标
            y: 初始Y坐标
            width: 宽度
            height: 高度
        """
        super().__init__(x, y, width, height)
        
        # 设置敌人专属的调试边框颜色（红色）
        self.debug_box_color = (255, 50, 50)
        
        # 移动属性
        self.speed = 1.0
        self.direction = -1  # 默认向左移动
        self.facing_right = False
        
        # 转向冷却（防止抖动）
        self.turn_cooldown = 0.0
        self.turn_cooldown_duration = 0.5  # 转向后0.5秒内不能再转向（增加防抖时间）
        
        # 行为属性
        self.can_be_stomped = True
        self.score_value = 100
        
        # 状态
        self.is_dead = False
        self.death_timer = 0.0
        self.death_duration = 0.5  # 死亡动画持续时间
        
        # 困难模式修饰
        self.speed_multiplier = 1.0
        
        # 安全区域引用（用于禁入检测）
        self.safe_zones: List['SafeZone'] = []
    
    def set_safe_zones(self, zones: List['SafeZone']) -> None:
        """设置需要避开的安全区域"""
        self.safe_zones = zones
    
    def apply_difficulty(self, multiplier: float) -> None:
        """
        应用难度修饰
        
        AI辅助生成: 策略模式的应用，根据难度调整敌人行为
        
        Args:
            multiplier: 速度倍率
        """
        self.speed_multiplier = multiplier
    
    def update(self, dt: float) -> None:
        """
        更新敌人状态
        
        模板方法：定义更新流程，子类可重写具体步骤
        
        Args:
            dt: 时间增量
        """
        if not self.active:
            return
        
        if self.is_dead:
            self._update_death(dt)
            return
        
        # 更新转向冷却
        if self.turn_cooldown > 0:
            self.turn_cooldown -= dt
        
        # 应用重力
        self.velocity_y += GRAVITY
        if self.velocity_y > MAX_FALL_SPEED:
            self.velocity_y = MAX_FALL_SPEED
        
        # 移动
        self.velocity_x = self.speed * self.direction * self.speed_multiplier
        
        # 检测是否会进入安全区域
        next_x = self.x + self.velocity_x
        if self._would_enter_safe_zone(next_x):
            # 转向，不进入安全区域
            self.direction *= -1
            self.velocity_x = self.speed * self.direction * self.speed_multiplier
            next_x = self.x + self.velocity_x
        
        # 更新位置
        self.x = next_x
        self.y += self.velocity_y
        
        # 更新朝向
        self.facing_right = self.direction > 0
        
        # 更新碰撞矩形
        self.update_rect()
        
        # 子类特有行为
        self._update_behavior(dt)
        
        # 更新动画
        self.update_animation(dt)
    
    @abstractmethod
    def _update_behavior(self, dt: float) -> None:
        """
        更新敌人特有行为（子类实现）
        
        Args:
            dt: 时间增量
        """
        pass
    
    def _would_enter_safe_zone(self, next_x: float) -> bool:
        """
        检测下一帧是否会进入安全区域
        AI辅助生成: 防止敌人进入玩家复活点
        
        Args:
            next_x: 下一帧的X坐标
            
        Returns:
            是否会进入安全区域
        """
        if not self.safe_zones:
            return False
        
        for zone in self.safe_zones:
            if zone.contains(next_x, self.y, self.width, self.height):
                return True
        
        return False
    
    def _update_death(self, dt: float) -> None:
        """更新死亡状态"""
        self.death_timer += dt
        if self.death_timer >= self.death_duration:
            self.active = False
    
    def apply_collision(self, tiles: List[pygame.Rect]) -> None:
        """
        应用与瓦片的碰撞检测
        
        Args:
            tiles: 碰撞瓦片列表
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
            
            # 垂直碰撞优先处理
            if min_overlap == overlap_top and self.velocity_y >= 0:
                self.y = tile.top - self.height
                self.velocity_y = 0
                self.on_ground = True
            elif min_overlap == overlap_bottom and self.velocity_y < 0:
                self.y = tile.bottom
                self.velocity_y = 0
            elif min_overlap == overlap_left:
                # 撞到了瓦片的左边（敌人在瓦片左侧）
                self.x = tile.left - self.width - 1  # 额外1像素缓冲
                hit_wall = True
                wall_on_right = True  # 墙在敌人右边
            elif min_overlap == overlap_right:
                # 撞到了瓦片的右边（敌人在瓦片右侧）
                self.x = tile.right + 1  # 额外1像素缓冲
                hit_wall = True
                wall_on_left = True  # 墙在敌人左边
            
            self.update_rect()
        
        # 根据撞墙情况调整方向（有冷却时间防止抖动）
        if hit_wall and self.turn_cooldown <= 0:
            if wall_on_right and self.direction > 0:
                # 正在向右走，撞到右边的墙，转向左
                self.direction = -1
                self.turn_cooldown = self.turn_cooldown_duration
            elif wall_on_left and self.direction < 0:
                # 正在向左走，撞到左边的墙，转向右
                self.direction = 1
                self.turn_cooldown = self.turn_cooldown_duration
            elif wall_on_right:
                # 墙在右边但不是向右走，强制向左
                self.direction = -1
                self.turn_cooldown = self.turn_cooldown_duration
            elif wall_on_left:
                # 墙在左边但不是向左走，强制向右
                self.direction = 1
                self.turn_cooldown = self.turn_cooldown_duration
    
    def check_edge(self, tiles: List[pygame.Rect]) -> None:
        """
        检测是否在平台边缘（防止掉落）
        
        AI辅助生成: 简单AI让敌人在边缘转向
        
        Args:
            tiles: 碰撞瓦片列表
        """
        if not self.on_ground or self.turn_cooldown > 0:
            return
        
        # 检测前方下一格是否有地面（向前看一整格）
        if self.direction > 0:
            # 向右移动，检测右前方
            check_x = self.x + self.width + 4
        else:
            # 向左移动，检测左前方
            check_x = self.x - TILE_SIZE // 2
        
        check_y = self.y + self.height + 4
        check_rect = pygame.Rect(check_x, check_y, TILE_SIZE // 2, TILE_SIZE)
        
        has_ground = any(check_rect.colliderect(tile) for tile in tiles)
        
        if not has_ground:
            self.direction *= -1  # 转向
            self.turn_cooldown = self.turn_cooldown_duration
            # 转向后稍微后退一点，避免卡在边缘
            self.x -= self.direction * 4
    
    def on_stomp(self, player: 'Player') -> bool:
        """
        被玩家踩踏时调用
        
        Args:
            player: 踩踏的玩家
            
        Returns:
            是否成功被踩（用于判断玩家是否反弹）
        """
        if not self.can_be_stomped or self.is_dead:
            return False
        
        self.is_dead = True
        self._on_stomped()
        
        # 发送事件
        EventSystem().emit(GameEvent.ENEMY_STOMP, {'score': self.score_value})
        
        return True
    
    @abstractmethod
    def _on_stomped(self) -> None:
        """被踩踏时的具体行为（子类实现）"""
        pass
    
    def on_player_collision(self, player: 'Player') -> bool:
        """
        与玩家碰撞时调用
        
        Args:
            player: 碰撞的玩家
            
        Returns:
            玩家是否应受到伤害
        """
        if self.is_dead:
            return False
        
        # 检查是否从上方踩踏
        player_bottom = player.y + player.height
        player_center_y = player.y + player.height / 2
        enemy_top = self.y
        enemy_center_y = self.y + self.height / 2
        
        # 踩踏条件（更宽松的判定）：
        # 1. 玩家正在下落 (velocity_y > 0)
        # 2. 玩家底部在敌人上半部分 (player_bottom < enemy_top + self.height * 0.6)
        # 3. 或者玩家中心在敌人中心上方
        is_falling = player.velocity_y > 0
        is_above = player_bottom < enemy_top + self.height * 0.6
        player_higher = player_center_y < enemy_center_y
        
        if is_falling and (is_above or player_higher):
            if self.on_stomp(player):
                player.stomp_enemy()
                return False
        
        # 否则玩家受伤
        return True
    
    def kill(self) -> None:
        """强制击杀敌人（如被星星玩家碰到）"""
        self.is_dead = True
        self.active = False
        EventSystem().emit(GameEvent.ENEMY_DEATH, {'score': self.score_value})
