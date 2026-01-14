"""
UI管理器模块
AI辅助生成: 统一管理所有UI组件

此模块提供UI组件的集中管理，简化UI的使用。
"""

import pygame
from typing import Dict, Optional, TYPE_CHECKING

from .button import Button
from .hud import HUD
from .menu import Menu

if TYPE_CHECKING:
    from ..game import Game


class UIManager:
    """
    UI管理器类
    
    统一管理游戏中的所有UI组件。
    
    Attributes:
        game: 游戏实例引用
        hud: HUD实例
        menu: 菜单实例
    """
    
    def __init__(self, game: 'Game'):
        """
        初始化UI管理器
        
        Args:
            game: 游戏实例
        """
        self.game = game
        
        # UI组件
        self.hud: Optional[HUD] = None
        self.current_menu: Optional[Menu] = None
        
        # 初始化组件
        self._init_components()
    
    def _init_components(self) -> None:
        """初始化UI组件"""
        self.hud = HUD(self.game)
    
    def create_menu(self, title: str = "Jump Loop World") -> Menu:
        """
        创建菜单
        
        Args:
            title: 菜单标题
            
        Returns:
            创建的菜单实例
        """
        self.current_menu = Menu(title)
        return self.current_menu
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """
        处理UI事件
        
        Args:
            event: Pygame事件
        """
        if self.current_menu:
            self.current_menu.handle_event(event)
    
    def update(self, dt: float) -> None:
        """
        更新UI
        
        Args:
            dt: 时间增量
        """
        if self.current_menu:
            self.current_menu.update(dt)
    
    def render_hud(self, screen: pygame.Surface) -> None:
        """渲染HUD"""
        if self.hud:
            self.hud.render(screen)
    
    def render_menu(self, screen: pygame.Surface) -> None:
        """渲染当前菜单"""
        if self.current_menu:
            self.current_menu.render(screen)
    
    def clear_menu(self) -> None:
        """清除当前菜单"""
        self.current_menu = None
