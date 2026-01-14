"""
玩家类模块
AI辅助生成: 实现玩家角色的所有行为

此模块包含Player类，负责玩家的移动、跳跃、状态管理等。
使用状态模式管理玩家的不同状态（小、大、无敌）。

设计模式: 状态模式 (State Pattern)
用于管理玩家的不同能力状态
"""

import pygame
from enum import Enum, auto
from typing import Optional, List, Dict, Any, TYPE_CHECKING

from .entity import AnimatedEntity
from ..settings import (
    GRAVITY, MAX_FALL_SPEED, JUMP_POWER, PLAYER_SPEED, PLAYER_ACCELERATION,
    FRICTION, AIR_FRICTION, PLAYER_WIDTH, PLAYER_HEIGHT, TILE_SIZE
)
from ..core.resource_manager import ResourceManager
from ..core.event_system import EventSystem, GameEvent
from ..core.player_config import PlayerConfig
from ..core.save_manager import SaveManager
from ..core.key_bindings import KeyBindings

if TYPE_CHECKING:
    from ..levels.level import Level


class PlayerState(Enum):
    """
    玩家状态枚举
    """
    SMALL = auto()       # 小型（初始状态）
    BIG = auto()         # 大型（吃蘑菇后）
    INVINCIBLE = auto()  # 无敌（吃星星后）


class Player(AnimatedEntity):
    """
    玩家类
    
    控制玩家角色的所有行为，包括移动、跳跃、碰撞响应等。
    
    Attributes:
        state: 玩家当前状态（小/大/无敌）
        is_jumping: 是否正在跳跃
        can_jump: 是否可以跳跃
        invincible_timer: 无敌计时器
        hurt_timer: 受伤无敌计时器
        color: 玩家颜色 ('red' 或 'green')
    """
    
    def __init__(self, x: float, y: float, color: str = 'red', player_id: int = 1, two_player_mode: bool = False):
        """
        初始化玩家
        
        Args:
            x: 初始X坐标
            y: 初始Y坐标
            color: 玩家颜色
            player_id: 玩家ID（1或2，用于双人模式区分控制）
            two_player_mode: 是否双人模式（双人模式不加载存档能力）
        """
        super().__init__(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        
        # 设置玩家专属的调试边框颜色（蓝色）
        self.debug_box_color = (0, 150, 255)
        
        # 碰撞体积 - 比精灵稍小，去掉头顶空白区域
        self.collision_width = PLAYER_WIDTH - 4   # 28 (左右各缩2像素)
        # 只缩短“头顶”碰撞，让玩家能通过 1 格高（32px）的通道；底部对齐不变
        self.collision_height = TILE_SIZE  # 32
        self.collision_offset_x = 2  # 居中
        self.collision_offset_y = PLAYER_HEIGHT - self.collision_height  # 从头顶下移，使底部保持对齐
        
        # 更新碰撞矩形尺寸
        self.rect.width = self.collision_width
        self.rect.height = self.collision_height
        
        self.color = color
        self.player_id = player_id  # 玩家ID（1=WASD, 2=方向键）
        self.two_player_mode = two_player_mode  # 是否双人模式（双人模式不加载存档能力）
        self.state = PlayerState.SMALL
        
        # 跳跃状态
        self.is_jumping = False
        self.can_jump = True
        self.jump_held = False
        self.jump_timer = 0.0
        self.max_jump_time = 0.25  # 最大跳跃持续时间
        
        # 无敌状态
        self.invincible_timer = 0.0
        self.hurt_timer = 0.0
        self.base_hurt_invincible_duration = 2.0  # 受伤后无敌时间基础值
        self.base_star_invincible_duration = 10.0  # 星星无敌时间基础值
        
        # 动画速度 - 降低速度使动画更自然
        self.animation_speed = 6.0
        
        # AI辅助生成: Roguelike能力系统
        # 特殊能力状态
        self.has_double_jump = False
        self.has_dash = False
        self.has_wall_jump = False
        self.has_ground_pound = False
        
        # 二段跳状态
        self.double_jump_used = False
        self.air_jumps_remaining = 0
        
        # 冲刺状态
        self.is_dashing = False
        self.dash_timer = 0.0
        self.dash_cooldown = 0.0
        self.dash_duration = 0.15  # 冲刺持续时间
        self.dash_cooldown_time = 0.8  # 冲刺冷却时间
        self.dash_speed = 15.0  # 冲刺速度
        
        # 下砸状态
        self.is_ground_pounding = False
        self.ground_pound_speed = 20.0
        
        # 踢墙跳状态
        self.wall_slide_speed = 2.0  # 贴墙下滑速度
        self.is_wall_sliding = False
        self.wall_jump_power_x = 8.0  # 踢墙跳水平力
        self.wall_side = 0  # 贴墙方向 (-1=左墙, 1=右墙, 0=不贴墙)
        self.wall_jump_timer = 0.0  # 踢墙跳后短暂禁止转向的计时器
        
        # 玩家配置引用（用于灵敏度设置）
        self.player_config = PlayerConfig()
        
        # 加载存档中的能力
        self._load_abilities_from_save()
        
        # 加载精灵
        self._load_sprites()
        
        # 设置初始动画
        self.play_animation('idle')
    
    @property
    def hurt_invincible_duration(self) -> float:
        """获取受伤无敌时间（包含升级加成）"""
        return self.base_hurt_invincible_duration + self.player_config.extra_invincible_time
    
    @property
    def star_invincible_duration(self) -> float:
        """获取星星无敌时间（包含装备加成）"""
        base = self.base_star_invincible_duration
        return base * (1.0 + self.player_config.star_duration_bonus)
    
    def update_rect(self) -> None:
        """更新碰撞矩形位置（考虑偏移量）"""
        self.rect.x = int(self.x + self.collision_offset_x)
        self.rect.y = int(self.y + self.collision_offset_y)
    
    def _load_abilities_from_save(self) -> None:
        """
        从存档加载已解锁的能力
        AI辅助生成: Roguelike能力加载
        """
        # 双人模式不加载能力
        if self.two_player_mode:
            return
        
        save_manager = SaveManager()
        save_data = save_manager.get_current_save()
        
        if not save_data:
            return
        
        abilities = save_data.get('abilities', {})
        upgrades = save_data.get('upgrades', {})
        equipment = save_data.get('equipment', {})
        
        # 加载特殊能力
        self.has_double_jump = abilities.get('double_jump', False)
        self.has_dash = abilities.get('dash', False)
        self.has_wall_jump = abilities.get('wall_jump', False)
        self.has_ground_pound = abilities.get('ground_pound', False)
        
        # 应用升级和装备到配置
        self.player_config.apply_upgrades(upgrades)
        self.player_config.apply_equipment(equipment)
        
        # 加载配置中的灵敏度设置
        player_config_data = save_data.get('player_config', {})
        self.player_config.load_from_save(player_config_data)
    
    def _load_sprites(self) -> None:
        """
        加载玩家精灵
        
        AI辅助生成: 从资源管理器加载所有玩家精灵和动画
        """
        rm = ResourceManager()
        sprites = rm.load_player_sprites(self.color)
        
        # 设置动画
        self.add_animation('idle', [sprites['idle']])
        self.add_animation('run', sprites['run'])
        self.add_animation('jump', [sprites['jump']])
    
    def handle_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        """
        处理玩家输入
        AI辅助生成: 使用PlayerConfig的灵敏度设置，支持特殊能力
        支持惯性系统：按键加速，松开减速
        支持自定义按键绑定（单人模式）或固定按键（双人模式）
        
        Args:
            keys: Pygame按键状态
        """
        # 获取实际参数（应用灵敏度设置和升级加成）
        effective_speed = self.player_config.effective_move_speed
        effective_accel = self.player_config.effective_acceleration
        effective_jump = self.player_config.effective_jump_power
        
        # 根据是否在地面选择不同的摩擦系数
        if self.on_ground:
            effective_friction = self.player_config.effective_friction
        else:
            effective_friction = self.player_config.effective_air_friction
        
        # 根据玩家ID和游戏模式确定使用哪套按键
        # 单人模式：WASD + 方向键 都可以
        # 双人模式：玩家1用WASD，玩家2用方向键
        if not self.two_player_mode:
            # 单人模式：两套按键都可以用
            left_pressed = keys[pygame.K_a] or keys[pygame.K_LEFT]
            right_pressed = keys[pygame.K_d] or keys[pygame.K_RIGHT]
            jump_pressed = keys[pygame.K_w] or keys[pygame.K_SPACE] or keys[pygame.K_UP]
            down_pressed = keys[pygame.K_s] or keys[pygame.K_DOWN]
            dash_pressed = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        elif self.player_id == 1:
            # 双人模式 玩家1: WASD + 左Shift冲刺
            left_pressed = keys[pygame.K_a]
            right_pressed = keys[pygame.K_d]
            jump_pressed = keys[pygame.K_w] or keys[pygame.K_SPACE]
            down_pressed = keys[pygame.K_s]
            dash_pressed = keys[pygame.K_LSHIFT]
        else:  # player_id == 2
            # 双人模式 玩家2: 方向键 + 右Shift冲刺
            left_pressed = keys[pygame.K_LEFT]
            right_pressed = keys[pygame.K_RIGHT]
            jump_pressed = keys[pygame.K_UP]
            down_pressed = keys[pygame.K_DOWN]
            dash_pressed = keys[pygame.K_RSHIFT]
        
        # 左右移动（使用加速度实现惯性）- 即使在冲刺中也要记录移动意图
        moving = False
        move_direction = 0
        if left_pressed:
            move_direction = -1
            self.facing_right = False
            moving = True
        elif right_pressed:
            move_direction = 1
            self.facing_right = True
            moving = True
        
        # 如果正在冲刺，跳过移动处理但不跳过跳跃
        if not self.is_dashing:
            if moving:
                self.velocity_x += effective_accel * move_direction
            
            # 限制最大速度
            if abs(self.velocity_x) > effective_speed:
                self.velocity_x = effective_speed if self.velocity_x > 0 else -effective_speed
            
            # 没有按键时应用摩擦力减速
            if not moving:
                self.velocity_x *= effective_friction
                if abs(self.velocity_x) < 0.1:
                    self.velocity_x = 0
        
        # 落地时重置跳跃能力
        if self.on_ground:
            self.can_jump = True
            if self.has_double_jump:
                self.air_jumps_remaining = 1
        
        if jump_pressed:
            if self.on_ground and self.can_jump:
                # 地面跳跃
                self._perform_jump(effective_jump)
            elif self.has_double_jump and not self.on_ground and self.air_jumps_remaining > 0 and not self.jump_held:
                # 二段跳 - 需要松开再按才能触发（不检查can_jump，用air_jumps_remaining控制）
                self._perform_jump(effective_jump * 0.85)  # 二段跳力度稍弱
                self.air_jumps_remaining -= 1
                self.jump_held = True  # 防止连续触发
            elif self.has_wall_jump and self.is_wall_sliding and not self.jump_held:
                # 踢墙跳
                self._perform_wall_jump()
                self.jump_held = True
            elif self.is_jumping and self.jump_held:
                # 持续按住跳跃键可以跳得更高（只在第一次跳跃时有效）
                if self.jump_timer < self.max_jump_time and self.velocity_y < 0:
                    self.velocity_y = effective_jump * (1 - self.jump_timer / self.max_jump_time * 0.5)
        else:
            self.jump_held = False
        
        # 冲刺
        if self.has_dash and dash_pressed:
            self._try_dash()
        
        # 下砸（下键，在空中时）
        if self.has_ground_pound and not self.on_ground and down_pressed:
            self._start_ground_pound()
    
    def _perform_jump(self, jump_power: float) -> None:
        """执行跳跃"""
        self.velocity_y = jump_power
        self.is_jumping = True
        self.can_jump = False
        self.jump_held = True
        self.jump_timer = 0.0
        self.on_ground = False
        EventSystem().emit(GameEvent.PLAYER_JUMP)
    
    def _try_dash(self) -> None:
        """尝试冲刺"""
        if self.dash_cooldown > 0 or self.is_dashing:
            return
        
        self.is_dashing = True
        self.dash_timer = self.dash_duration
        
        # 冲刺方向
        direction = 1 if self.facing_right else -1
        self.velocity_x = self.dash_speed * direction
        self.velocity_y = 0  # 冲刺时不受重力
    
    def _start_ground_pound(self) -> None:
        """开始下砸"""
        if self.is_ground_pounding:
            return
        
        self.is_ground_pounding = True
        self.velocity_x = 0
        self.velocity_y = self.ground_pound_speed
    
    def _perform_wall_jump(self) -> None:
        """执行踢墙跳"""
        effective_jump = self.player_config.effective_jump_power
        
        # 垂直跳跃
        self.velocity_y = effective_jump * 0.9
        
        # 水平推力（离开墙壁的方向）
        self.velocity_x = self.wall_jump_power_x * (-self.wall_side)
        
        # 更新朝向
        self.facing_right = self.wall_side < 0
        
        # 设置状态
        self.is_jumping = True
        self.can_jump = False
        self.is_wall_sliding = False
        self.wall_jump_timer = 0.15  # 短暂禁止转向
        
        EventSystem().emit(GameEvent.PLAYER_JUMP)
    
    def update(self, dt: float) -> None:
        """
        更新玩家状态
        AI辅助生成: 添加冲刺和下砸计时器处理
        
        Args:
            dt: 时间增量（秒）
        """
        if not self.active:
            return
        
        # 更新跳跃计时器
        if self.is_jumping and self.jump_held:
            self.jump_timer += dt
        
        # 更新冲刺状态
        if self.is_dashing:
            self.dash_timer -= dt
            if self.dash_timer <= 0:
                self.is_dashing = False
                self.dash_cooldown = self.dash_cooldown_time
        
        # 更新冲刺冷却
        if self.dash_cooldown > 0:
            self.dash_cooldown -= dt
        
        # 更新踢墙跳计时器
        if self.wall_jump_timer > 0:
            self.wall_jump_timer -= dt
        
        # 应用重力
        if not self.is_dashing:
            if self.on_ground:
                # 在地面上时，不应用重力，速度归零
                if self.velocity_y > 0:
                    self.velocity_y = 0
            elif self.is_wall_sliding and self.velocity_y > 0:
                # 贴墙下滑时减缓下落速度
                self.velocity_y = min(self.velocity_y, self.wall_slide_speed)
            else:
                # 空中时正常应用重力
                self.velocity_y += GRAVITY
                if self.velocity_y > MAX_FALL_SPEED:
                    self.velocity_y = MAX_FALL_SPEED
        
        # 更新位置
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # 更新碰撞矩形
        self.update_rect()
        
        # 更新无敌计时器
        if self.invincible_timer > 0:
            self.invincible_timer -= dt
            if self.invincible_timer <= 0:
                self.state = PlayerState.SMALL if self.state == PlayerState.INVINCIBLE else self.state
        
        if self.hurt_timer > 0:
            self.hurt_timer -= dt
        
        # 更新动画
        self._update_animation_state()
        self.update_animation(dt)
    
    def _update_animation_state(self) -> None:
        """根据当前状态更新动画"""
        if not self.on_ground:
            self.play_animation('jump')
        elif abs(self.velocity_x) > 0.8:
            # 速度较大时切换到跑步动画
            self.play_animation('run')
        elif abs(self.velocity_x) < 0.2:
            # 速度很小时切换到站立动画（使用较低阈值避免来回切换）
            self.play_animation('idle')
        # 速度在0.2-0.8之间时保持当前动画，避免频繁切换
    
    def apply_collision(self, tiles: List[pygame.Rect], level_width: int, level_height: int) -> None:
        """
        应用碰撞检测和响应
        
        AI辅助生成: 实现AABB碰撞检测，我修改了分离轴检测逻辑以提高准确性
        
        Args:
            tiles: 碰撞瓦片列表
            level_width: 关卡宽度（像素）
            level_height: 关卡高度（像素）
        """
        # 边界检测
        if self.x < 0:
            self.x = 0
            self.velocity_x = 0
        elif self.x + self.width > level_width:
            self.x = level_width - self.width
            self.velocity_x = 0
        
        # 保存之前的状态
        was_on_ground = self.on_ground
        self.on_ground = False
        
        # 踢墙跳: 重置贴墙状态
        self.wall_side = 0
        self.is_wall_sliding = False
        
        # 与瓦片碰撞检测
        self.update_rect()
        
        # 首先检查是否站在地面上（使用稍微扩展的检测区域）
        feet_rect = pygame.Rect(self.rect.x + 2, self.rect.bottom, self.rect.width - 4, 2)
        for tile in tiles:
            if feet_rect.colliderect(tile):
                # 站在地面上
                self.on_ground = True
                self.is_jumping = False
                # 确保精确对齐到地面（考虑碰撞偏移）
                if abs(self.rect.bottom - tile.top) <= 2:
                    self.y = tile.top - self.collision_offset_y - self.collision_height
                    self.velocity_y = 0
                break
        
        # 然后处理碰撞
        self.update_rect()
        for tile in tiles:
            if not self.rect.colliderect(tile):
                continue
            
            # 计算重叠量
            overlap_left = self.rect.right - tile.left
            overlap_right = tile.right - self.rect.left
            overlap_top = self.rect.bottom - tile.top
            overlap_bottom = tile.bottom - self.rect.top
            
            # 找出最小重叠方向
            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
            
            if min_overlap == overlap_top and self.velocity_y >= 0:
                # 从上方碰撞（落地）- 考虑碰撞偏移
                self.y = tile.top - self.collision_offset_y - self.collision_height
                self.velocity_y = 0
                self.on_ground = True
                self.is_jumping = False
            elif min_overlap == overlap_bottom and self.velocity_y < 0:
                # 从下方碰撞（顶头）- 考虑碰撞偏移
                self.y = tile.bottom - self.collision_offset_y
                self.velocity_y = 0
            elif min_overlap == overlap_left and self.velocity_x > 0:
                # 从左侧碰撞（撞到右边的墙）- 考虑碰撞偏移
                self.x = tile.left - self.collision_offset_x - self.collision_width
                self.velocity_x = 0
                # 踢墙跳检测
                if self.has_wall_jump and not self.on_ground and self.velocity_y >= 0:
                    self.wall_side = 1  # 墙在右边
                    self.is_wall_sliding = True
            elif min_overlap == overlap_right and self.velocity_x < 0:
                # 从右侧碰撞（撞到左边的墙）- 考虑碰撞偏移
                self.x = tile.right - self.collision_offset_x
                self.velocity_x = 0
                # 踢墙跳检测
                if self.has_wall_jump and not self.on_ground and self.velocity_y >= 0:
                    self.wall_side = -1  # 墙在左边
                    self.is_wall_sliding = True
            
            self.update_rect()
        
        # 掉出底部判定死亡
        if self.y > level_height:
            self.die()
        
        # 落地事件
        if self.on_ground and not was_on_ground:
            EventSystem().emit(GameEvent.PLAYER_LAND)
            
            # AI辅助生成: 落地时重置特殊能力状态
            # 重置下砸
            self.is_ground_pounding = False
            
            # 重置二段跳
            if self.has_double_jump:
                self.air_jumps_remaining = 1
            
            # 重置贴墙状态
            self.is_wall_sliding = False
            self.wall_side = 0
    
    def take_damage(self) -> bool:
        """
        玩家受到伤害
        
        Returns:
            是否死亡
        """
        # 无敌状态不受伤
        if self.hurt_timer > 0 or self.state == PlayerState.INVINCIBLE:
            return False
        
        # 安全帽效果：有概率抵挡伤害
        damage_reduction = self.player_config.damage_reduction
        if damage_reduction > 0:
            import random
            if random.random() < damage_reduction:
                # 成功抵挡伤害，进入短暂无敌
                self.hurt_timer = 1.0
                EventSystem().emit(GameEvent.PLAYER_DAMAGE)
                return False
        
        if self.state == PlayerState.BIG:
            # 大状态变小
            self.state = PlayerState.SMALL
            self.hurt_timer = self.hurt_invincible_duration
            EventSystem().emit(GameEvent.PLAYER_DAMAGE)
            return False
        else:
            # 小状态直接死亡
            self.die()
            return True
    
    def die(self) -> None:
        """玩家死亡"""
        self.active = False
        EventSystem().emit(GameEvent.PLAYER_DEATH, {'player': self})
    
    def power_up(self) -> None:
        """吃到蘑菇变大"""
        if self.state == PlayerState.SMALL:
            self.state = PlayerState.BIG
            EventSystem().emit(GameEvent.PLAYER_POWER_UP)
    
    def become_invincible(self) -> None:
        """吃到星星变无敌"""
        self.state = PlayerState.INVINCIBLE
        self.invincible_timer = self.star_invincible_duration
        EventSystem().emit(GameEvent.PLAYER_INVINCIBLE)
    
    def is_invincible(self) -> bool:
        """检查是否处于无敌状态"""
        return self.state == PlayerState.INVINCIBLE or self.hurt_timer > 0
    
    def stomp_enemy(self) -> None:
        """踩敌人后的反弹"""
        self.velocity_y = JUMP_POWER * 0.6  # 小跳
        self.is_jumping = True
        # 踩踏后给予短暂无敌时间，防止踩踏重叠的怪物时受伤
        if self.hurt_timer < 0.15:
            self.hurt_timer = 0.15
    
    def render(self, screen: pygame.Surface, camera_offset: tuple = (0, 0)) -> None:
        """
        渲染玩家
        
        重写渲染方法以实现受伤闪烁效果，并正确显示碰撞框
        """
        if not self.active:
            return
        
        # 受伤闪烁效果
        if self.hurt_timer > 0:
            if int(self.hurt_timer * 10) % 2 == 0:
                return  # 跳过渲染实现闪烁
        
        # 无敌闪烁效果（更快）
        if self.state == PlayerState.INVINCIBLE:
            if int(self.invincible_timer * 20) % 2 == 0:
                # 使用金色滤镜效果
                pass  # TODO: 可以添加颜色滤镜
        
        # 调用父类渲染
        super().render(screen, camera_offset)
    
    def reset(self, x: float, y: float) -> None:
        """
        重置玩家状态
        
        Args:
            x: 新的X坐标
            y: 新的Y坐标
        """
        self.x = x
        self.y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.state = PlayerState.SMALL
        self.invincible_timer = 0
        self.hurt_timer = 0
        self.is_jumping = False
        self.on_ground = False
        self.active = True
        self.facing_right = True
        self.update_rect()
