"""
事件系统模块
AI辅助生成: 实现观察者模式的事件系统

此模块提供了一个灵活的事件发布-订阅系统，用于游戏组件间的解耦通信。
支持的事件类型包括：得分、玩家死亡、通关、道具获取等。

设计模式: 观察者模式 (Observer Pattern)
- Subject: EventSystem 作为事件发布者
- Observer: 订阅事件的回调函数
"""

from typing import Callable, Dict, List, Any
from enum import Enum, auto


class GameEvent(Enum):
    """
    游戏事件类型枚举
    AI辅助生成: 定义所有可能的游戏事件
    """
    # 玩家事件
    PLAYER_JUMP = auto()
    PLAYER_LAND = auto()
    PLAYER_DAMAGE = auto()
    PLAYER_DEATH = auto()
    PLAYER_POWER_UP = auto()
    PLAYER_INVINCIBLE = auto()
    
    # 敌人事件
    ENEMY_STOMP = auto()
    ENEMY_DEATH = auto()
    
    # 道具事件
    COIN_COLLECT = auto()
    ITEM_SPAWN = auto()
    ITEM_COLLECT = auto()
    
    # 方块事件
    BLOCK_HIT = auto()
    BRICK_BREAK = auto()
    
    # 游戏流程事件
    GAME_START = auto()
    GAME_PAUSE = auto()
    GAME_RESUME = auto()
    GAME_OVER = auto()
    LEVEL_COMPLETE = auto()
    LEVEL_START = auto()
    
    # 分数事件
    SCORE_UPDATE = auto()


class EventSystem:
    """
    事件系统类 - 观察者模式实现
    
    提供事件的发布和订阅功能，实现游戏组件间的松耦合通信。
    
    使用示例:
        # 订阅事件
        event_system.subscribe(GameEvent.COIN_COLLECT, on_coin_collect)
        
        # 发布事件
        event_system.emit(GameEvent.COIN_COLLECT, {'value': 100})
        
        # 取消订阅
        event_system.unsubscribe(GameEvent.COIN_COLLECT, on_coin_collect)
    
    Attributes:
        _listeners: 事件监听器字典，键为事件类型，值为回调函数列表
    """
    
    # 单例实例
    _instance = None
    
    def __new__(cls):
        """
        单例模式实现
        确保整个游戏只有一个事件系统实例
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化事件系统"""
        if self._initialized:
            return
        
        self._listeners: Dict[GameEvent, List[Callable]] = {}
        self._initialized = True
    
    def subscribe(self, event: GameEvent, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        订阅事件
        
        Args:
            event: 要订阅的事件类型
            callback: 事件触发时调用的回调函数，接收一个字典参数
        
        Raises:
            TypeError: 如果callback不是可调用对象
        """
        if not callable(callback):
            raise TypeError(f"回调函数必须是可调用对象，得到: {type(callback)}")
        
        if event not in self._listeners:
            self._listeners[event] = []
        
        if callback not in self._listeners[event]:
            self._listeners[event].append(callback)
    
    def unsubscribe(self, event: GameEvent, callback: Callable) -> bool:
        """
        取消订阅事件
        
        Args:
            event: 要取消订阅的事件类型
            callback: 要移除的回调函数
            
        Returns:
            是否成功取消订阅
        """
        if event in self._listeners and callback in self._listeners[event]:
            self._listeners[event].remove(callback)
            return True
        return False
    
    def emit(self, event: GameEvent, data: Dict[str, Any] = None) -> None:
        """
        发布事件
        
        Args:
            event: 要发布的事件类型
            data: 事件携带的数据（可选）
        """
        if data is None:
            data = {}
        
        if event in self._listeners:
            for callback in self._listeners[event]:
                try:
                    callback(data)
                except Exception as e:
                    # 记录错误但不中断其他监听器
                    print(f"事件处理器错误 [{event.name}]: {e}")
    
    def clear(self, event: GameEvent = None) -> None:
        """
        清除事件监听器
        
        Args:
            event: 要清除的事件类型，如果为None则清除所有
        """
        if event is None:
            self._listeners.clear()
        elif event in self._listeners:
            self._listeners[event].clear()
    
    def get_listener_count(self, event: GameEvent) -> int:
        """
        获取指定事件的监听器数量
        
        Args:
            event: 事件类型
            
        Returns:
            监听器数量
        """
        return len(self._listeners.get(event, []))
    
    @classmethod
    def reset_instance(cls) -> None:
        """
        重置单例实例（主要用于测试）
        """
        cls._instance = None


# 全局事件系统实例
event_system = EventSystem()
