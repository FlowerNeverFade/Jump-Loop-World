"""
按钮组件模块
AI辅助生成: 实现可点击的UI按钮

此模块提供Button类，用于创建游戏菜单中的交互按钮。
"""

import pygame
from typing import Callable, Optional, Tuple

from ..settings import Colors
from ..core.audio_manager import AudioManager


class Button:
    """
    UI按钮类
    
    可点击的按钮组件，支持悬停效果和点击回调。
    
    Attributes:
        x: X坐标
        y: Y坐标
        width: 宽度
        height: 高度
        text: 按钮文本
        callback: 点击回调函数
        hovered: 是否被悬停
        pressed: 是否被按下
    """
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 text: str, callback: Callable = None):
        """
        初始化按钮
        
        Args:
            x: X坐标
            y: Y坐标
            width: 宽度
            height: 高度
            text: 按钮文本
            callback: 点击时调用的函数
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.callback = callback
        
        self.rect = pygame.Rect(x, y, width, height)
        
        # 状态
        self.hovered = False
        self.pressed = False
        self.enabled = True
        self._was_hovered = False
        
        # 颜色
        self.color_normal = Colors.UI_BUTTON
        self.color_hover = Colors.UI_BUTTON_HOVER
        self.color_pressed = (60, 60, 100)
        self.color_disabled = (50, 50, 50)
        self.text_color = Colors.UI_TEXT
        self.border_color = Colors.UI_HIGHLIGHT
        
        # 字体
        self.font: Optional[pygame.font.Font] = None
        self._init_font()
    
    def _init_font(self) -> None:
        """初始化字体"""
        # 根据按钮高度自动选择字体大小
        if self.height <= 36:
            font_size = 18
        elif self.height <= 40:
            font_size = 20
        else:
            font_size = 24
        
        try:
            # 尝试使用系统中文字体
            self.font = pygame.font.SysFont('microsoftyahei', font_size)
        except:
            self.font = pygame.font.Font(None, font_size + 4)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        处理事件
        
        Args:
            event: Pygame事件
            
        Returns:
            是否消费了事件
        """
        if not self.enabled:
            return False
        
        if event.type == pygame.MOUSEMOTION:
            new_hovered = self.rect.collidepoint(event.pos)
            self.hovered = new_hovered
            # 仅在“刚进入悬停”时播放一次
            if new_hovered and not self._was_hovered:
                try:
                    AudioManager().play_sfx("ui_hover")
                except Exception:
                    pass
            self._was_hovered = new_hovered
            return self.hovered
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.pressed = True
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.pressed:
                self.pressed = False
                if self.rect.collidepoint(event.pos) and self.callback:
                    try:
                        AudioManager().play_sfx("ui_click")
                    except Exception:
                        pass
                    self.callback()
                    return True
        
        return False
    
    def update(self, dt: float) -> None:
        """更新按钮状态"""
        # 检查鼠标位置更新悬停状态
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)
        self._was_hovered = self.hovered
    
    def render(self, screen: pygame.Surface) -> None:
        """
        渲染按钮
        
        Args:
            screen: 渲染目标
        """
        # 确定当前颜色
        if not self.enabled:
            color = self.color_disabled
        elif self.pressed:
            color = self.color_pressed
        elif self.hovered:
            color = self.color_hover
        else:
            color = self.color_normal
        
        # 绘制按钮背景
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        
        # 绘制边框
        if self.hovered or self.pressed:
            pygame.draw.rect(screen, self.border_color, self.rect, 
                           width=3, border_radius=8)
        else:
            pygame.draw.rect(screen, (100, 100, 140), self.rect, 
                           width=2, border_radius=8)
        
        # 绘制文本
        if self.font:
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)
    
    def set_position(self, x: int, y: int) -> None:
        """设置按钮位置"""
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
    
    def set_text(self, text: str) -> None:
        """设置按钮文本"""
        self.text = text
    
    def set_enabled(self, enabled: bool) -> None:
        """设置是否启用"""
        self.enabled = enabled
