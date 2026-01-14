"""
设置状态模块
AI辅助生成: 实现游戏设置界面

允许玩家调节灵敏度参数和自定义按键绑定。
"""

import pygame
from typing import TYPE_CHECKING, List, Optional, Tuple

from .game_state import GameState
from ..ui.slider import Slider
from ..ui.button import Button
from ..core.player_config import PlayerConfig
from ..core.save_manager import SaveManager
from ..core.key_bindings import KeyBindings
from ..settings import Colors, SCREEN_WIDTH, SCREEN_HEIGHT

if TYPE_CHECKING:
    from ..game import Game
    from ..core.state_machine import StateMachine


class SettingsState(GameState):
    """
    设置状态
    
    显示设置界面，包含灵敏度设置和按键绑定。
    """
    
    def __init__(self, game: 'Game', state_machine: 'StateMachine'):
        super().__init__(game, state_machine)
        
        self.sliders: List[Slider] = []
        self.buttons: List[Button] = []
        self.player_config = PlayerConfig()
        self.save_manager = SaveManager()
        self.key_bindings = KeyBindings()
        
        # 当前选中的索引
        self.selected_index = 0
        
        # 当前标签页: 'sensitivity' 或 'keybinds'
        self.current_tab = 'sensitivity'
        
        # 按键绑定相关
        self.waiting_for_key = False  # 是否正在等待按键输入
        self.binding_action: Optional[str] = None  # 正在绑定的动作
        self.binding_slot: int = 0  # 正在绑定的槽位
        
        # 按键绑定项目
        self.keybind_items: List[dict] = []
        self.keybind_selected = 0
    
    def enter(self, **kwargs) -> None:
        """进入设置状态"""
        self._create_ui()
    
    def exit(self) -> None:
        """退出设置状态"""
        self._save_settings()
        self.key_bindings.save_bindings()
        self.sliders.clear()
        self.buttons.clear()
    
    def _create_ui(self) -> None:
        """创建UI元素"""
        self.sliders.clear()
        self.buttons.clear()
        self.keybind_items.clear()
        
        center_x = SCREEN_WIDTH // 2
        
        # 标签页按钮
        tab_y = 70
        tab_width = 120
        tab_height = 35
        tab_spacing = 20
        
        sensitivity_tab = Button(
            x=center_x - tab_width - tab_spacing // 2,
            y=tab_y,
            width=tab_width,
            height=tab_height,
            text="灵敏度",
            callback=lambda: self._switch_tab('sensitivity')
        )
        self.buttons.append(sensitivity_tab)
        
        keybinds_tab = Button(
            x=center_x + tab_spacing // 2,
            y=tab_y,
            width=tab_width,
            height=tab_height,
            text="按键绑定",
            callback=lambda: self._switch_tab('keybinds')
        )
        self.buttons.append(keybinds_tab)
        
        # 根据当前标签页创建内容
        if self.current_tab == 'sensitivity':
            self._create_sensitivity_ui()
        else:
            self._create_keybinds_ui()
        
        # 底部按钮
        button_y = SCREEN_HEIGHT - 80
        button_width = 140
        button_height = 45
        button_spacing = 20
        
        # 重置按钮
        reset_button = Button(
            x=center_x - button_width - button_spacing // 2,
            y=button_y,
            width=button_width,
            height=button_height,
            text="重置默认",
            callback=self._reset_defaults
        )
        self.buttons.append(reset_button)
        
        # 返回按钮
        back_button = Button(
            x=center_x + button_spacing // 2,
            y=button_y,
            width=button_width,
            height=button_height,
            text="返回",
            callback=self._go_back
        )
        self.buttons.append(back_button)
    
    def _create_sensitivity_ui(self) -> None:
        """创建灵敏度设置UI"""
        center_x = SCREEN_WIDTH // 2
        start_y = 140
        slider_width = 300
        slider_height = 12
        spacing = 80
        
        # 移动速度滑块
        speed_info = self.player_config.get_param_info('move_speed_multiplier')
        speed_slider = Slider(
            x=center_x - slider_width // 2,
            y=start_y,
            width=slider_width,
            height=slider_height,
            min_value=speed_info['min'],
            max_value=speed_info['max'],
            initial_value=speed_info['current'],
            label="移动速度",
            step=speed_info['step'],
            on_change=lambda v: setattr(self.player_config, 'move_speed_multiplier', v)
        )
        self.sliders.append(speed_slider)
        
        # 摩擦力/惯性滑块
        friction_info = self.player_config.get_param_info('friction_multiplier')
        friction_slider = Slider(
            x=center_x - slider_width // 2,
            y=start_y + spacing,
            width=slider_width,
            height=slider_height,
            min_value=friction_info['min'],
            max_value=friction_info['max'],
            initial_value=friction_info['current'],
            label="惯性/滑动感 (越高越滑)",
            step=friction_info['step'],
            on_change=lambda v: setattr(self.player_config, 'friction_multiplier', v)
        )
        self.sliders.append(friction_slider)
        
        # 跳跃力度滑块
        jump_info = self.player_config.get_param_info('jump_power_multiplier')
        jump_slider = Slider(
            x=center_x - slider_width // 2,
            y=start_y + spacing * 2,
            width=slider_width,
            height=slider_height,
            min_value=jump_info['min'],
            max_value=jump_info['max'],
            initial_value=jump_info['current'],
            label="跳跃力度",
            step=jump_info['step'],
            on_change=lambda v: setattr(self.player_config, 'jump_power_multiplier', v)
        )
        self.sliders.append(jump_slider)
        
        # 设置初始焦点
        if self.sliders:
            self.sliders[0].set_focus(True)
            self.selected_index = 0
    
    def _create_keybinds_ui(self) -> None:
        """创建按键绑定UI"""
        self.keybind_items.clear()
        
        start_y = 140
        item_height = 50
        
        for i, action in enumerate(self.key_bindings.get_all_actions()):
            self.keybind_items.append({
                'action': action,
                'y': start_y + i * item_height,
                'keys': self.key_bindings.get_keys(action)
            })
        
        self.keybind_selected = 0
    
    def _switch_tab(self, tab: str) -> None:
        """切换标签页"""
        if self.current_tab != tab:
            self.current_tab = tab
            self.waiting_for_key = False
            self._create_ui()
    
    def _reset_defaults(self) -> None:
        """重置为默认值"""
        if self.current_tab == 'sensitivity':
            self.player_config.reset_to_defaults()
            # 更新滑块显示
            param_names = ['move_speed_multiplier', 'friction_multiplier', 'jump_power_multiplier']
            for i, name in enumerate(param_names):
                if i < len(self.sliders):
                    self.sliders[i].value = getattr(self.player_config, name)
        else:
            self.key_bindings.reset_to_defaults()
            self._create_keybinds_ui()
    
    def _go_back(self) -> None:
        """返回上一个状态"""
        self.state_machine.change_state('menu')
    
    def _save_settings(self) -> None:
        """保存设置到存档"""
        if self.save_manager.current_save_id:
            config_data = self.player_config.to_save_data()
            self.save_manager.update_current_save({'player_config': config_data})
            self.save_manager.save_current()
    
    def _start_key_binding(self, action: str, slot: int) -> None:
        """开始监听按键绑定"""
        self.waiting_for_key = True
        self.binding_action = action
        self.binding_slot = slot
    
    def _finish_key_binding(self, key: int) -> None:
        """完成按键绑定"""
        if self.binding_action:
            self.key_bindings.set_key(self.binding_action, self.binding_slot, key)
            self._create_keybinds_ui()
        
        self.waiting_for_key = False
        self.binding_action = None
    
    def _cancel_key_binding(self) -> None:
        """取消按键绑定"""
        self.waiting_for_key = False
        self.binding_action = None
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """处理事件"""
        # 如果正在等待按键输入
        if self.waiting_for_key:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._cancel_key_binding()
                else:
                    self._finish_key_binding(event.key)
            return
        
        # 处理滑块事件
        for slider in self.sliders:
            if slider.handle_event(event):
                return
        
        # 处理按钮事件
        for button in self.buttons:
            button.handle_event(event)
        
        # 处理按键绑定项目点击
        if self.current_tab == 'keybinds' and event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self._handle_keybind_click(event.pos)
        
        # 键盘导航
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._go_back()
            elif self.current_tab == 'sensitivity':
                self._handle_sensitivity_keys(event)
            else:
                self._handle_keybind_keys(event)
    
    def _handle_sensitivity_keys(self, event: pygame.event.Event) -> None:
        """处理灵敏度页面的键盘事件"""
        if event.key == pygame.K_UP:
            self._navigate_sliders(-1)
        elif event.key == pygame.K_DOWN:
            self._navigate_sliders(1)
        elif event.key == pygame.K_TAB:
            direction = -1 if pygame.key.get_mods() & pygame.KMOD_SHIFT else 1
            self._navigate_sliders(direction)
    
    def _handle_keybind_keys(self, event: pygame.event.Event) -> None:
        """处理按键绑定页面的键盘事件"""
        if event.key == pygame.K_UP:
            self.keybind_selected = max(0, self.keybind_selected - 1)
        elif event.key == pygame.K_DOWN:
            self.keybind_selected = min(len(self.keybind_items) - 1, self.keybind_selected + 1)
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            # 绑定第一个槽位
            if self.keybind_items:
                action = self.keybind_items[self.keybind_selected]['action']
                self._start_key_binding(action, 0)
        elif event.key == pygame.K_1:
            # 绑定第一个槽位
            if self.keybind_items:
                action = self.keybind_items[self.keybind_selected]['action']
                self._start_key_binding(action, 0)
        elif event.key == pygame.K_2:
            # 绑定第二个槽位
            if self.keybind_items:
                action = self.keybind_items[self.keybind_selected]['action']
                self._start_key_binding(action, 1)
    
    def _handle_keybind_click(self, pos: Tuple[int, int]) -> None:
        """处理按键绑定项目的点击"""
        center_x = SCREEN_WIDTH // 2
        item_width = 400
        key_box_width = 80
        
        for i, item in enumerate(self.keybind_items):
            item_rect = pygame.Rect(
                center_x - item_width // 2,
                item['y'],
                item_width,
                45
            )
            
            if item_rect.collidepoint(pos):
                self.keybind_selected = i
                
                # 检查点击了哪个按键槽位
                key1_rect = pygame.Rect(
                    center_x + 40,
                    item['y'] + 8,
                    key_box_width,
                    30
                )
                key2_rect = pygame.Rect(
                    center_x + 40 + key_box_width + 10,
                    item['y'] + 8,
                    key_box_width,
                    30
                )
                
                if key1_rect.collidepoint(pos):
                    self._start_key_binding(item['action'], 0)
                elif key2_rect.collidepoint(pos):
                    self._start_key_binding(item['action'], 1)
                break
    
    def _navigate_sliders(self, direction: int) -> None:
        """导航滑块"""
        if not self.sliders:
            return
        
        self.sliders[self.selected_index].set_focus(False)
        self.selected_index = (self.selected_index + direction) % len(self.sliders)
        self.sliders[self.selected_index].set_focus(True)
    
    def update(self, dt: float) -> None:
        """更新状态"""
        for slider in self.sliders:
            slider.update(dt)
        
        for button in self.buttons:
            button.update(dt)
    
    def render(self, screen: pygame.Surface) -> None:
        """渲染设置界面"""
        # 背景
        screen.fill(Colors.UI_BACKGROUND)
        
        # 标题
        self._render_title(screen)
        
        # 渲染标签页按钮（高亮当前标签）
        for i, button in enumerate(self.buttons[:2]):
            if (i == 0 and self.current_tab == 'sensitivity') or \
               (i == 1 and self.current_tab == 'keybinds'):
                button.bg_color = Colors.UI_HIGHLIGHT
            else:
                button.bg_color = Colors.UI_BUTTON
            button.render(screen)
        
        # 渲染内容
        if self.current_tab == 'sensitivity':
            for slider in self.sliders:
                slider.render(screen)
        else:
            self._render_keybinds(screen)
        
        # 渲染底部按钮
        for button in self.buttons[2:]:
            button.render(screen)
        
        # 渲染提示
        self._render_hints(screen)
        
        # 如果正在等待按键，显示提示
        if self.waiting_for_key:
            self._render_waiting_overlay(screen)
    
    def _render_title(self, screen: pygame.Surface) -> None:
        """渲染标题"""
        try:
            font = pygame.font.SysFont('microsoftyahei', 32)
        except:
            font = pygame.font.Font(None, 38)
        
        title = font.render("游戏设置", True, Colors.UI_HIGHLIGHT)
        rect = title.get_rect(center=(SCREEN_WIDTH // 2, 30))
        screen.blit(title, rect)
    
    def _render_keybinds(self, screen: pygame.Surface) -> None:
        """渲染按键绑定列表"""
        try:
            font = pygame.font.SysFont('microsoftyahei', 18)
            small_font = pygame.font.SysFont('microsoftyahei', 14)
        except:
            font = pygame.font.Font(None, 22)
            small_font = pygame.font.Font(None, 16)
        
        center_x = SCREEN_WIDTH // 2
        item_width = 400
        key_box_width = 80
        
        for i, item in enumerate(self.keybind_items):
            y = item['y']
            is_selected = i == self.keybind_selected
            
            # 背景
            bg_color = (60, 60, 80) if is_selected else (40, 40, 55)
            item_rect = pygame.Rect(center_x - item_width // 2, y, item_width, 45)
            pygame.draw.rect(screen, bg_color, item_rect, border_radius=5)
            
            if is_selected:
                pygame.draw.rect(screen, Colors.UI_HIGHLIGHT, item_rect, 2, border_radius=5)
            
            # 动作名称
            action_name = self.key_bindings.get_action_name(item['action'])
            text = font.render(action_name, True, (220, 220, 230))
            screen.blit(text, (center_x - item_width // 2 + 15, y + 12))
            
            # 按键槽位
            keys = self.key_bindings.get_keys(item['action'])
            for slot in range(2):
                key_x = center_x + 40 + slot * (key_box_width + 10)
                key_rect = pygame.Rect(key_x, y + 8, key_box_width, 30)
                
                # 槽位背景
                slot_bg = (50, 50, 70)
                pygame.draw.rect(screen, slot_bg, key_rect, border_radius=3)
                pygame.draw.rect(screen, (80, 80, 100), key_rect, 1, border_radius=3)
                
                # 按键名称
                if slot < len(keys) and keys[slot]:
                    key_name = self.key_bindings.get_key_name(keys[slot])
                else:
                    key_name = "---"
                
                key_text = small_font.render(key_name, True, (180, 180, 200))
                key_text_rect = key_text.get_rect(center=key_rect.center)
                screen.blit(key_text, key_text_rect)
    
    def _render_waiting_overlay(self, screen: pygame.Surface) -> None:
        """渲染等待按键输入的遮罩"""
        # 半透明遮罩
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # 提示框
        box_width = 350
        box_height = 120
        box_rect = pygame.Rect(
            (SCREEN_WIDTH - box_width) // 2,
            (SCREEN_HEIGHT - box_height) // 2,
            box_width,
            box_height
        )
        pygame.draw.rect(screen, (50, 50, 70), box_rect, border_radius=10)
        pygame.draw.rect(screen, Colors.UI_HIGHLIGHT, box_rect, 2, border_radius=10)
        
        try:
            font = pygame.font.SysFont('microsoftyahei', 20)
            small_font = pygame.font.SysFont('microsoftyahei', 14)
        except:
            font = pygame.font.Font(None, 24)
            small_font = pygame.font.Font(None, 16)
        
        # 提示文字
        if self.binding_action:
            action_name = self.key_bindings.get_action_name(self.binding_action)
            text1 = font.render(f"请按下要绑定的按键", True, (220, 220, 230))
            text2 = font.render(f"动作: {action_name}", True, Colors.UI_HIGHLIGHT)
            text3 = small_font.render("按 ESC 取消", True, (150, 150, 170))
            
            screen.blit(text1, text1.get_rect(center=(SCREEN_WIDTH // 2, box_rect.y + 30)))
            screen.blit(text2, text2.get_rect(center=(SCREEN_WIDTH // 2, box_rect.y + 60)))
            screen.blit(text3, text3.get_rect(center=(SCREEN_WIDTH // 2, box_rect.y + 95)))
    
    def _render_hints(self, screen: pygame.Surface) -> None:
        """渲染操作提示"""
        try:
            font = pygame.font.SysFont('microsoftyahei', 14)
        except:
            font = pygame.font.Font(None, 16)
        
        if self.current_tab == 'sensitivity':
            hints = [
                "↑/↓: 切换选项  ←/→: 调节数值  ESC: 返回"
            ]
        else:
            hints = [
                "↑/↓: 选择动作  点击按键槽位或按1/2绑定  ESC: 返回"
            ]
        
        y = SCREEN_HEIGHT - 35
        for hint in hints:
            text = font.render(hint, True, (120, 120, 150))
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            screen.blit(text, rect)
            y += 20
