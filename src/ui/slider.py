"""
滑块UI组件模块
AI辅助生成: 实现可拖动的滑块控件用于设置调节

滑块支持鼠标拖动和键盘方向键控制。
"""

import pygame
from typing import Callable, Optional, Tuple
from ..settings import Colors


class Slider:
    """
    滑块组件
    
    用于在指定范围内调节数值的UI控件。
    
    Attributes:
        x, y: 滑块位置
        width, height: 滑块尺寸
        min_value, max_value: 值范围
        value: 当前值
        label: 显示的标签
    """
    
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        min_value: float,
        max_value: float,
        initial_value: float,
        label: str = "",
        step: float = 0.1,
        on_change: Optional[Callable[[float], None]] = None
    ):
        """
        初始化滑块
        
        Args:
            x, y: 位置
            width, height: 尺寸
            min_value, max_value: 值范围
            initial_value: 初始值
            label: 标签文本
            step: 步进值
            on_change: 值改变时的回调函数
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.label = label
        self.on_change = on_change
        
        # 当前值
        self._value = max(min_value, min(max_value, initial_value))
        
        # 滑块手柄尺寸
        self.handle_width = 16
        self.handle_height = height + 8
        
        # 状态
        self.is_dragging = False
        self.is_hovered = False
        self.is_focused = False
        
        # 颜色
        self.track_color = (60, 60, 80)
        self.track_fill_color = (100, 150, 220)
        self.handle_color = (200, 200, 220)
        self.handle_hover_color = (255, 255, 255)
        self.handle_drag_color = (255, 220, 100)
        self.label_color = Colors.UI_TEXT
        self.value_color = (180, 220, 255)
        
        # 字体
        try:
            self.font = pygame.font.SysFont('microsoftyahei', 20)
            self.value_font = pygame.font.SysFont('microsoftyahei', 18)
        except:
            self.font = pygame.font.Font(None, 24)
            self.value_font = pygame.font.Font(None, 20)
    
    @property
    def value(self) -> float:
        return self._value
    
    @value.setter
    def value(self, new_value: float) -> None:
        old_value = self._value
        self._value = max(self.min_value, min(self.max_value, new_value))
        
        # 量化到步进值
        if self.step > 0:
            steps = round((self._value - self.min_value) / self.step)
            self._value = self.min_value + steps * self.step
            self._value = max(self.min_value, min(self.max_value, self._value))
        
        if self._value != old_value and self.on_change:
            self.on_change(self._value)
    
    @property
    def rect(self) -> pygame.Rect:
        """整个滑块区域（包括标签）"""
        return pygame.Rect(self.x, self.y - 30, self.width, self.height + 40)
    
    @property
    def track_rect(self) -> pygame.Rect:
        """滑轨矩形"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    @property
    def handle_rect(self) -> pygame.Rect:
        """滑块手柄矩形"""
        progress = (self._value - self.min_value) / (self.max_value - self.min_value)
        handle_x = self.x + int(progress * (self.width - self.handle_width))
        handle_y = self.y - (self.handle_height - self.height) // 2
        return pygame.Rect(handle_x, handle_y, self.handle_width, self.handle_height)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        处理输入事件
        
        Args:
            event: Pygame事件
            
        Returns:
            是否消费了事件
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键
                if self.handle_rect.collidepoint(event.pos):
                    self.is_dragging = True
                    self.is_focused = True
                    return True
                elif self.track_rect.collidepoint(event.pos):
                    # 点击滑轨，直接跳转到该位置
                    self._update_value_from_pos(event.pos[0])
                    self.is_dragging = True
                    self.is_focused = True
                    return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_dragging:
                self.is_dragging = False
                return True
        
        elif event.type == pygame.MOUSEMOTION:
            # 更新悬停状态
            self.is_hovered = self.handle_rect.collidepoint(event.pos) or \
                             self.track_rect.collidepoint(event.pos)
            
            if self.is_dragging:
                self._update_value_from_pos(event.pos[0])
                return True
        
        elif event.type == pygame.KEYDOWN and self.is_focused:
            if event.key == pygame.K_LEFT:
                self.value -= self.step
                return True
            elif event.key == pygame.K_RIGHT:
                self.value += self.step
                return True
        
        return False
    
    def _update_value_from_pos(self, x: int) -> None:
        """根据鼠标X坐标更新值"""
        relative_x = x - self.x
        progress = relative_x / self.width
        progress = max(0, min(1, progress))
        self.value = self.min_value + progress * (self.max_value - self.min_value)
    
    def update(self, dt: float) -> None:
        """更新滑块状态"""
        pass  # 目前不需要动画
    
    def render(self, screen: pygame.Surface) -> None:
        """渲染滑块"""
        # 渲染标签
        if self.label:
            label_surface = self.font.render(self.label, True, self.label_color)
            screen.blit(label_surface, (self.x, self.y - 28))
        
        # 渲染滑轨背景
        track_rect = self.track_rect
        pygame.draw.rect(screen, self.track_color, track_rect, border_radius=4)
        
        # 渲染已填充部分
        progress = (self._value - self.min_value) / (self.max_value - self.min_value)
        fill_width = int(progress * self.width)
        if fill_width > 0:
            fill_rect = pygame.Rect(self.x, self.y, fill_width, self.height)
            pygame.draw.rect(screen, self.track_fill_color, fill_rect, border_radius=4)
        
        # 渲染手柄
        handle_rect = self.handle_rect
        if self.is_dragging:
            color = self.handle_drag_color
        elif self.is_hovered:
            color = self.handle_hover_color
        else:
            color = self.handle_color
        
        pygame.draw.rect(screen, color, handle_rect, border_radius=3)
        pygame.draw.rect(screen, (255, 255, 255), handle_rect, width=1, border_radius=3)
        
        # 渲染当前值
        value_text = f"{self._value:.1f}"
        value_surface = self.value_font.render(value_text, True, self.value_color)
        value_x = self.x + self.width + 15
        value_y = self.y + (self.height - value_surface.get_height()) // 2
        screen.blit(value_surface, (value_x, value_y))
    
    def set_focus(self, focused: bool) -> None:
        """设置焦点状态"""
        self.is_focused = focused
