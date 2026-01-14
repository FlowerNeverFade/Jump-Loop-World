"""
暂停状态模块
AI辅助生成: 实现游戏暂停状态

暂停状态显示暂停菜单，允许玩家继续游戏或返回主菜单。
"""

import pygame
from typing import TYPE_CHECKING

from .game_state import GameState
from ..ui.menu import Menu
from ..settings import SCREEN_WIDTH, SCREEN_HEIGHT

if TYPE_CHECKING:
    from ..game import Game
    from ..core.state_machine import StateMachine


class PauseState(GameState):
    """
    暂停状态
    
    游戏暂停时显示的界面，可以继续游戏或返回菜单。
    """
    
    def __init__(self, game: 'Game', state_machine: 'StateMachine'):
        super().__init__(game, state_machine)
        
        self.menu: Menu = None
    
    def enter(self, **kwargs) -> None:
        """进入暂停状态"""
        self.menu = Menu("游戏暂停")
        
        self.menu.add_button("继续游戏", self._resume)
        self.menu.add_button("返回主菜单", self._return_to_menu)
    
    def exit(self) -> None:
        """退出暂停状态"""
        self.menu = None
    
    def _resume(self) -> None:
        """继续游戏"""
        self.state_machine.pop_state()
    
    def _return_to_menu(self) -> None:
        """返回主菜单"""
        # 先弹出暂停状态，再切换到菜单
        self.state_machine.pop_state()
        self.state_machine.change_state('menu')
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """处理事件"""
        if self.menu:
            self.menu.handle_event(event)
        
        # ESC继续游戏（在Game类中处理）
    
    def update(self, dt: float) -> None:
        """更新"""
        if self.menu:
            self.menu.update(dt)
    
    def render(self, screen: pygame.Surface) -> None:
        """渲染"""
        # 半透明遮罩（游戏画面在下层已渲染）
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # 渲染暂停菜单
        if self.menu:
            self.menu.render(screen)
        
        # 渲染提示
        try:
            font = pygame.font.SysFont('microsoftyahei', 20)
        except:
            font = pygame.font.Font(None, 24)
        
        hint = font.render("按 ESC 继续游戏", True, (150, 150, 180))
        rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        screen.blit(hint, rect)
