"""
存档选择状态模块
AI辅助生成: 实现存档选择界面

允许玩家创建、加载和删除存档。
支持无限数量的存档槽位。
"""

import pygame
from typing import TYPE_CHECKING, List, Dict, Any, Optional

from .game_state import GameState
from ..ui.button import Button
from ..core.save_manager import SaveManager
from ..settings import Colors, SCREEN_WIDTH, SCREEN_HEIGHT

if TYPE_CHECKING:
    from ..game import Game
    from ..core.state_machine import StateMachine


class SaveSelectState(GameState):
    """
    存档选择状态
    
    显示所有存档列表，提供新建、加载、删除功能。
    """
    
    def __init__(self, game: 'Game', state_machine: 'StateMachine'):
        super().__init__(game, state_machine)
        
        self.save_manager = SaveManager()
        
        # 存档列表
        self.save_list: List[Dict[str, Any]] = []
        
        # 当前选中的存档索引
        self.selected_index = 0
        
        # 滚动偏移
        self.scroll_offset = 0
        self.max_visible_saves = 4
        
        # 按钮
        self.buttons: List[Button] = []
        
        # 删除确认状态
        self.confirming_delete = False
        self.delete_target: Optional[str] = None
        
        # 字体
        try:
            self.title_font = pygame.font.SysFont('microsoftyahei', 36)
            self.save_font = pygame.font.SysFont('microsoftyahei', 22)
            self.info_font = pygame.font.SysFont('microsoftyahei', 16)
        except:
            self.title_font = pygame.font.Font(None, 40)
            self.save_font = pygame.font.Font(None, 26)
            self.info_font = pygame.font.Font(None, 18)
    
    def enter(self, **kwargs) -> None:
        """进入存档选择状态"""
        # 存档界面使用菜单音乐
        try:
            self.game.audio_manager.play_music('menu')
        except Exception:
            pass
        self._refresh_save_list()
        self._create_buttons()
    
    def exit(self) -> None:
        """退出存档选择状态"""
        self.buttons.clear()
        self.confirming_delete = False
        self.delete_target = None
    
    def _refresh_save_list(self) -> None:
        """刷新存档列表"""
        self.save_list = self.save_manager.get_save_list()
    
    def _create_buttons(self) -> None:
        """创建按钮"""
        self.buttons.clear()
        
        button_width = 120
        button_height = 40
        spacing = 15
        y = SCREEN_HEIGHT - 70
        
        # 新建存档按钮
        new_btn = Button(
            x=SCREEN_WIDTH // 2 - button_width * 2 - spacing,
            y=y,
            width=button_width,
            height=button_height,
            text="新建存档",
            callback=self._create_new_save
        )
        self.buttons.append(new_btn)
        
        # 加载按钮
        load_btn = Button(
            x=SCREEN_WIDTH // 2 - button_width // 2,
            y=y,
            width=button_width,
            height=button_height,
            text="加载存档",
            callback=self._load_selected_save
        )
        self.buttons.append(load_btn)
        
        # 删除按钮
        delete_btn = Button(
            x=SCREEN_WIDTH // 2 + button_width + spacing,
            y=y,
            width=button_width,
            height=button_height,
            text="删除存档",
            callback=self._confirm_delete
        )
        self.buttons.append(delete_btn)
    
    def _create_new_save(self) -> None:
        """创建新存档"""
        save_id = self.save_manager.create_new_save()
        self.save_manager.set_current_save(save_id)
        self._refresh_save_list()
        
        # 直接进入商店
        self.state_machine.change_state('shop')
    
    def _load_selected_save(self) -> None:
        """加载选中的存档"""
        if not self.save_list or self.selected_index >= len(self.save_list):
            return
        
        save_info = self.save_list[self.selected_index]
        save_id = save_info['id']
        
        if self.save_manager.set_current_save(save_id):
            # 进入商店
            self.state_machine.change_state('shop')
    
    def _confirm_delete(self) -> None:
        """确认删除存档"""
        if not self.save_list or self.selected_index >= len(self.save_list):
            return
        
        save_info = self.save_list[self.selected_index]
        self.delete_target = save_info['id']
        self.confirming_delete = True
    
    def _delete_save(self) -> None:
        """删除存档"""
        if self.delete_target:
            self.save_manager.delete_save(self.delete_target)
            self._refresh_save_list()
            
            # 调整选中索引
            if self.selected_index >= len(self.save_list) and len(self.save_list) > 0:
                self.selected_index = len(self.save_list) - 1
        
        self.confirming_delete = False
        self.delete_target = None
    
    def _cancel_delete(self) -> None:
        """取消删除"""
        self.confirming_delete = False
        self.delete_target = None
    
    def _go_back(self) -> None:
        """返回主菜单"""
        self.state_machine.change_state('menu')
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """处理事件"""
        # 删除确认模式
        if self.confirming_delete:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    self._delete_save()
                elif event.key in (pygame.K_n, pygame.K_ESCAPE):
                    self._cancel_delete()
            return
        
        # 按钮事件
        for btn in self.buttons:
            btn.handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._go_back()
            elif event.key == pygame.K_UP:
                self._navigate(-1)
            elif event.key == pygame.K_DOWN:
                self._navigate(1)
            elif event.key == pygame.K_RETURN:
                self._load_selected_save()
            elif event.key == pygame.K_n:
                self._create_new_save()
            elif event.key == pygame.K_DELETE:
                self._confirm_delete()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self._handle_click(event.pos)
    
    def _navigate(self, direction: int) -> None:
        """导航存档列表"""
        if not self.save_list:
            return
        
        self.selected_index = (self.selected_index + direction) % len(self.save_list)
        
        # 调整滚动
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.max_visible_saves:
            self.scroll_offset = self.selected_index - self.max_visible_saves + 1
    
    def _handle_click(self, pos: tuple) -> None:
        """处理点击事件"""
        # 检查是否点击了存档
        save_start_y = 100
        save_height = 70
        
        for i, save in enumerate(self.save_list[self.scroll_offset:self.scroll_offset + self.max_visible_saves]):
            save_y = save_start_y + i * save_height
            save_rect = pygame.Rect(50, save_y, SCREEN_WIDTH - 100, save_height - 5)
            
            if save_rect.collidepoint(pos):
                clicked_index = self.scroll_offset + i
                if clicked_index == self.selected_index:
                    # 双击加载
                    self._load_selected_save()
                else:
                    self.selected_index = clicked_index
                return
    
    def update(self, dt: float) -> None:
        """更新状态"""
        for btn in self.buttons:
            btn.update(dt)
    
    def render(self, screen: pygame.Surface) -> None:
        """渲染存档选择界面"""
        screen.fill(Colors.UI_BACKGROUND)
        
        # 标题
        title = self.title_font.render("选择存档", True, Colors.UI_HIGHLIGHT)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))
        
        # 存档列表
        self._render_save_list(screen)
        
        # 按钮
        for btn in self.buttons:
            btn.render(screen)
        
        # 操作提示
        self._render_hints(screen)
        
        # 删除确认对话框
        if self.confirming_delete:
            self._render_delete_confirm(screen)
    
    def _render_save_list(self, screen: pygame.Surface) -> None:
        """渲染存档列表"""
        if not self.save_list:
            no_saves = self.save_font.render("暂无存档，按 N 创建新存档", True, (150, 150, 150))
            screen.blit(no_saves, (SCREEN_WIDTH // 2 - no_saves.get_width() // 2, 200))
            return
        
        save_start_y = 100
        save_height = 70
        save_width = SCREEN_WIDTH - 100
        
        visible_saves = self.save_list[self.scroll_offset:self.scroll_offset + self.max_visible_saves]
        
        for i, save in enumerate(visible_saves):
            actual_index = self.scroll_offset + i
            save_y = save_start_y + i * save_height
            save_rect = pygame.Rect(50, save_y, save_width, save_height - 5)
            
            # 背景
            if actual_index == self.selected_index:
                bg_color = (80, 100, 140)
            else:
                bg_color = (50, 55, 70)
            
            pygame.draw.rect(screen, bg_color, save_rect, border_radius=8)
            pygame.draw.rect(screen, (100, 100, 120), save_rect, width=1, border_radius=8)
            
            # 存档名称
            name_text = self.save_font.render(save['name'], True, Colors.UI_TEXT)
            screen.blit(name_text, (save_rect.x + 15, save_rect.y + 10))
            
            # 存档信息
            coins = save.get('total_coins', 0)
            level = save.get('level_reached', 1)
            info_text = f"金币: {coins}  |  关卡: {level}"
            info_surface = self.info_font.render(info_text, True, (180, 180, 200))
            screen.blit(info_surface, (save_rect.x + 15, save_rect.y + 38))
            
            # 最后游玩时间
            last_played = save.get('last_played', '未知')
            if last_played != '未知':
                # 简化时间显示
                try:
                    last_played = last_played[:16].replace('T', ' ')
                except:
                    pass
            time_text = self.info_font.render(f"上次游玩: {last_played}", True, (140, 140, 160))
            screen.blit(time_text, (save_rect.right - time_text.get_width() - 15, save_rect.y + 25))
        
        # 滚动指示器
        if len(self.save_list) > self.max_visible_saves:
            if self.scroll_offset > 0:
                arrow_up = self.save_font.render("▲", True, (200, 200, 200))
                screen.blit(arrow_up, (SCREEN_WIDTH // 2 - 10, save_start_y - 20))
            
            if self.scroll_offset + self.max_visible_saves < len(self.save_list):
                arrow_down = self.save_font.render("▼", True, (200, 200, 200))
                screen.blit(arrow_down, (SCREEN_WIDTH // 2 - 10, save_start_y + self.max_visible_saves * save_height))
    
    def _render_hints(self, screen: pygame.Surface) -> None:
        """渲染操作提示"""
        hints = "↑↓: 选择  Enter: 加载  N: 新建  Delete: 删除  ESC: 返回"
        hint_surface = self.info_font.render(hints, True, (120, 120, 150))
        screen.blit(hint_surface, (SCREEN_WIDTH // 2 - hint_surface.get_width() // 2, SCREEN_HEIGHT - 25))
    
    def _render_delete_confirm(self, screen: pygame.Surface) -> None:
        """渲染删除确认对话框"""
        # 半透明背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # 对话框
        dialog_width = 350
        dialog_height = 150
        dialog_x = (SCREEN_WIDTH - dialog_width) // 2
        dialog_y = (SCREEN_HEIGHT - dialog_height) // 2
        
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        pygame.draw.rect(screen, (60, 60, 80), dialog_rect, border_radius=10)
        pygame.draw.rect(screen, (100, 100, 120), dialog_rect, width=2, border_radius=10)
        
        # 标题
        title = self.save_font.render("确认删除", True, (255, 100, 100))
        screen.blit(title, (dialog_x + dialog_width // 2 - title.get_width() // 2, dialog_y + 20))
        
        # 提示文本
        msg = self.info_font.render("确定要删除这个存档吗？此操作无法撤销。", True, Colors.UI_TEXT)
        screen.blit(msg, (dialog_x + dialog_width // 2 - msg.get_width() // 2, dialog_y + 60))
        
        # 按键提示
        keys = self.info_font.render("Y = 确认删除    N = 取消", True, (180, 180, 200))
        screen.blit(keys, (dialog_x + dialog_width // 2 - keys.get_width() // 2, dialog_y + 110))
