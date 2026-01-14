"""
菜单状态模块
AI辅助生成: 实现游戏主菜单状态

主菜单状态允许玩家选择难度并开始游戏。
"""

import pygame
from typing import TYPE_CHECKING

from .game_state import GameState
from ..ui.menu import Menu
from ..settings import Colors, SCREEN_WIDTH, SCREEN_HEIGHT

if TYPE_CHECKING:
    from ..game import Game
    from ..core.state_machine import StateMachine


class MenuState(GameState):
    """
    主菜单状态
    
    显示游戏主菜单，提供难度选择和开始游戏选项。
    """
    
    def __init__(self, game: 'Game', state_machine: 'StateMachine'):
        super().__init__(game, state_machine)
        
        self.menu: Menu = None
    
    def enter(self, **kwargs) -> None:
        """进入菜单状态"""
        # 创建菜单
        self.menu = Menu("Jump Loop World")
        self._show_main_menu()
    
    def exit(self) -> None:
        """退出菜单状态"""
        self.menu = None
    
    def _start_adventure(self) -> None:
        """开始冒险模式（Roguelike）"""
        self.state_machine.change_state('save_select')
    
    def _start_two_player(self) -> None:
        """进入双人模式难度选择"""
        self._show_two_player_difficulty_menu()
    
    def _show_main_menu(self) -> None:
        """渲染主菜单按钮"""
        if not self.menu:
            return
        self.menu.clear_buttons()
        self.menu.add_button("冒险模式", self._start_adventure)
        self.menu.add_button("双人模式", self._start_two_player)
        self.menu.add_button("设置", self._open_settings)
        self.menu.add_button("退出游戏", self._quit_game)
    
    def _show_two_player_difficulty_menu(self) -> None:
        """双人模式难度选择菜单"""
        if not self.menu:
            return
        self.menu.clear_buttons()
        self.menu.add_button("双人：简单", lambda: self._start_two_player_with_difficulty('easy'))
        self.menu.add_button("双人：困难", lambda: self._start_two_player_with_difficulty('hard'))
        self.menu.add_button("双人：变态", lambda: self._start_two_player_with_difficulty('hardcore'))
        self.menu.add_button("返回", self._show_main_menu)
    
    def _start_two_player_with_difficulty(self, difficulty: str) -> None:
        """开始双人模式（带难度）"""
        # 先清除当前存档，避免加载冒险模式的能力
        from ..core.save_manager import SaveManager
        from ..core.player_config import PlayerConfig
        
        SaveManager().clear_current_save()
        PlayerConfig().reset_bonuses()  # 重置所有升级和装备加成
        
        self.game.set_difficulty(difficulty)
        self.game.reset_game_data()
        
        # 变态难度使用 HardcoreLevel
        hardcore = difficulty == 'hardcore'
        self.state_machine.change_state('play', two_player=True, hardcore=hardcore)
    
    
    def _open_settings(self) -> None:
        """打开设置界面"""
        self.state_machine.change_state('settings')
    
    def _quit_game(self) -> None:
        """退出游戏"""
        self.game.quit()
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """处理事件"""
        if self.menu:
            self.menu.handle_event(event)
    
    def update(self, dt: float) -> None:
        """更新菜单"""
        if self.menu:
            self.menu.update(dt)
    
    def render(self, screen: pygame.Surface) -> None:
        """渲染菜单"""
        if self.menu:
            self.menu.render(screen)
        
        # 渲染按键提示
        self._render_key_hints(screen)
    
    def _render_key_hints(self, screen: pygame.Surface) -> None:
        """渲染按键提示"""
        try:
            font = pygame.font.SysFont('microsoftyahei', 14)
        except:
            font = pygame.font.Font(None, 18)
        
        # 操作提示放在最底部
        hint_text = "方向键/WASD移动 | 空格跳跃"
        text = font.render(hint_text, True, (80, 80, 110))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 12))
        screen.blit(text, rect)
