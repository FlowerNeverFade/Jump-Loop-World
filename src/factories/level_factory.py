"""
关卡工厂模块
AI辅助生成: 实现工厂模式创建关卡

此模块提供LevelFactory类，根据难度和配置创建关卡。

设计模式: 工厂模式 (Factory Pattern)
"""

from typing import Dict, Any, Optional

from ..levels.level import Level
from ..settings import DifficultySettings


class LevelFactory:
    """
    关卡工厂类
    
    根据难度设置创建配置好的关卡实例。
    
    使用示例:
        factory = LevelFactory()
        level = factory.create_level('easy')
    """
    
    def __init__(self):
        """初始化关卡工厂"""
        pass
    
    def create_level(self, difficulty: str = 'easy', level_id: int = 1) -> Level:
        """
        创建关卡
        
        Args:
            difficulty: 难度 ('easy' 或 'hard')
            level_id: 关卡ID
            
        Returns:
            配置好的关卡实例
        """
        # 获取难度配置
        if difficulty == 'easy':
            diff_settings = DifficultySettings.EASY
        elif difficulty == 'hard':
            diff_settings = DifficultySettings.HARD
        else:
            print(f"未知难度 '{difficulty}'，使用简单模式")
            diff_settings = DifficultySettings.EASY
        
        # 创建关卡
        level = Level(diff_settings)
        
        # 加载关卡数据
        # 目前使用默认生成的关卡
        level.load_default_level()
        
        return level
    
    def create_from_file(self, filename: str, difficulty: str = 'easy') -> Optional[Level]:
        """
        从文件创建关卡
        
        AI辅助生成: 预留从JSON文件加载关卡的接口
        
        Args:
            filename: 关卡文件名
            difficulty: 难度
            
        Returns:
            关卡实例，加载失败返回None
        """
        # 获取难度配置
        if difficulty == 'easy':
            diff_settings = DifficultySettings.EASY
        else:
            diff_settings = DifficultySettings.HARD
        
        level = Level(diff_settings)
        
        # TODO: 实现从文件加载关卡
        # 目前使用默认关卡
        level.load_default_level()
        
        return level
