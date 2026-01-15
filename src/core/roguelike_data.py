"""
Roguelike数据模型模块
AI辅助生成: 定义升级、装备和商店物品的数据结构

此模块包含所有Roguelike元游戏相关的数据定义。
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum, auto


class UpgradeType(Enum):
    """升级类型枚举"""
    MAX_HEALTH = auto()      # 生命值上限
    MOVE_SPEED = auto()      # 移动速度
    JUMP_HEIGHT = auto()     # 跳跃高度
    COIN_MAGNET = auto()     # 金币吸引范围
    INVINCIBLE_TIME = auto() # 无敌时间延长


class AbilityType(Enum):
    """特殊能力类型枚举"""
    DOUBLE_JUMP = auto()    # 二段跳
    DASH = auto()           # 冲刺
    WALL_JUMP = auto()      # 踢墙跳
    GROUND_POUND = auto()   # 下砸


class EquipmentSlot(Enum):
    """装备槽位枚举"""
    HAT = auto()       # 帽子
    BOOTS = auto()     # 靴子
    ACCESSORY = auto() # 饰品


@dataclass
class UpgradeDefinition:
    """
    升级定义数据类
    
    Attributes:
        id: 升级ID
        name: 显示名称
        description: 描述
        max_level: 最大等级
        base_cost: 基础价格
        cost_multiplier: 每级价格倍率
        effect_per_level: 每级效果值
    """
    id: str
    name: str
    description: str
    max_level: int
    base_cost: int
    cost_multiplier: float = 1.5
    effect_per_level: float = 0.05
    
    def get_cost(self, current_level: int) -> int:
        """获取升级到下一级的花费"""
        if current_level >= self.max_level:
            return -1  # 已满级
        return int(self.base_cost * (self.cost_multiplier ** current_level))
    
    def get_total_effect(self, level: int) -> float:
        """获取当前等级的总效果"""
        return self.effect_per_level * level


@dataclass
class AbilityDefinition:
    """
    特殊能力定义数据类
    
    Attributes:
        id: 能力ID
        name: 显示名称
        description: 描述
        cost: 解锁价格
        icon: 图标名称
    """
    id: str
    name: str
    description: str
    cost: int
    icon: str = ""


@dataclass
class EquipmentDefinition:
    """
    装备定义数据类
    
    Attributes:
        id: 装备ID
        name: 显示名称
        description: 描述
        slot: 装备槽位
        cost: 购买价格
        effects: 效果字典
    """
    id: str
    name: str
    description: str
    slot: EquipmentSlot
    cost: int
    effects: Dict[str, float] = field(default_factory=dict)


class RoguelikeData:
    """
    Roguelike数据管理类
    
    存储所有升级、能力和装备的定义数据。
    作为游戏的数据仓库使用。
    """
    
    # ==================== 升级定义 ====================
    UPGRADES: Dict[str, UpgradeDefinition] = {
        'max_health': UpgradeDefinition(
            id='max_health',
            name='生命强化',
            description='增加最大生命值',
            max_level=5,
            base_cost=100,
            cost_multiplier=1.8,
            effect_per_level=1.0  # 每级+1生命
        ),
        'move_speed': UpgradeDefinition(
            id='move_speed',
            name='疾风步',
            description='提升移动速度',
            max_level=5,
            base_cost=150,
            cost_multiplier=1.6,
            effect_per_level=0.05  # 每级+5%速度
        ),
        'jump_height': UpgradeDefinition(
            id='jump_height',
            name='弹跳力',
            description='增加跳跃高度',
            max_level=5,
            base_cost=150,
            cost_multiplier=1.6,
            effect_per_level=0.03  # 每级+3%跳跃力
        ),
        'coin_magnet': UpgradeDefinition(
            id='coin_magnet',
            name='金币磁铁',
            description='增加金币自动吸引范围',
            max_level=3,
            base_cost=200,
            cost_multiplier=2.0,
            effect_per_level=32.0  # 每级+32像素范围
        ),
        'invincible_time': UpgradeDefinition(
            id='invincible_time',
            name='护盾延长',
            description='受伤后无敌时间延长',
            max_level=3,
            base_cost=250,
            cost_multiplier=2.0,
            effect_per_level=0.5  # 每级+0.5秒
        ),
    }
    
    # ==================== 特殊能力定义 ====================
    ABILITIES: Dict[str, AbilityDefinition] = {
        'double_jump': AbilityDefinition(
            id='double_jump',
            name='二段跳',
            description='在空中可以再次跳跃',
            cost=500,
            icon='double_jump'
        ),
        'dash': AbilityDefinition(
            id='dash',
            name='冲刺',
            description='按Alt键快速冲刺一小段距离',
            cost=600,
            icon='dash'
        ),
        'wall_jump': AbilityDefinition(
            id='wall_jump',
            name='踢墙跳',
            description='接触墙壁时可以蹬墙跳跃',
            cost=800,
            icon='wall_jump'
        ),
        'ground_pound': AbilityDefinition(
            id='ground_pound',
            name='下砸',
            description='在空中按下键快速下落并砸碎砖块',
            cost=700,
            icon='ground_pound'
        ),
    }
    
    # ==================== 装备定义 ====================
    EQUIPMENT: Dict[str, EquipmentDefinition] = {
        # 帽子
        'lucky_hat': EquipmentDefinition(
            id='lucky_hat',
            name='幸运帽',
            description='增加金币掉落数量',
            slot=EquipmentSlot.HAT,
            cost=300,
            effects={'coin_bonus': 0.25}  # 金币+25%
        ),
        'hard_hat': EquipmentDefinition(
            id='hard_hat',
            name='安全帽',
            description='减少受到的伤害',
            slot=EquipmentSlot.HAT,
            cost=400,
            effects={'damage_reduction': 0.2}  # 伤害减少20%
        ),
        
        # 靴子
        'speed_boots': EquipmentDefinition(
            id='speed_boots',
            name='疾风靴',
            description='大幅提升移动速度',
            slot=EquipmentSlot.BOOTS,
            cost=350,
            effects={'speed_bonus': 0.15}  # 速度+15%
        ),
        'jump_boots': EquipmentDefinition(
            id='jump_boots',
            name='弹簧靴',
            description='提升跳跃高度',
            slot=EquipmentSlot.BOOTS,
            cost=350,
            effects={'jump_bonus': 0.10}  # 跳跃+10%
        ),
        'feather_boots': EquipmentDefinition(
            id='feather_boots',
            name='羽毛靴',
            description='大幅提升跳跃高度，略微提升速度',
            slot=EquipmentSlot.BOOTS,
            cost=500,
            effects={'jump_bonus': 0.20, 'speed_bonus': 0.05}
        ),
        
        # 饰品
        'speed_charm': EquipmentDefinition(
            id='speed_charm',
            name='速度护符',
            description='轻微提升移动速度',
            slot=EquipmentSlot.ACCESSORY,
            cost=200,
            effects={'speed_bonus': 0.10}
        ),
        'jump_charm': EquipmentDefinition(
            id='jump_charm',
            name='弹跳护符',
            description='轻微提升跳跃高度',
            slot=EquipmentSlot.ACCESSORY,
            cost=200,
            effects={'jump_bonus': 0.08}
        ),
        'coin_charm': EquipmentDefinition(
            id='coin_charm',
            name='聚财护符',
            description='金币掉落数量小幅增加',
            slot=EquipmentSlot.ACCESSORY,
            cost=250,
            effects={'coin_bonus': 0.15}
        ),
        'star_charm': EquipmentDefinition(
            id='star_charm',
            name='星星护符',
            description='星星效果持续时间延长',
            slot=EquipmentSlot.ACCESSORY,
            cost=400,
            effects={'star_duration': 0.50}  # +50%持续时间
        ),
    }
    
    @classmethod
    def get_upgrade(cls, upgrade_id: str) -> Optional[UpgradeDefinition]:
        """获取升级定义"""
        return cls.UPGRADES.get(upgrade_id)
    
    @classmethod
    def get_ability(cls, ability_id: str) -> Optional[AbilityDefinition]:
        """获取能力定义"""
        return cls.ABILITIES.get(ability_id)
    
    @classmethod
    def get_equipment(cls, equipment_id: str) -> Optional[EquipmentDefinition]:
        """获取装备定义"""
        return cls.EQUIPMENT.get(equipment_id)
    
    @classmethod
    def get_all_upgrades(cls) -> List[UpgradeDefinition]:
        """获取所有升级"""
        return list(cls.UPGRADES.values())
    
    @classmethod
    def get_all_abilities(cls) -> List[AbilityDefinition]:
        """获取所有能力"""
        return list(cls.ABILITIES.values())
    
    @classmethod
    def get_all_equipment(cls) -> List[EquipmentDefinition]:
        """获取所有装备"""
        return list(cls.EQUIPMENT.values())
    
    @classmethod
    def get_equipment_by_slot(cls, slot: EquipmentSlot) -> List[EquipmentDefinition]:
        """获取指定槽位的所有装备"""
        return [e for e in cls.EQUIPMENT.values() if e.slot == slot]


# ==================== 商店分类 ====================
class ShopCategory(Enum):
    """商店分类"""
    UPGRADES = auto()   # 升级
    ABILITIES = auto()  # 能力
    EQUIPMENT = auto()  # 装备


@dataclass
class ShopItem:
    """
    商店物品数据类
    
    用于在商店UI中显示物品信息。
    """
    item_id: str
    name: str
    description: str
    cost: int
    category: ShopCategory
    is_purchased: bool = False
    current_level: int = 0
    max_level: int = 1
    
    @property
    def can_purchase(self) -> bool:
        """是否可以购买"""
        if self.category == ShopCategory.UPGRADES:
            return self.current_level < self.max_level
        else:
            return not self.is_purchased
    
    @property
    def display_cost(self) -> str:
        """显示的价格文本"""
        if not self.can_purchase:
            return "已购买" if self.is_purchased else "已满级"
        return f"{self.cost} 金币"
