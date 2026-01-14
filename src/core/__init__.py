# Core Module
# AI辅助生成: 核心模块初始化
"""
核心模块 - 包含游戏基础框架
- StateMachine: 状态机
- ResourceManager: 资源管理器
- EventSystem: 事件系统
"""

from .state_machine import StateMachine
from .resource_manager import ResourceManager
from .event_system import EventSystem

__all__ = ['StateMachine', 'ResourceManager', 'EventSystem']
