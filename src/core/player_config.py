"""
玩家配置模块
AI辅助生成: 管理玩家的灵敏度设置和游戏参数

此模块提供运行时可调节的玩家配置，包括移动速度、摩擦力、跳跃力度等。
配置会自动与存档系统同步。
"""

from typing import Optional, Dict, Any
from ..settings import PLAYER_SPEED, PLAYER_ACCELERATION, FRICTION, AIR_FRICTION, JUMP_POWER, GRAVITY


class PlayerConfig:
    """
    玩家配置类（单例）
    
    管理玩家的灵敏度设置，允许在游戏中实时调节。
    配置数据会保存到存档中。
    
    Attributes:
        move_speed_multiplier: 移动速度倍率 (0.5 - 2.0)
        friction_multiplier: 摩擦力倍率 (0.5 - 2.0)，值越高越滑
        jump_power_multiplier: 跳跃力倍率 (0.5 - 1.5)
    """
    
    _instance = None
    
    # 参数范围定义
    PARAM_RANGES = {
        'move_speed_multiplier': {'min': 0.5, 'max': 2.0, 'default': 1.0, 'step': 0.1},
        'friction_multiplier': {'min': 0.5, 'max': 2.0, 'default': 1.0, 'step': 0.1},
        'jump_power_multiplier': {'min': 0.5, 'max': 1.5, 'default': 1.0, 'step': 0.1},
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        
        # 灵敏度设置（倍率）
        self._move_speed_multiplier = 1.0
        self._friction_multiplier = 1.0
        self._jump_power_multiplier = 1.0
        
        # 升级加成
        self._upgrade_speed_bonus = 0.0
        self._upgrade_jump_bonus = 0.0
        self._upgrade_max_health = 0  # 额外生命数
        self._upgrade_coin_magnet = 0.0  # 金币吸引范围
        self._upgrade_invincible_time = 0.0  # 额外无敌时间
        
        # 装备加成
        self._equipment_speed_bonus = 0.0
        self._equipment_jump_bonus = 0.0
        self._equipment_coin_bonus = 0.0  # 金币数量加成
        self._equipment_damage_reduction = 0.0  # 伤害减免
        self._equipment_star_duration = 0.0  # 星星持续时间加成
    
    def reset_bonuses(self) -> None:
        """重置所有升级和装备加成（用于双人模式等不需要加成的场景）"""
        # 重置升级加成
        self._upgrade_speed_bonus = 0.0
        self._upgrade_jump_bonus = 0.0
        self._upgrade_max_health = 0
        self._upgrade_coin_magnet = 0.0
        self._upgrade_invincible_time = 0.0
        
        # 重置装备加成
        self._equipment_speed_bonus = 0.0
        self._equipment_jump_bonus = 0.0
        self._equipment_coin_bonus = 0.0
        self._equipment_damage_reduction = 0.0
        self._equipment_star_duration = 0.0
        
        # 重置灵敏度为默认值
        self._move_speed_multiplier = 1.0
        self._friction_multiplier = 1.0
        self._jump_power_multiplier = 1.0
    
    # ==================== 属性访问器 ====================
    
    @property
    def move_speed_multiplier(self) -> float:
        return self._move_speed_multiplier
    
    @move_speed_multiplier.setter
    def move_speed_multiplier(self, value: float) -> None:
        params = self.PARAM_RANGES['move_speed_multiplier']
        self._move_speed_multiplier = max(params['min'], min(params['max'], value))
    
    @property
    def friction_multiplier(self) -> float:
        return self._friction_multiplier
    
    @friction_multiplier.setter
    def friction_multiplier(self, value: float) -> None:
        params = self.PARAM_RANGES['friction_multiplier']
        self._friction_multiplier = max(params['min'], min(params['max'], value))
    
    @property
    def jump_power_multiplier(self) -> float:
        return self._jump_power_multiplier
    
    @jump_power_multiplier.setter
    def jump_power_multiplier(self, value: float) -> None:
        params = self.PARAM_RANGES['jump_power_multiplier']
        self._jump_power_multiplier = max(params['min'], min(params['max'], value))
    
    # ==================== 计算后的实际值 ====================
    
    @property
    def effective_move_speed(self) -> float:
        """获取实际移动速度（包含升级和装备加成）"""
        base = PLAYER_SPEED * self._move_speed_multiplier
        return base * (1.0 + self._upgrade_speed_bonus + self._equipment_speed_bonus)
    
    @property
    def effective_acceleration(self) -> float:
        """获取实际加速度（包含升级和装备加成）"""
        base = PLAYER_ACCELERATION * self._move_speed_multiplier
        return base * (1.0 + self._upgrade_speed_bonus + self._equipment_speed_bonus)
    
    @property
    def effective_friction(self) -> float:
        """
        获取实际摩擦系数（地面）
        摩擦力倍率越高，摩擦系数越接近1（越滑）
        """
        # 摩擦力范围: 0.7 (粘) 到 0.95 (滑)
        base_friction = FRICTION  # 0.85
        # multiplier = 1.0 时使用默认值
        # multiplier < 1.0 时更粘 (降低friction)
        # multiplier > 1.0 时更滑 (提高friction)
        adjusted = base_friction + (self._friction_multiplier - 1.0) * 0.1
        return max(0.7, min(0.95, adjusted))
    
    @property
    def effective_air_friction(self) -> float:
        """获取空中摩擦系数（空中控制较弱）"""
        base_friction = AIR_FRICTION  # 0.92
        adjusted = base_friction + (self._friction_multiplier - 1.0) * 0.05
        return max(0.85, min(0.98, adjusted))
    
    @property
    def effective_jump_power(self) -> float:
        """获取实际跳跃力（包含升级和装备加成）"""
        base = JUMP_POWER * self._jump_power_multiplier
        # 跳跃力是负值，所以加成需要让它更负
        bonus_multiplier = 1.0 + self._upgrade_jump_bonus + self._equipment_jump_bonus
        return base * bonus_multiplier
    
    @property
    def extra_lives(self) -> int:
        """获取额外生命数（生命强化升级）"""
        return self._upgrade_max_health
    
    @property
    def coin_magnet_range(self) -> float:
        """获取金币吸引范围（像素）"""
        return self._upgrade_coin_magnet
    
    @property
    def extra_invincible_time(self) -> float:
        """获取额外无敌时间（秒）"""
        return self._upgrade_invincible_time
    
    @property
    def coin_bonus(self) -> float:
        """获取金币收集加成（比例）"""
        return self._equipment_coin_bonus
    
    @property
    def damage_reduction(self) -> float:
        """获取伤害减免（比例）"""
        return self._equipment_damage_reduction
    
    @property
    def star_duration_bonus(self) -> float:
        """获取星星持续时间加成（比例）"""
        return self._equipment_star_duration
    
    # ==================== 升级和装备加成 ====================
    
    def apply_upgrades(self, upgrades: Dict[str, int]) -> None:
        """
        应用升级加成
        
        Args:
            upgrades: 升级等级字典
        """
        # 移动速度升级: 每级+5%
        speed_level = upgrades.get('move_speed', 0)
        self._upgrade_speed_bonus = speed_level * 0.05
        
        # 跳跃高度升级: 每级+3%
        jump_level = upgrades.get('jump_height', 0)
        self._upgrade_jump_bonus = jump_level * 0.03
        
        # 生命强化升级: 每级+1生命
        health_level = upgrades.get('max_health', 0)
        self._upgrade_max_health = health_level
        
        # 金币磁铁升级: 每级+32像素范围
        magnet_level = upgrades.get('coin_magnet', 0)
        self._upgrade_coin_magnet = magnet_level * 32.0
        
        # 护盾延长升级: 每级+0.5秒无敌时间
        invincible_level = upgrades.get('invincible_time', 0)
        self._upgrade_invincible_time = invincible_level * 0.5
    
    def apply_equipment(self, equipment: Dict[str, Optional[str]]) -> None:
        """
        应用装备加成
        
        Args:
            equipment: 装备字典
        """
        self._equipment_speed_bonus = 0.0
        self._equipment_jump_bonus = 0.0
        self._equipment_coin_bonus = 0.0
        self._equipment_damage_reduction = 0.0
        self._equipment_star_duration = 0.0
        
        # 帽子加成
        hat = equipment.get('hat')
        if hat == 'lucky_hat':
            self._equipment_coin_bonus += 0.25  # 金币+25%
        elif hat == 'hard_hat':
            self._equipment_damage_reduction += 0.2  # 伤害减少20%
        
        # 靴子加成
        boots = equipment.get('boots')
        if boots == 'speed_boots':
            self._equipment_speed_bonus += 0.15
        elif boots == 'jump_boots':
            self._equipment_jump_bonus += 0.10
        elif boots == 'feather_boots':
            self._equipment_jump_bonus += 0.20
            self._equipment_speed_bonus += 0.05
        
        # 饰品加成
        accessory = equipment.get('accessory')
        if accessory == 'speed_charm':
            self._equipment_speed_bonus += 0.10
        elif accessory == 'jump_charm':
            self._equipment_jump_bonus += 0.08
        elif accessory == 'coin_charm':
            self._equipment_coin_bonus += 0.15  # 金币+15%
        elif accessory == 'star_charm':
            self._equipment_star_duration += 0.50  # 星星时间+50%
    
    # ==================== 存档同步 ====================
    
    def load_from_save(self, config_data: Dict[str, Any]) -> None:
        """
        从存档数据加载配置
        
        Args:
            config_data: 存档中的player_config数据
        """
        if not config_data:
            return
        
        self.move_speed_multiplier = config_data.get('move_speed_multiplier', 1.0)
        self.friction_multiplier = config_data.get('friction_multiplier', 1.0)
        self.jump_power_multiplier = config_data.get('jump_power_multiplier', 1.0)
    
    def to_save_data(self) -> Dict[str, float]:
        """
        导出配置数据用于保存
        
        Returns:
            配置数据字典
        """
        return {
            'move_speed_multiplier': self._move_speed_multiplier,
            'friction_multiplier': self._friction_multiplier,
            'jump_power_multiplier': self._jump_power_multiplier,
        }
    
    def reset_to_defaults(self) -> None:
        """重置为默认值"""
        self._move_speed_multiplier = self.PARAM_RANGES['move_speed_multiplier']['default']
        self._friction_multiplier = self.PARAM_RANGES['friction_multiplier']['default']
        self._jump_power_multiplier = self.PARAM_RANGES['jump_power_multiplier']['default']
    
    # ==================== 辅助方法 ====================
    
    def get_param_info(self, param_name: str) -> Dict[str, float]:
        """获取参数信息（范围、当前值等）"""
        if param_name not in self.PARAM_RANGES:
            return {}
        
        info = self.PARAM_RANGES[param_name].copy()
        info['current'] = getattr(self, param_name)
        return info
    
    def get_all_params(self) -> Dict[str, Dict[str, float]]:
        """获取所有参数信息"""
        return {
            name: self.get_param_info(name)
            for name in self.PARAM_RANGES
        }
