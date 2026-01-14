"""
实体工厂模块
AI辅助生成: 实现工厂模式创建游戏实体

此模块提供EntityFactory类，根据类型创建不同的游戏实体。
工厂模式使得添加新实体类型时无需修改使用代码。

设计模式: 工厂模式 (Factory Pattern)
"""

from typing import Optional, Dict, Any, TYPE_CHECKING

from ..entities.player import Player
from ..entities.enemies.goomba import Goomba
from ..entities.enemies.koopa import Koopa
from ..entities.enemies.flapper import Flapper
from ..entities.items.coin import Coin
from ..entities.items.mushroom import Mushroom, Star
from ..settings import TILE_SIZE

if TYPE_CHECKING:
    from ..entities.enemies.enemy import Enemy
    from ..entities.items.item import Item


class EntityFactory:
    """
    实体工厂类
    
    使用工厂模式创建游戏实体，提供统一的创建接口。
    
    使用示例:
        factory = EntityFactory()
        enemy = factory.create_enemy('goomba', 100, 200)
        item = factory.create_item('coin', 150, 100)
    """
    
    # 敌人类型映射
    ENEMY_TYPES = {
        'goomba': Goomba,
        'mushling': Goomba,  # 别名
        'koopa': Koopa,
        'shellback': Koopa,  # 别名
        'flapper': Flapper,
    }
    
    # 道具类型映射
    ITEM_TYPES = {
        'coin': Coin,
        'mushroom': Mushroom,
        'star': Star,
    }
    
    def __init__(self, difficulty_multiplier: float = 1.0):
        """
        初始化工厂
        
        Args:
            difficulty_multiplier: 难度倍率（影响敌人速度等）
        """
        self.difficulty_multiplier = difficulty_multiplier
    
    def create_enemy(self, enemy_type: str, x: float, y: float, 
                     **kwargs) -> Optional['Enemy']:
        """
        创建敌人实体
        
        AI辅助生成: 工厂方法，根据类型创建对应的敌人实例
        
        Args:
            enemy_type: 敌人类型（'goomba', 'koopa', 'flapper'）
            x: X坐标
            y: Y坐标
            **kwargs: 额外参数
            
        Returns:
            敌人实例，如果类型无效返回None
        """
        enemy_type = enemy_type.lower()
        
        if enemy_type not in self.ENEMY_TYPES:
            print(f"警告: 未知的敌人类型 '{enemy_type}'")
            return None
        
        enemy_class = self.ENEMY_TYPES[enemy_type]
        
        try:
            enemy = enemy_class(x, y)
            enemy.apply_difficulty(self.difficulty_multiplier)
            return enemy
        except Exception as e:
            print(f"创建敌人失败: {e}")
            return None
    
    def create_item(self, item_type: str, x: float, y: float,
                    **kwargs) -> Optional['Item']:
        """
        创建道具实体
        
        Args:
            item_type: 道具类型（'coin', 'mushroom', 'star'）
            x: X坐标
            y: Y坐标
            **kwargs: 额外参数
            
        Returns:
            道具实例，如果类型无效返回None
        """
        item_type = item_type.lower()
        
        if item_type not in self.ITEM_TYPES:
            print(f"警告: 未知的道具类型 '{item_type}'")
            return None
        
        item_class = self.ITEM_TYPES[item_type]
        
        try:
            item = item_class(x, y)
            return item
        except Exception as e:
            print(f"创建道具失败: {e}")
            return None
    
    def create_player(self, x: float, y: float, color: str = 'red') -> Player:
        """
        创建玩家实体
        
        Args:
            x: X坐标
            y: Y坐标
            color: 玩家颜色
            
        Returns:
            玩家实例
        """
        return Player(x, y, color)
    
    def set_difficulty(self, multiplier: float) -> None:
        """
        设置难度倍率
        
        Args:
            multiplier: 难度倍率
        """
        self.difficulty_multiplier = multiplier
    
    @classmethod
    def get_enemy_types(cls) -> list:
        """获取所有支持的敌人类型"""
        return list(set(cls.ENEMY_TYPES.keys()))
    
    @classmethod
    def get_item_types(cls) -> list:
        """获取所有支持的道具类型"""
        return list(cls.ITEM_TYPES.keys())
