"""
状态机模块
AI辅助生成: 实现游戏状态管理的状态机模式

此模块提供游戏状态的管理功能，支持状态切换、状态栈等功能。
用于管理菜单、游戏、暂停、结束等不同的游戏状态。

设计模式: 状态模式 (State Pattern)
- Context: StateMachine 管理当前状态
- State: GameState 定义状态接口
- ConcreteState: MenuState, PlayState 等具体状态
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, List
import pygame


class GameState(ABC):
    """
    游戏状态抽象基类
    
    定义所有游戏状态必须实现的接口。
    每个状态负责处理自己的输入、更新和渲染逻辑。
    
    Attributes:
        game: 游戏实例引用
        state_machine: 状态机引用
    """
    
    def __init__(self, game: Any, state_machine: 'StateMachine'):
        """
        初始化状态
        
        Args:
            game: 游戏主实例
            state_machine: 状态机实例
        """
        self.game = game
        self.state_machine = state_machine
    
    @abstractmethod
    def enter(self, **kwargs) -> None:
        """
        进入状态时调用
        
        用于初始化状态所需的资源和变量。
        
        Args:
            **kwargs: 从前一个状态传递的参数
        """
        pass
    
    @abstractmethod
    def exit(self) -> None:
        """
        退出状态时调用
        
        用于清理状态使用的资源。
        """
        pass
    
    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """
        处理输入事件
        
        Args:
            event: Pygame事件对象
        """
        pass
    
    @abstractmethod
    def update(self, dt: float) -> None:
        """
        更新状态逻辑
        
        Args:
            dt: 距离上一帧的时间（秒）
        """
        pass
    
    @abstractmethod
    def render(self, screen: pygame.Surface) -> None:
        """
        渲染状态画面
        
        Args:
            screen: 渲染目标Surface
        """
        pass


class StateMachine:
    """
    状态机类
    
    管理游戏状态的切换和更新。支持状态栈，可以实现暂停等功能。
    
    使用示例:
        sm = StateMachine(game)
        sm.register_state('menu', MenuState)
        sm.register_state('play', PlayState)
        sm.change_state('menu')
    
    Attributes:
        game: 游戏实例引用
        states: 已注册的状态类字典
        current_state: 当前活动状态
        state_stack: 状态栈（用于暂停等场景）
    """
    
    def __init__(self, game: Any):
        """
        初始化状态机
        
        Args:
            game: 游戏主实例
        """
        self.game = game
        self.states: Dict[str, type] = {}
        self.current_state: Optional[GameState] = None
        self.state_stack: List[GameState] = []
        self._pending_state: Optional[str] = None
        self._pending_kwargs: Dict = {}
    
    def register_state(self, name: str, state_class: type) -> None:
        """
        注册状态类
        
        Args:
            name: 状态名称
            state_class: 状态类（必须继承自GameState）
            
        Raises:
            TypeError: 如果state_class不是GameState的子类
        """
        if not issubclass(state_class, GameState):
            raise TypeError(f"状态类必须继承自GameState: {state_class}")
        self.states[name] = state_class
    
    def change_state(self, state_name: str, **kwargs) -> None:
        """
        切换到指定状态
        
        Args:
            state_name: 目标状态名称
            **kwargs: 传递给新状态enter方法的参数
            
        Raises:
            KeyError: 如果状态未注册
        """
        if state_name not in self.states:
            raise KeyError(f"未注册的状态: {state_name}")
        
        # 标记待切换的状态（在下一帧开始时执行实际切换）
        self._pending_state = state_name
        self._pending_kwargs = kwargs
    
    def _do_state_change(self) -> None:
        """执行实际的状态切换"""
        if self._pending_state is None:
            return
        
        state_name = self._pending_state
        kwargs = self._pending_kwargs
        self._pending_state = None
        self._pending_kwargs = {}
        
        # 退出当前状态
        if self.current_state is not None:
            self.current_state.exit()
        
        # 清空状态栈
        self.state_stack.clear()
        
        # 创建并进入新状态
        state_class = self.states[state_name]
        self.current_state = state_class(self.game, self)
        self.current_state.enter(**kwargs)
    
    def push_state(self, state_name: str, **kwargs) -> None:
        """
        压入新状态（保留当前状态）
        
        用于暂停菜单等需要覆盖当前状态但不销毁它的场景。
        
        Args:
            state_name: 目标状态名称
            **kwargs: 传递给新状态的参数
        """
        if state_name not in self.states:
            raise KeyError(f"未注册的状态: {state_name}")
        
        # 将当前状态压入栈
        if self.current_state is not None:
            self.state_stack.append(self.current_state)
        
        # 创建并进入新状态
        state_class = self.states[state_name]
        self.current_state = state_class(self.game, self)
        self.current_state.enter(**kwargs)
    
    def pop_state(self) -> bool:
        """
        弹出当前状态，恢复栈顶状态
        
        Returns:
            是否成功弹出（栈非空时返回True）
        """
        if not self.state_stack:
            return False
        
        # 退出当前状态
        if self.current_state is not None:
            self.current_state.exit()
        
        # 恢复栈顶状态
        self.current_state = self.state_stack.pop()
        
        return True
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """
        将事件传递给当前状态处理
        
        Args:
            event: Pygame事件对象
        """
        if self.current_state is not None:
            self.current_state.handle_event(event)
    
    def update(self, dt: float) -> None:
        """
        更新当前状态
        
        Args:
            dt: 时间增量（秒）
        """
        # 先处理待切换的状态
        self._do_state_change()
        
        # 更新当前状态
        if self.current_state is not None:
            self.current_state.update(dt)
    
    def render(self, screen: pygame.Surface) -> None:
        """
        渲染当前状态
        
        如果有状态栈，会先渲染栈中的状态（用于实现暂停菜单半透明效果）
        
        Args:
            screen: 渲染目标Surface
        """
        # 渲染栈中的状态（底层先渲染）
        for state in self.state_stack:
            state.render(screen)
        
        # 渲染当前状态
        if self.current_state is not None:
            self.current_state.render(screen)
    
    def get_current_state_name(self) -> Optional[str]:
        """
        获取当前状态名称
        
        Returns:
            当前状态名称，如果没有当前状态返回None
        """
        if self.current_state is None:
            return None
        
        for name, state_class in self.states.items():
            if isinstance(self.current_state, state_class):
                return name
        
        return None
    
    def is_state(self, state_name: str) -> bool:
        """
        检查当前是否为指定状态
        
        Args:
            state_name: 状态名称
            
        Returns:
            是否为指定状态
        """
        return self.get_current_state_name() == state_name
