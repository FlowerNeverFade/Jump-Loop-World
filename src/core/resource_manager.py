"""
资源管理器模块
AI辅助生成: 实现单例模式的资源加载与缓存管理

此模块负责游戏资源的统一加载、缓存和管理，包括：
- 图像资源（精灵、背景）
- 动画资源
- 关卡数据

设计模式: 单例模式 (Singleton Pattern)
确保资源只被加载一次，避免重复加载导致的性能问题
"""

import pygame
import os
import json
from typing import Dict, Optional, List, Tuple, Any
from ..settings import SPRITES_DIR, LEVELS_DIR


class ResourceManager:
    """
    资源管理器类 - 单例模式实现
    
    统一管理游戏中所有资源的加载和缓存，避免重复加载。
    
    使用示例:
        rm = ResourceManager()
        player_sprite = rm.get_image('player/red_idle.png')
        level_data = rm.get_level('level_1')
    
    Attributes:
        _images: 图像资源缓存
        _animations: 动画资源缓存
        _levels: 关卡数据缓存
    """
    
    # 单例实例
    _instance = None
    
    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化资源管理器"""
        if self._initialized:
            return
        
        self._images: Dict[str, pygame.Surface] = {}
        self._animations: Dict[str, List[pygame.Surface]] = {}
        self._levels: Dict[str, Dict] = {}
        self._initialized = True
        
        # 默认占位图像（用于加载失败时）
        self._placeholder: Optional[pygame.Surface] = None
    
    def _create_placeholder(self, width: int = 32, height: int = 32) -> pygame.Surface:
        """
        创建占位图像（紫红色方块，表示资源缺失）
        
        AI辅助生成: 创建一个显眼的占位图像用于调试
        
        Args:
            width: 宽度
            height: 高度
            
        Returns:
            占位图像Surface
        """
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        # 紫红色棋盘格图案
        for y in range(height):
            for x in range(width):
                if (x // 4 + y // 4) % 2 == 0:
                    surface.set_at((x, y), (255, 0, 255, 255))
                else:
                    surface.set_at((x, y), (0, 0, 0, 255))
        return surface
    
    def get_placeholder(self, width: int = 32, height: int = 32) -> pygame.Surface:
        """获取占位图像"""
        return self._create_placeholder(width, height)
    
    def load_image(self, path: str, convert_alpha: bool = True) -> pygame.Surface:
        """
        加载图像文件
        
        Args:
            path: 图像文件路径（相对于sprites目录或绝对路径）
            convert_alpha: 是否转换为带alpha通道的格式
            
        Returns:
            加载的pygame.Surface对象
            
        Raises:
            记录警告并返回占位图像（不抛出异常以保证游戏继续运行）
        """
        # 检查缓存
        if path in self._images:
            return self._images[path]
        
        # 构建完整路径
        if os.path.isabs(path):
            full_path = path
        else:
            full_path = os.path.join(SPRITES_DIR, path)
        
        try:
            image = pygame.image.load(full_path)
            if convert_alpha:
                image = image.convert_alpha()
            else:
                image = image.convert()
            
            # 缓存图像
            self._images[path] = image
            return image
            
        except pygame.error as e:
            print(f"警告: 无法加载图像 '{full_path}': {e}")
            # 返回占位图像
            placeholder = self.get_placeholder()
            self._images[path] = placeholder
            return placeholder
        except FileNotFoundError:
            print(f"警告: 图像文件不存在 '{full_path}'")
            placeholder = self.get_placeholder()
            self._images[path] = placeholder
            return placeholder
    
    def get_image(self, path: str) -> pygame.Surface:
        """
        获取图像（如果未加载则自动加载）
        
        Args:
            path: 图像路径
            
        Returns:
            pygame.Surface对象
        """
        if path not in self._images:
            return self.load_image(path)
        return self._images[path]
    
    def load_animation(self, name: str, paths: List[str]) -> List[pygame.Surface]:
        """
        加载动画帧序列
        
        Args:
            name: 动画名称（用于缓存）
            paths: 动画帧图像路径列表
            
        Returns:
            动画帧Surface列表
        """
        if name in self._animations:
            return self._animations[name]
        
        frames = []
        for path in paths:
            frame = self.load_image(path)
            frames.append(frame)
        
        self._animations[name] = frames
        return frames
    
    def get_animation(self, name: str) -> Optional[List[pygame.Surface]]:
        """
        获取已加载的动画
        
        Args:
            name: 动画名称
            
        Returns:
            动画帧列表，如果不存在返回None
        """
        return self._animations.get(name)
    
    def load_player_sprites(self, color: str = 'red') -> Dict[str, Any]:
        """
        加载玩家所有精灵
        
        AI辅助生成: 便捷方法，一次性加载玩家的所有动画
        
        Args:
            color: 玩家颜色 ('red' 或 'green')
            
        Returns:
            包含所有玩家精灵和动画的字典
        """
        sprites = {}
        
        # 站立精灵
        sprites['idle'] = self.load_image(f'player/{color}_idle.png')
        
        # 跑步动画
        run_frames = []
        for i in range(1, 5):
            frame = self.load_image(f'player/{color}_run_{i}.png')
            run_frames.append(frame)
        sprites['run'] = run_frames
        self._animations[f'{color}_player_run'] = run_frames
        
        # 跳跃精灵
        sprites['jump'] = self.load_image(f'player/{color}_jump.png')
        
        return sprites
    
    def load_enemy_sprites(self, enemy_type: str) -> Dict[str, Any]:
        """
        加载敌人精灵
        
        Args:
            enemy_type: 敌人类型 ('mushling', 'shellback', 'flapper')
            
        Returns:
            包含敌人精灵和动画的字典
        """
        sprites = {}
        
        if enemy_type == 'mushling':
            # 走路动画
            walk_frames = [
                self.load_image('enemies/mushling_walk_1.png'),
                self.load_image('enemies/mushling_walk_2.png'),
            ]
            sprites['walk'] = walk_frames
            sprites['squashed'] = self.load_image('enemies/mushling_squashed.png')
            
        elif enemy_type == 'shellback':
            walk_frames = [
                self.load_image('enemies/shellback_walk_1.png'),
                self.load_image('enemies/shellback_walk_2.png'),
            ]
            sprites['walk'] = walk_frames
            sprites['shell'] = self.load_image('enemies/shellback_shell.png')
            
        elif enemy_type == 'flapper':
            fly_frames = [
                self.load_image(f'enemies/flapper_{i}.png')
                for i in range(1, 5)
            ]
            sprites['fly'] = fly_frames
        
        return sprites
    
    def load_tile_sprites(self) -> Dict[str, Any]:
        """
        加载所有瓦片精灵
        
        Returns:
            包含所有瓦片精灵的字典
        """
        tiles = {
            'ground': self.load_image('tiles/ground.png'),
            'brick': self.load_image('tiles/brick.png'),
            'empty_block': self.load_image('tiles/empty_block.png'),
            'pipe': self.load_image('tiles/pipe.png'),
            'spike': self.load_image('tiles/spike.png'),
            'spike_blink': self.load_image('tiles/spike_blink.png'),
            'platform': self.load_image('tiles/platform.png'),
            'flag': self.load_image('tiles/flag.png'),
        }
        
        # 问号块动画
        question_frames = [
            self.load_image(f'tiles/question_block_{i}.png')
            for i in range(1, 5)
        ]
        tiles['question_block'] = question_frames
        self._animations['question_block'] = question_frames
        
        return tiles
    
    def load_item_sprites(self) -> Dict[str, Any]:
        """
        加载所有道具精灵
        
        Returns:
            包含所有道具精灵的字典
        """
        items = {
            'mushroom': self.load_image('items/mushroom.png'),
        }
        
        # 金币动画
        coin_frames = [
            self.load_image(f'items/coin_{i}.png')
            for i in range(1, 5)
        ]
        items['coin'] = coin_frames
        self._animations['coin'] = coin_frames
        
        # 星星动画
        star_frames = [
            self.load_image(f'items/star_{i}.png')
            for i in range(1, 5)
        ]
        items['star'] = star_frames
        self._animations['star'] = star_frames
        
        return items
    
    def load_level(self, level_name: str) -> Dict:
        """
        加载关卡数据
        
        Args:
            level_name: 关卡名称（不含扩展名）
            
        Returns:
            关卡数据字典
        """
        if level_name in self._levels:
            return self._levels[level_name]
        
        level_path = os.path.join(LEVELS_DIR, f'{level_name}.json')
        
        try:
            with open(level_path, 'r', encoding='utf-8') as f:
                level_data = json.load(f)
            self._levels[level_name] = level_data
            return level_data
            
        except FileNotFoundError:
            print(f"警告: 关卡文件不存在 '{level_path}'")
            # 返回默认空关卡
            default_level = self._create_default_level()
            self._levels[level_name] = default_level
            return default_level
        except json.JSONDecodeError as e:
            print(f"警告: 关卡文件格式错误 '{level_path}': {e}")
            default_level = self._create_default_level()
            self._levels[level_name] = default_level
            return default_level
    
    def _create_default_level(self) -> Dict:
        """
        创建默认关卡数据
        
        AI辅助生成: 当关卡文件加载失败时使用的备用关卡
        """
        return {
            'name': 'Default Level',
            'width': 100,
            'height': 15,
            'tiles': [],
            'enemies': [],
            'items': [],
            'player_start': {'x': 2, 'y': 12},
            'goal': {'x': 95, 'y': 12}
        }
    
    def preload_all(self) -> None:
        """
        预加载所有游戏资源
        
        在游戏开始前调用此方法可以避免游戏过程中的加载延迟
        """
        print("预加载资源...")
        
        # 加载玩家精灵
        self.load_player_sprites('red')
        self.load_player_sprites('green')
        
        # 加载敌人精灵
        for enemy_type in ['mushling', 'shellback', 'flapper']:
            self.load_enemy_sprites(enemy_type)
        
        # 加载瓦片精灵
        self.load_tile_sprites()
        
        # 加载道具精灵
        self.load_item_sprites()
        
        print(f"资源加载完成: {len(self._images)} 张图像, "
              f"{len(self._animations)} 个动画")
    
    def clear_cache(self) -> None:
        """清除所有缓存的资源"""
        self._images.clear()
        self._animations.clear()
        self._levels.clear()
    
    def get_stats(self) -> Dict[str, int]:
        """
        获取资源统计信息
        
        Returns:
            资源数量统计字典
        """
        return {
            'images': len(self._images),
            'animations': len(self._animations),
            'levels': len(self._levels)
        }
    
    @classmethod
    def reset_instance(cls) -> None:
        """重置单例实例（主要用于测试）"""
        cls._instance = None
