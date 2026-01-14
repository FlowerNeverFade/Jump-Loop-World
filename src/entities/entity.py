"""
实体基类模块
AI辅助生成: 定义所有游戏实体的基类

此模块提供Entity基类，所有游戏实体（玩家、敌人、道具等）都继承自此类。
封装了位置、碰撞盒、渲染等通用功能。

设计原则: 开闭原则 (Open-Closed Principle)
基类对扩展开放，对修改关闭
"""

import pygame
from abc import ABC, abstractmethod
from typing import Optional, Tuple, List
from ..settings import TILE_SIZE


class Entity(ABC):
    """
    游戏实体抽象基类
    
    所有游戏对象的基类，提供位置、碰撞、渲染等基础功能。
    
    Attributes:
        x: X坐标（像素）
        y: Y坐标（像素）
        width: 实体宽度
        height: 实体高度
        velocity_x: X方向速度
        velocity_y: Y方向速度
        image: 当前显示的图像
        rect: 碰撞矩形
        active: 实体是否活动
        facing_right: 是否面向右边
    """
    
    # 是否显示调试边框
    show_debug_box = True
    # 默认边框颜色
    debug_box_color = (0, 255, 0)  # 绿色
    
    def __init__(self, x: float, y: float, width: int, height: int):
        """
        初始化实体
        
        Args:
            x: 初始X坐标
            y: 初始Y坐标
            width: 实体宽度
            height: 实体高度
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # 速度
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        
        # 图像
        self.image: Optional[pygame.Surface] = None
        self._flipped_image: Optional[pygame.Surface] = None
        
        # 碰撞矩形
        self.rect = pygame.Rect(x, y, width, height)
        
        # 状态
        self.active = True
        self.facing_right = True
        self.on_ground = False
    
    def update_rect(self) -> None:
        """更新碰撞矩形位置"""
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
    
    def set_image(self, image: pygame.Surface) -> None:
        """
        设置实体图像
        
        Args:
            image: Pygame Surface对象
        """
        self.image = image
        self._flipped_image = pygame.transform.flip(image, True, False)
    
    def get_current_image(self) -> Optional[pygame.Surface]:
        """
        获取当前应显示的图像（考虑朝向）
        
        Returns:
            当前图像Surface
        """
        if self.image is None:
            return None
        return self.image if self.facing_right else self._flipped_image
    
    @abstractmethod
    def update(self, dt: float) -> None:
        """
        更新实体状态
        
        Args:
            dt: 时间增量（秒）
        """
        pass
    
    def render(self, screen: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)) -> None:
        """
        渲染实体
        
        Args:
            screen: 渲染目标Surface
            camera_offset: 摄像机偏移量 (x, y)
        """
        if not self.active:
            return
        
        # 计算渲染位置（应用摄像机偏移）
        render_x = int(self.x - camera_offset[0])
        render_y = int(self.y - camera_offset[1])
        
        current_image = self.get_current_image()
        if current_image is not None:
            screen.blit(current_image, (render_x, render_y))
        
        # 绘制调试边框（使用实际碰撞矩形位置）
        if Entity.show_debug_box:
            # 如果有碰撞偏移，使用偏移后的位置
            offset_x = getattr(self, 'collision_offset_x', 0)
            offset_y = getattr(self, 'collision_offset_y', 0)
            col_width = getattr(self, 'collision_width', self.width)
            col_height = getattr(self, 'collision_height', self.height)
            debug_rect = pygame.Rect(
                render_x + offset_x, 
                render_y + offset_y, 
                col_width, 
                col_height
            )
            pygame.draw.rect(screen, self.debug_box_color, debug_rect, 2)
    
    def collides_with(self, other: 'Entity') -> bool:
        """
        检测与另一个实体的碰撞
        
        Args:
            other: 另一个实体
            
        Returns:
            是否发生碰撞
        """
        return self.rect.colliderect(other.rect)
    
    def collides_with_rect(self, rect: pygame.Rect) -> bool:
        """
        检测与矩形的碰撞
        
        Args:
            rect: Pygame Rect对象
            
        Returns:
            是否发生碰撞
        """
        return self.rect.colliderect(rect)
    
    def get_center(self) -> Tuple[float, float]:
        """
        获取实体中心点坐标
        
        Returns:
            (center_x, center_y) 元组
        """
        return (self.x + self.width / 2, self.y + self.height / 2)
    
    def get_bottom(self) -> float:
        """获取实体底部Y坐标"""
        return self.y + self.height
    
    def get_right(self) -> float:
        """获取实体右边X坐标"""
        return self.x + self.width
    
    def is_on_screen(self, screen_width: int, screen_height: int, 
                     camera_offset: Tuple[int, int] = (0, 0)) -> bool:
        """
        检查实体是否在屏幕内
        
        Args:
            screen_width: 屏幕宽度
            screen_height: 屏幕高度
            camera_offset: 摄像机偏移
            
        Returns:
            是否在屏幕内
        """
        screen_x = self.x - camera_offset[0]
        screen_y = self.y - camera_offset[1]
        
        return (screen_x + self.width > 0 and screen_x < screen_width and
                screen_y + self.height > 0 and screen_y < screen_height)
    
    def deactivate(self) -> None:
        """停用实体"""
        self.active = False
    
    def activate(self) -> None:
        """激活实体"""
        self.active = True


class AnimatedEntity(Entity):
    """
    带动画的实体类
    
    扩展Entity类，添加帧动画支持。
    
    Attributes:
        animations: 动画字典 {动画名: 帧列表}
        current_animation: 当前播放的动画名
        animation_frame: 当前帧索引
        animation_speed: 动画播放速度（帧/秒）
        animation_timer: 动画计时器
    """
    
    def __init__(self, x: float, y: float, width: int, height: int):
        super().__init__(x, y, width, height)
        
        self.animations: dict = {}
        self.current_animation: str = ''
        self.animation_frame: int = 0
        self.animation_speed: float = 10.0  # 帧/秒
        self.animation_timer: float = 0.0
        
        # 缓存翻转后的动画帧
        self._flipped_animations: dict = {}
    
    def add_animation(self, name: str, frames: List[pygame.Surface]) -> None:
        """
        添加动画
        
        Args:
            name: 动画名称
            frames: 动画帧列表
        """
        self.animations[name] = frames
        # 预生成翻转帧
        self._flipped_animations[name] = [
            pygame.transform.flip(frame, True, False) for frame in frames
        ]
    
    def play_animation(self, name: str, reset: bool = False) -> None:
        """
        播放指定动画
        
        Args:
            name: 动画名称
            reset: 是否重置到第一帧
        """
        if name not in self.animations:
            return
        
        if self.current_animation != name or reset:
            self.current_animation = name
            if reset:
                self.animation_frame = 0
                self.animation_timer = 0.0
    
    def update_animation(self, dt: float) -> None:
        """
        更新动画帧
        
        Args:
            dt: 时间增量（秒）
        """
        if not self.current_animation or self.current_animation not in self.animations:
            return
        
        frames = self.animations[self.current_animation]
        if not frames:
            return
        
        # 更新计时器
        self.animation_timer += dt * self.animation_speed
        
        # 切换到下一帧
        if self.animation_timer >= 1.0:
            self.animation_timer -= 1.0
            self.animation_frame = (self.animation_frame + 1) % len(frames)
    
    def get_current_image(self) -> Optional[pygame.Surface]:
        """获取当前动画帧"""
        if not self.current_animation or self.current_animation not in self.animations:
            return super().get_current_image()
        
        frames = self.animations[self.current_animation]
        if not frames:
            return super().get_current_image()
        
        frame_index = self.animation_frame % len(frames)
        
        if self.facing_right:
            return frames[frame_index]
        else:
            return self._flipped_animations[self.current_animation][frame_index]
