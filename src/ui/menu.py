"""
菜单界面模块
AI辅助生成: 实现游戏主菜单

此模块提供菜单界面的渲染和交互功能。
"""

import pygame
from typing import List, Callable, Optional

from .button import Button
from ..settings import SCREEN_WIDTH, SCREEN_HEIGHT, Colors


class Menu:
    """
    菜单界面类
    
    提供游戏的主菜单界面，包括开始游戏、选择难度等选项。
    
    Attributes:
        buttons: 按钮列表
        title: 菜单标题
    """
    
    def __init__(self, title: str = "Jump Loop World"):
        """
        初始化菜单
        
        Args:
            title: 菜单标题
        """
        self.title = title
        self.buttons: List[Button] = []
        
        # 字体
        self.title_font: Optional[pygame.font.Font] = None
        self.subtitle_font: Optional[pygame.font.Font] = None
        self._init_fonts()
        
        # 背景动画
        self.bg_offset = 0.0
        
        # 装饰精灵
        self.decorations = []
    
    def _init_fonts(self) -> None:
        """初始化字体"""
        try:
            self.title_font = pygame.font.SysFont('microsoftyahei', 64)
            self.subtitle_font = pygame.font.SysFont('microsoftyahei', 24)
        except:
            self.title_font = pygame.font.Font(None, 72)
            self.subtitle_font = pygame.font.Font(None, 28)
    
    def add_button(self, text: str, callback: Callable) -> Button:
        """
        添加按钮
        
        Args:
            text: 按钮文本
            callback: 点击回调
            
        Returns:
            创建的按钮
        """
        # 自动计算按钮位置 - 紧凑布局，上移留出底部提示空间
        button_width = 220
        button_height = 38
        button_spacing = 44  # 按钮间距
        button_x = (SCREEN_WIDTH - button_width) // 2
        button_y = 220 + len(self.buttons) * button_spacing
        
        button = Button(button_x, button_y, button_width, button_height, 
                       text, callback)
        self.buttons.append(button)
        return button
    
    def clear_buttons(self) -> None:
        """清除所有按钮"""
        self.buttons.clear()
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """
        处理事件
        
        Args:
            event: Pygame事件
        """
        for button in self.buttons:
            button.handle_event(event)
    
    def update(self, dt: float) -> None:
        """
        更新菜单
        
        Args:
            dt: 时间增量
        """
        # 更新背景动画
        self.bg_offset += dt * 20
        if self.bg_offset > 100:
            self.bg_offset -= 100
        
        # 更新按钮
        for button in self.buttons:
            button.update(dt)
    
    def render(self, screen: pygame.Surface) -> None:
        """
        渲染菜单
        
        Args:
            screen: 渲染目标
        """
        # 渲染背景
        self._render_background(screen)
        
        # 渲染标题
        self._render_title(screen)
        
        # 渲染按钮
        for button in self.buttons:
            button.render(screen)
        
        # 渲染底部提示
        self._render_footer(screen)
    
    def _render_background(self, screen: pygame.Surface) -> None:
        """渲染装饰性背景"""
        # 绘制网格图案
        grid_color = (100, 140, 180, 30)
        for y in range(0, SCREEN_HEIGHT, 50):
            offset = int(self.bg_offset) % 50
            for x in range(-50, SCREEN_WIDTH + 50, 50):
                rect = pygame.Rect(x + offset, y, 48, 48)
                s = pygame.Surface((48, 48), pygame.SRCALPHA)
                pygame.draw.rect(s, grid_color, (0, 0, 48, 48), 1, border_radius=5)
                screen.blit(s, rect.topleft)
    
    def _render_title(self, screen: pygame.Surface) -> None:
        """渲染标题"""
        if not self.title_font:
            return
        
        # 标题阴影
        shadow_surface = self.title_font.render(self.title, True, (0, 0, 50))
        shadow_rect = shadow_surface.get_rect(center=(SCREEN_WIDTH // 2 + 3, 120 + 3))
        screen.blit(shadow_surface, shadow_rect)
        
        # 标题文字
        title_surface = self.title_font.render(self.title, True, Colors.UI_HIGHLIGHT)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 120))
        screen.blit(title_surface, title_rect)
        
        # 副标题
        if self.subtitle_font:
            subtitle = "Jump Loop World"
            subtitle_surface = self.subtitle_font.render(subtitle, True, Colors.UI_TEXT)
            subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, 180))
            screen.blit(subtitle_surface, subtitle_rect)
    
    def _render_footer(self, screen: pygame.Surface) -> None:
        """渲染底部信息"""
        # 不再渲染底部提示，避免与按钮重叠
        pass
