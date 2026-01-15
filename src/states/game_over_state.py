"""
游戏结束状态模块
AI辅助生成: 实现游戏结束/胜利状态

显示游戏结果，提供重新开始或返回菜单的选项。
支持Roguelike模式的金币结算显示。
"""

import pygame
from typing import TYPE_CHECKING

from .game_state import GameState
from ..ui.menu import Menu
from ..settings import SCREEN_WIDTH, SCREEN_HEIGHT, Colors, DifficultySettings
from ..core.save_manager import SaveManager

if TYPE_CHECKING:
    from ..game import Game
    from ..core.state_machine import StateMachine


class GameOverState(GameState):
    """
    游戏结束状态
    
    显示游戏结果（胜利或失败），并提供选项。
    """
    
    def __init__(self, game: 'Game', state_machine: 'StateMachine'):
        super().__init__(game, state_machine)
        
        self.menu: Menu = None
        self.won = False  # 是否胜利
        self.save_manager = SaveManager()
        
        # Roguelike结算信息
        self.is_adventure_mode = False
        self.earned_coins = 0
        self.total_coins = 0
    
    def enter(self, **kwargs) -> None:
        """进入游戏结束状态"""
        self.won = kwargs.get('won', False)

        # 结算界面使用菜单音乐
        try:
            self.game.audio_manager.play_music('menu')
        except Exception:
            pass
        
        # 检查是否为冒险模式
        self.is_adventure_mode = self.save_manager.current_save_id is not None
        
        # 计算金币结算
        if self.is_adventure_mode:
            collected = self.game.coins
            if self.won:
                self.earned_coins = collected + 50  # 通关奖励
            else:
                self.earned_coins = int(collected * 0.5)  # 死亡损失一半
            self.total_coins = self.save_manager.get_coins()
        
        # 创建按钮（不使用Menu的自动布局）
        from ..ui.button import Button
        self.menu = Menu("")  # 空标题，不用Menu渲染标题
        
        # 手动设置按钮位置
        btn_y = 200
        btn_spacing = 50
        btn_width = 200
        btn_height = 40
        btn_x = (SCREEN_WIDTH - btn_width) // 2
        
        restart_btn = Button(btn_x, btn_y, btn_width, btn_height, "重新开始", self._restart)
        self.menu.buttons.append(restart_btn)
        btn_y += btn_spacing
        
        # 冒险模式显示返回商店选项
        if self.is_adventure_mode:
            shop_btn = Button(btn_x, btn_y, btn_width, btn_height, "返回商店", self._return_to_shop)
            self.menu.buttons.append(shop_btn)
            btn_y += btn_spacing
        
        menu_btn = Button(btn_x, btn_y, btn_width, btn_height, "返回主菜单", self._return_to_menu)
        self.menu.buttons.append(menu_btn)
    
    def exit(self) -> None:
        """退出状态"""
        self.menu = None
    
    def _restart(self) -> None:
        """重新开始游戏"""
        self.game.reset_game_data()
        
        # 沿用当前难度；若为变态难度，则需要进入 HardcoreLevel
        hardcore = self.game.difficulty == DifficultySettings.HARDCORE
        
        # 保持双人模式状态
        two_player = self.game.two_player_mode
        
        if hardcore:
            self.state_machine.change_state('play', hardcore=True, two_player=two_player)
        else:
            self.state_machine.change_state('play', two_player=two_player)
    
    def _return_to_shop(self) -> None:
        """返回商店（冒险模式）"""
        self.state_machine.change_state('shop')
    
    def _return_to_menu(self) -> None:
        """返回主菜单"""
        self.state_machine.change_state('menu')
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """处理事件"""
        if self.menu:
            self.menu.handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._restart()
            elif event.key == pygame.K_ESCAPE:
                self._return_to_menu()
    
    def update(self, dt: float) -> None:
        """更新"""
        if self.menu:
            self.menu.update(dt)
    
    def render(self, screen: pygame.Surface) -> None:
        """渲染"""
        # 背景色
        if self.won:
            # 胜利 - 金色调
            screen.fill((50, 40, 20))
        else:
            # 失败 - 暗红色调
            screen.fill((40, 20, 20))
        
        # 自定义渲染布局，避免重叠
        self._render_title(screen)
        self._render_score(screen)
        self._render_buttons(screen)
        self._render_hints(screen)
    
    def _render_title(self, screen: pygame.Surface) -> None:
        """渲染标题"""
        try:
            title_font = pygame.font.SysFont('microsoftyahei', 48)
        except:
            title_font = pygame.font.Font(None, 56)
        
        title = "恭喜通关!" if self.won else "游戏结束"
        title_color = (255, 215, 0) if self.won else Colors.UI_HIGHLIGHT
        
        # 标题阴影
        shadow = title_font.render(title, True, (0, 0, 0))
        shadow_rect = shadow.get_rect(center=(SCREEN_WIDTH // 2 + 2, 62))
        screen.blit(shadow, shadow_rect)
        
        # 标题
        title_surface = title_font.render(title, True, title_color)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 60))
        screen.blit(title_surface, title_rect)
    
    def _render_score(self, screen: pygame.Surface) -> None:
        """渲染分数和金币"""
        try:
            font = pygame.font.SysFont('microsoftyahei', 22)
            small_font = pygame.font.SysFont('microsoftyahei', 18)
        except:
            font = pygame.font.Font(None, 26)
            small_font = pygame.font.Font(None, 20)
        
        y_offset = 110
        
        # 分数
        score_text = f"最终分数: {self.game.score}"
        score_surface = font.render(score_text, True, Colors.UI_TEXT)
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
        screen.blit(score_surface, score_rect)
        y_offset += 28
        
        # 金币信息
        if self.is_adventure_mode:
            # 冒险模式显示详细结算
            coin_text = f"金币: {self.game.coins} → 获得: +{self.earned_coins}"
            coin_surface = small_font.render(coin_text, True, Colors.YELLOW)
            coin_rect = coin_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(coin_surface, coin_rect)
            y_offset += 24
            
            total_text = f"总金币: {self.total_coins}"
            total_surface = small_font.render(total_text, True, (255, 200, 100))
            total_rect = total_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(total_surface, total_rect)
        else:
            # 普通模式
            coin_text = f"收集金币: {self.game.coins}"
            coin_surface = small_font.render(coin_text, True, Colors.YELLOW)
            coin_rect = coin_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(coin_surface, coin_rect)
    
    def _render_buttons(self, screen: pygame.Surface) -> None:
        """渲染按钮"""
        if self.menu:
            for btn in self.menu.buttons:
                btn.render(screen)
    
    def _render_hints(self, screen: pygame.Surface) -> None:
        """渲染底部提示"""
        try:
            hint_font = pygame.font.SysFont('microsoftyahei', 14)
        except:
            hint_font = pygame.font.Font(None, 18)
        
        hint_text = "Enter 重新开始 | ESC 返回菜单"
        hint_surface = hint_font.render(hint_text, True, (100, 100, 130))
        hint_rect = hint_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 15))
        screen.blit(hint_surface, hint_rect)
