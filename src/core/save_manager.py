"""
存档管理模块
AI辅助生成: 实现游戏存档的保存、加载和管理功能

此模块使用单例模式确保全局只有一个存档管理器实例。
存档数据以JSON格式存储，支持无限数量的存档槽位。

设计模式: 单例模式 (Singleton Pattern)
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any

from ..settings import APP_NAME, get_user_data_dir


class SaveManager:
    """
    存档管理器类（单例）
    
    负责游戏存档的创建、保存、加载和删除。
    存档数据包括玩家配置、金币、升级、装备等。
    
    Attributes:
        save_dir: 存档目录路径
        saves: 已加载的存档数据缓存
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        
        # 存档目录
        if getattr(sys, "frozen", False):
            base_dir = get_user_data_dir(APP_NAME)
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.save_dir = os.path.join(base_dir, "saves")
        
        # 确保存档目录存在
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        
        # 存档缓存
        self.saves: Dict[str, Dict] = {}
        
        # 当前激活的存档ID
        self.current_save_id: Optional[str] = None
        
        # 加载所有存档元数据
        self._load_save_list()
    
    def _get_save_path(self, save_id: str) -> str:
        """获取存档文件路径"""
        return os.path.join(self.save_dir, f"{save_id}.json")
    
    def _load_save_list(self) -> None:
        """加载所有存档的元数据"""
        self.saves.clear()
        
        if not os.path.exists(self.save_dir):
            return
        
        for filename in os.listdir(self.save_dir):
            if filename.endswith('.json'):
                save_id = filename[:-5]  # 移除.json后缀
                try:
                    save_data = self.load_save(save_id)
                    if save_data:
                        self.saves[save_id] = save_data
                except Exception as e:
                    print(f"警告: 无法加载存档 '{save_id}': {e}")
    
    def get_save_list(self) -> List[Dict[str, Any]]:
        """
        获取所有存档的列表信息
        
        Returns:
            存档信息列表，包含id、名称、创建时间、游戏时间等
        """
        save_list = []
        for save_id, data in self.saves.items():
            save_info = {
                'id': save_id,
                'name': data.get('name', f'存档 {save_id}'),
                'created_at': data.get('created_at', '未知'),
                'last_played': data.get('last_played', '未知'),
                'play_time': data.get('play_time', 0),
                'total_coins': data.get('total_coins', 0),
                'level_reached': data.get('level_reached', 1),
            }
            save_list.append(save_info)
        
        # 按最后游玩时间排序
        save_list.sort(key=lambda x: x['last_played'], reverse=True)
        return save_list
    
    def create_new_save(self, name: str = None) -> str:
        """
        创建新存档
        
        Args:
            name: 存档名称（可选）
            
        Returns:
            新存档的ID
        """
        # 生成唯一ID（使用时间戳）
        save_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if name is None:
            name = f"存档 {len(self.saves) + 1}"
        
        # 创建默认存档数据
        save_data = self._create_default_save_data(save_id, name)
        
        # 保存到文件
        self._save_to_file(save_id, save_data)
        
        # 添加到缓存
        self.saves[save_id] = save_data
        
        return save_id
    
    def _create_default_save_data(self, save_id: str, name: str) -> Dict[str, Any]:
        """创建默认存档数据"""
        now = datetime.now().isoformat()
        
        return {
            'id': save_id,
            'name': name,
            'created_at': now,
            'last_played': now,
            'play_time': 0,  # 游戏时间（秒）
            
            # Roguelike 数据
            'total_coins': 0,  # 累计金币
            'current_run_coins': 0,  # 当前运行收集的金币
            'level_reached': 1,  # 到达的最高关卡
            'runs_completed': 0,  # 完成的运行次数
            'enemies_defeated': 0,  # 击败的敌人数
            
            # 玩家配置（灵敏度设置）
            'player_config': {
                'move_speed_multiplier': 1.0,  # 移动速度倍率 (0.5 - 2.0)
                'friction_multiplier': 1.0,     # 摩擦力倍率 (0.5 - 2.0)
                'jump_power_multiplier': 1.0,   # 跳跃力倍率 (0.5 - 1.5)
            },
            
            # 永久升级
            'upgrades': {
                'max_health': 0,        # 生命值上限提升
                'move_speed': 0,        # 移动速度提升等级
                'jump_height': 0,       # 跳跃高度提升等级
                'coin_magnet': 0,       # 金币吸引范围等级
                'invincible_time': 0,   # 无敌时间延长等级
            },
            
            # 特殊能力（解锁状态）
            'abilities': {
                'double_jump': False,   # 二段跳
                'dash': False,          # 冲刺
                'wall_jump': False,     # 踢墙跳
                'ground_pound': False,  # 下砸
            },
            
            # 装备槽
            'equipment': {
                'hat': None,           # 帽子
                'boots': None,         # 靴子
                'accessory': None,     # 饰品
            },
            
            # 已购买的物品（避免重复购买）
            'purchased_items': [],
            
            # 统计数据
            'statistics': {
                'total_jumps': 0,
                'total_deaths': 0,
                'max_combo': 0,
                'best_time': None,
            }
        }
    
    def load_save(self, save_id: str) -> Optional[Dict[str, Any]]:
        """
        加载指定存档
        
        Args:
            save_id: 存档ID
            
        Returns:
            存档数据，如果不存在返回None
        """
        save_path = self._get_save_path(save_id)
        
        if not os.path.exists(save_path):
            return None
        
        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except (json.JSONDecodeError, IOError) as e:
            print(f"错误: 读取存档失败 '{save_id}': {e}")
            return None
    
    def save_current(self) -> bool:
        """
        保存当前存档
        
        Returns:
            是否保存成功
        """
        if self.current_save_id is None:
            print("警告: 没有激活的存档")
            return False
        
        if self.current_save_id not in self.saves:
            print(f"警告: 存档 '{self.current_save_id}' 不存在")
            return False
        
        # 更新最后游玩时间
        self.saves[self.current_save_id]['last_played'] = datetime.now().isoformat()
        
        return self._save_to_file(self.current_save_id, self.saves[self.current_save_id])
    
    def _save_to_file(self, save_id: str, data: Dict[str, Any]) -> bool:
        """将存档数据保存到文件"""
        save_path = self._get_save_path(save_id)
        
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except IOError as e:
            print(f"错误: 保存存档失败 '{save_id}': {e}")
            return False
    
    def delete_save(self, save_id: str) -> bool:
        """
        删除指定存档
        
        Args:
            save_id: 存档ID
            
        Returns:
            是否删除成功
        """
        save_path = self._get_save_path(save_id)
        
        try:
            if os.path.exists(save_path):
                os.remove(save_path)
            
            if save_id in self.saves:
                del self.saves[save_id]
            
            if self.current_save_id == save_id:
                self.current_save_id = None
            
            return True
        except IOError as e:
            print(f"错误: 删除存档失败 '{save_id}': {e}")
            return False
    
    def set_current_save(self, save_id: str) -> bool:
        """
        设置当前激活的存档
        
        Args:
            save_id: 存档ID
            
        Returns:
            是否设置成功
        """
        if save_id not in self.saves:
            # 尝试加载
            data = self.load_save(save_id)
            if data is None:
                return False
            self.saves[save_id] = data
        
        self.current_save_id = save_id
        return True
    
    def get_current_save(self) -> Optional[Dict[str, Any]]:
        """获取当前存档数据"""
        if self.current_save_id is None:
            return None
        return self.saves.get(self.current_save_id)
    
    def clear_current_save(self) -> None:
        """清除当前激活的存档（用于双人模式等不需要存档的场景）"""
        self.current_save_id = None
    
    def update_current_save(self, updates: Dict[str, Any]) -> None:
        """
        更新当前存档的数据
        
        Args:
            updates: 要更新的数据字典
        """
        if self.current_save_id is None:
            return
        
        save_data = self.saves.get(self.current_save_id)
        if save_data is None:
            return
        
        # 递归更新嵌套字典
        self._deep_update(save_data, updates)
    
    def _deep_update(self, base: Dict, updates: Dict) -> None:
        """递归更新嵌套字典"""
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value
    
    def add_coins(self, amount: int) -> None:
        """添加金币到当前存档"""
        if self.current_save_id is None:
            return
        
        save_data = self.saves.get(self.current_save_id)
        if save_data:
            save_data['total_coins'] = save_data.get('total_coins', 0) + amount
            save_data['current_run_coins'] = save_data.get('current_run_coins', 0) + amount
    
    def spend_coins(self, amount: int) -> bool:
        """
        消费金币
        
        Args:
            amount: 消费数量
            
        Returns:
            是否消费成功
        """
        if self.current_save_id is None:
            return False
        
        save_data = self.saves.get(self.current_save_id)
        if save_data is None:
            return False
        
        current_coins = save_data.get('total_coins', 0)
        if current_coins < amount:
            return False
        
        save_data['total_coins'] = current_coins - amount
        return True
    
    def get_coins(self) -> int:
        """获取当前金币数量"""
        if self.current_save_id is None:
            return 0
        
        save_data = self.saves.get(self.current_save_id)
        if save_data is None:
            return 0
        
        return save_data.get('total_coins', 0)
    
    def unlock_ability(self, ability_name: str) -> bool:
        """解锁特殊能力"""
        if self.current_save_id is None:
            return False
        
        save_data = self.saves.get(self.current_save_id)
        if save_data is None:
            return False
        
        if ability_name in save_data.get('abilities', {}):
            save_data['abilities'][ability_name] = True
            return True
        
        return False
    
    def has_ability(self, ability_name: str) -> bool:
        """检查是否拥有某个能力"""
        if self.current_save_id is None:
            return False
        
        save_data = self.saves.get(self.current_save_id)
        if save_data is None:
            return False
        
        return save_data.get('abilities', {}).get(ability_name, False)
    
    def get_upgrade_level(self, upgrade_name: str) -> int:
        """获取升级等级"""
        if self.current_save_id is None:
            return 0
        
        save_data = self.saves.get(self.current_save_id)
        if save_data is None:
            return 0
        
        return save_data.get('upgrades', {}).get(upgrade_name, 0)
    
    def upgrade(self, upgrade_name: str) -> bool:
        """提升升级等级"""
        if self.current_save_id is None:
            return False
        
        save_data = self.saves.get(self.current_save_id)
        if save_data is None:
            return False
        
        if upgrade_name in save_data.get('upgrades', {}):
            save_data['upgrades'][upgrade_name] += 1
            return True
        
        return False
