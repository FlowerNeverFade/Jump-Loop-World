"""
金币模块
AI辅助生成: 实现金币道具

金币是最常见的收集品，收集100个可以获得额外生命。
"""

import math
from typing import TYPE_CHECKING

from .item import Item
from ...settings import TILE_SIZE
from ...core.resource_manager import ResourceManager
from ...core.event_system import EventSystem, GameEvent
from ...core.player_config import PlayerConfig

if TYPE_CHECKING:
    from ..player import Player


class Coin(Item):
    """
    金币类
    
    游戏中最常见的收集品，有旋转动画。
    收集100个金币可以获得1UP（额外生命）。
    
    Attributes:
        在Item基类基础上无额外属性
    """
    
    def __init__(self, x: float, y: float):
        """
        初始化金币
        
        Args:
            x: X坐标
            y: Y坐标
        """
        super().__init__(x, y, 24, 24)
        
        self.score_value = 200
        self.auto_collect = True
        self.moves = False
        
        # 动画速度（旋转速度）
        self.animation_speed = 8.0
        
        # 磁铁吸引状态
        self.being_attracted = False
        self.attract_speed = 8.0  # 吸引速度
        
        # 加载精灵
        self._load_sprites()
        
        # 开始旋转动画
        self.play_animation('spin')
    
    def _load_sprites(self) -> None:
        """加载金币精灵"""
        rm = ResourceManager()
        items = rm.load_item_sprites()
        
        self.add_animation('spin', items['coin'])
    
    def update_magnet(self, player_x: float, player_y: float, magnet_range: float) -> None:
        """
        更新磁铁吸引效果
        
        Args:
            player_x: 玩家X坐标
            player_y: 玩家Y坐标
            magnet_range: 吸引范围
        """
        if self.collected or not self.active:
            return
        
        if magnet_range <= 0:
            return
        
        # 计算到玩家的距离
        coin_center_x = self.x + self.width / 2
        coin_center_y = self.y + self.height / 2
        
        dx = player_x - coin_center_x
        dy = player_y - coin_center_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < magnet_range and distance > 0:
            # 在吸引范围内，向玩家移动
            self.being_attracted = True
            # 归一化方向并移动
            speed = self.attract_speed * (1 + (magnet_range - distance) / magnet_range)
            self.x += (dx / distance) * speed
            self.y += (dy / distance) * speed
            self.update_rect()
        else:
            self.being_attracted = False
    
    def _apply_effect(self, player: 'Player') -> None:
        """收集金币效果"""
        # 获取金币加成
        config = PlayerConfig()
        coin_bonus = config.coin_bonus
        
        # 计算实际金币数量（有加成时可能获得额外金币）
        coin_value = 1
        if coin_bonus > 0:
            # 有概率获得额外金币
            import random
            if random.random() < coin_bonus:
                coin_value = 2
        
        # 发送金币收集事件
        EventSystem().emit(GameEvent.COIN_COLLECT, {'value': coin_value})


class BlockCoin(Coin):
    """
    从方块弹出的金币
    
    与普通金币不同，这种金币会向上弹出然后消失。
    """
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        
        # 弹出动画参数
        self.popup_velocity = -8
        self.velocity_y = self.popup_velocity
        self.popup_timer = 0.0
        self.popup_duration = 0.5
        self.popping = True
    
    def update(self, dt: float) -> None:
        """更新弹出金币"""
        if self.popping:
            self.popup_timer += dt
            self.velocity_y += 0.5  # 重力
            self.y += self.velocity_y
            
            if self.popup_timer >= self.popup_duration:
                # 自动收集
                self.collected = True
                self.active = False
                EventSystem().emit(GameEvent.COIN_COLLECT, {'value': 1})
            
            self.update_rect()
            self.update_animation(dt)
        else:
            super().update(dt)
