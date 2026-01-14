"""
摄像机模块
AI辅助生成: 实现跟随玩家的2D摄像机

摄像机负责计算视口偏移，使玩家始终保持在屏幕适当位置。
"""

from typing import Tuple, TYPE_CHECKING

from ..settings import SCREEN_WIDTH, SCREEN_HEIGHT

if TYPE_CHECKING:
    from ..entities.player import Player


class Camera:
    """
    2D摄像机类
    
    跟随玩家移动，计算渲染偏移量。
    
    Attributes:
        x: 摄像机X坐标
        y: 摄像机Y坐标
        width: 视口宽度
        height: 视口高度
        level_width: 关卡宽度
        level_height: 关卡高度
        follow_speed: 跟随速度（0-1，1为立即跟随）
    """
    
    def __init__(self, level_width: int, level_height: int):
        """
        初始化摄像机
        
        Args:
            level_width: 关卡宽度（像素）
            level_height: 关卡高度（像素）
        """
        self.x = 0.0
        self.y = 0.0
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        self.level_width = level_width
        self.level_height = level_height
        
        # 跟随参数
        self.follow_speed = 0.1  # 平滑跟随
        self.target_x = 0.0
        self.target_y = 0.0
        
        # 跟随区域（玩家在此区域内时摄像机不移动）
        self.dead_zone_x = SCREEN_WIDTH * 0.2
        self.dead_zone_y = SCREEN_HEIGHT * 0.2
    
    def update(self, player: 'Player', dt: float) -> None:
        """
        更新摄像机位置
        
        AI辅助生成: 实现平滑跟随和死区逻辑
        我修改为只水平跟随，保持地面在屏幕底部（经典马里奥风格）
        
        Args:
            player: 要跟随的玩家
            dt: 时间增量
        """
        # 计算目标位置（玩家在屏幕中心偏左）
        self.target_x = player.x - self.width * 0.35
        
        # Y轴固定，不跟随玩家垂直移动（经典马里奥摄像机）
        # 摄像机Y固定为0，使地面始终在屏幕底部
        self.target_y = 0
        
        # 平滑跟随（只在X轴）
        self.x += (self.target_x - self.x) * self.follow_speed
        self.y = self.target_y
        
        # 限制摄像机范围
        self._clamp_to_level()
    
    def _clamp_to_level(self) -> None:
        """将摄像机限制在关卡范围内"""
        # 左边界
        if self.x < 0:
            self.x = 0
        
        # 右边界
        max_x = self.level_width - self.width
        if max_x > 0 and self.x > max_x:
            self.x = max_x
        elif max_x <= 0:
            self.x = 0
        
        # 上边界
        if self.y < 0:
            self.y = 0
        
        # 下边界
        max_y = self.level_height - self.height
        if max_y > 0 and self.y > max_y:
            self.y = max_y
        elif max_y <= 0:
            self.y = 0
    
    def get_offset(self) -> Tuple[int, int]:
        """
        获取渲染偏移量
        
        Returns:
            (offset_x, offset_y) 元组
        """
        return (int(self.x), int(self.y))
    
    def is_visible(self, x: float, y: float, width: int, height: int) -> bool:
        """
        检查对象是否在视口内
        
        Args:
            x: 对象X坐标
            y: 对象Y坐标
            width: 对象宽度
            height: 对象高度
            
        Returns:
            是否可见
        """
        return (x + width > self.x and x < self.x + self.width and
                y + height > self.y and y < self.y + self.height)
    
    def screen_to_world(self, screen_x: int, screen_y: int) -> Tuple[float, float]:
        """
        将屏幕坐标转换为世界坐标
        
        Args:
            screen_x: 屏幕X坐标
            screen_y: 屏幕Y坐标
            
        Returns:
            (world_x, world_y) 元组
        """
        return (screen_x + self.x, screen_y + self.y)
    
    def world_to_screen(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """
        将世界坐标转换为屏幕坐标
        
        Args:
            world_x: 世界X坐标
            world_y: 世界Y坐标
            
        Returns:
            (screen_x, screen_y) 元组
        """
        return (int(world_x - self.x), int(world_y - self.y))
    
    def reset(self) -> None:
        """重置摄像机位置"""
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
    
    def set_position(self, x: float, y: float) -> None:
        """
        直接设置摄像机位置
        
        Args:
            x: X坐标
            y: Y坐标
        """
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self._clamp_to_level()
