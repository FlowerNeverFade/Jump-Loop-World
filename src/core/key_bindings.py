"""
按键绑定管理模块
AI辅助生成: 实现自定义按键绑定功能

允许玩家自定义游戏操作的按键映射。
"""

import pygame
import json
import os
import sys
from typing import Dict, Optional, List, Callable

from ..settings import BASE_DIR, APP_NAME, get_user_data_dir


class KeyBindings:
    """
    按键绑定管理器（单例模式）
    
    管理游戏中所有可自定义的按键绑定。
    """
    
    _instance: Optional['KeyBindings'] = None
    
    # 默认按键绑定
    DEFAULT_BINDINGS = {
        'move_left': [pygame.K_LEFT, pygame.K_a],
        'move_right': [pygame.K_RIGHT, pygame.K_d],
        'jump': [pygame.K_SPACE, pygame.K_w, pygame.K_UP],
        'down': [pygame.K_DOWN, pygame.K_s],
        'dash': [pygame.K_LALT, pygame.K_RALT],
    }
    
    # 动作名称的中文显示
    ACTION_NAMES = {
        'move_left': '向左移动',
        'move_right': '向右移动',
        'jump': '跳跃',
        'down': '下蹲/下砸',
        'dash': '冲刺',
    }
    
    # 按键名称映射
    KEY_NAMES = {
        pygame.K_LEFT: '←',
        pygame.K_RIGHT: '→',
        pygame.K_UP: '↑',
        pygame.K_DOWN: '↓',
        pygame.K_SPACE: '空格',
        pygame.K_LSHIFT: '左Shift',
        pygame.K_RSHIFT: '右Shift',
        pygame.K_LCTRL: '左Ctrl',
        pygame.K_RCTRL: '右Ctrl',
        pygame.K_LALT: '左Alt',
        pygame.K_RALT: '右Alt',
        pygame.K_TAB: 'Tab',
        pygame.K_RETURN: '回车',
        pygame.K_ESCAPE: 'ESC',
        pygame.K_BACKSPACE: '退格',
    }
    
    def __new__(cls) -> 'KeyBindings':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._bindings: Dict[str, List[int]] = {}
        if getattr(sys, "frozen", False):
            config_dir = os.path.join(get_user_data_dir(APP_NAME), "config")
        else:
            config_dir = os.path.join(BASE_DIR, "config")
        self._config_path = os.path.join(config_dir, "key_bindings.json")
        
        # 加载绑定
        self._load_bindings()
    
    def _load_bindings(self) -> None:
        """从文件加载按键绑定"""
        try:
            if os.path.exists(self._config_path):
                with open(self._config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 验证并加载
                    for action, keys in data.items():
                        if action in self.DEFAULT_BINDINGS:
                            self._bindings[action] = keys
        except Exception as e:
            print(f"加载按键绑定失败: {e}")
        
        # 填充缺失的绑定为默认值
        for action, keys in self.DEFAULT_BINDINGS.items():
            if action not in self._bindings:
                self._bindings[action] = keys.copy()
    
    def save_bindings(self) -> None:
        """保存按键绑定到文件"""
        try:
            os.makedirs(os.path.dirname(self._config_path), exist_ok=True)
            with open(self._config_path, 'w', encoding='utf-8') as f:
                json.dump(self._bindings, f, indent=2)
        except Exception as e:
            print(f"保存按键绑定失败: {e}")
    
    def get_keys(self, action: str) -> List[int]:
        """获取某个动作绑定的按键列表"""
        return self._bindings.get(action, [])
    
    def set_key(self, action: str, slot: int, key: int) -> None:
        """
        设置某个动作的按键
        
        Args:
            action: 动作名称
            slot: 按键槽位（0/1/2，支持三个按键）
            key: pygame按键码
        """
        if action not in self._bindings:
            self._bindings[action] = []
        
        # 确保列表足够长
        while len(self._bindings[action]) <= slot:
            self._bindings[action].append(0)
        
        self._bindings[action][slot] = key
    
    def is_action_pressed(self, action: str, keys: pygame.key.ScancodeWrapper) -> bool:
        """
        检查某个动作是否被按下
        
        Args:
            action: 动作名称
            keys: pygame.key.get_pressed()的结果
            
        Returns:
            是否有任意绑定的按键被按下
        """
        for key in self._bindings.get(action, []):
            if key and keys[key]:
                return True
        return False
    
    def reset_to_defaults(self) -> None:
        """重置为默认按键绑定"""
        self._bindings = {action: keys.copy() for action, keys in self.DEFAULT_BINDINGS.items()}
    
    def get_key_name(self, key: int) -> str:
        """获取按键的显示名称"""
        if key in self.KEY_NAMES:
            return self.KEY_NAMES[key]
        
        # 字母键
        if pygame.K_a <= key <= pygame.K_z:
            return chr(key).upper()
        
        # 数字键
        if pygame.K_0 <= key <= pygame.K_9:
            return chr(key)
        
        # 小键盘数字
        if pygame.K_KP0 <= key <= pygame.K_KP9:
            return f'小键盘{key - pygame.K_KP0}'
        
        # F键
        if pygame.K_F1 <= key <= pygame.K_F12:
            return f'F{key - pygame.K_F1 + 1}'
        
        # 其他
        return pygame.key.name(key).upper()
    
    def get_action_name(self, action: str) -> str:
        """获取动作的中文名称"""
        return self.ACTION_NAMES.get(action, action)
    
    def get_all_actions(self) -> List[str]:
        """获取所有可绑定的动作"""
        return list(self.DEFAULT_BINDINGS.keys())
