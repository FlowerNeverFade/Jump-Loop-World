"""
游戏主类模块
AI辅助生成: 游戏的核心控制类，管理游戏循环

此模块实现了Game类，作为整个游戏的入口和控制中心。
负责初始化Pygame、管理游戏循环、协调各个子系统。

设计模式: 单例模式 (Singleton Pattern)
确保整个应用只有一个Game实例
"""

import pygame
import sys
from typing import Optional

from .settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
    DifficultySettings, Colors
)
from .core.state_machine import StateMachine
from .core.resource_manager import ResourceManager
from .core.event_system import EventSystem
from .core.audio_manager import AudioManager


class Game:
    """
    游戏主类 - 单例模式实现
    
    管理游戏的生命周期，包括初始化、游戏循环、资源清理。
    
    职责:
    - 初始化Pygame和游戏子系统
    - 运行主游戏循环
    - 处理全局事件（如退出）
    - 协调状态机、资源管理器等组件
    
    Attributes:
        screen: Pygame显示Surface
        clock: Pygame时钟对象
        running: 游戏运行标志
        state_machine: 状态机实例
        resource_manager: 资源管理器实例
        event_system: 事件系统实例
        difficulty: 当前难度设置
    """
    
    # 单例实例
    _instance = None
    
    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化游戏"""
        if self._initialized:
            return
        
        # 初始化Pygame
        try:
            # 降低音频延迟：必须在 pygame.init() 前调用
            try:
                pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=256)
            except Exception:
                pass
            pygame.init()
            pygame.display.set_caption(TITLE)
        except pygame.error as e:
            print(f"Pygame初始化失败: {e}")
            sys.exit(1)
        
        # 创建游戏窗口
        self.is_fullscreen = False
        
        # 游戏画布（固定大小，用于渲染所有游戏内容）
        self.game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # 全屏缩放参数
        self.scale_factor = 1.0
        self.render_offset = (0, 0)  # 居中偏移
        
        try:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        except pygame.error as e:
            print(f"无法创建游戏窗口: {e}")
            sys.exit(1)
        
        # 游戏时钟
        self.clock = pygame.time.Clock()
        
        # 运行状态
        self.running = True
        
        # 当前难度设置（默认简单模式）
        self.difficulty = DifficultySettings.EASY
        
        # 游戏数据
        self.score = 0
        self.lives = self.difficulty['player_lives']
        self.coins = 0
        
        # 双人模式标志（用于重新开始时恢复）
        self.two_player_mode = False
        
        # 初始化子系统
        self.resource_manager = ResourceManager()
        self.event_system = EventSystem()
        self.audio_manager = AudioManager()
        # 音频初始化失败会自动降级为静默模式，不影响游戏运行
        self.audio_manager.init()
        self.state_machine = StateMachine(self)
        
        # 注册游戏状态（延迟导入避免循环依赖）
        self._register_states()
        
        self._initialized = True
    
    def _register_states(self) -> None:
        """
        注册所有游戏状态
        
        AI辅助生成: 使用延迟导入避免循环依赖问题
        """
        # 延迟导入状态类
        from .states.menu_state import MenuState
        from .states.play_state import PlayState
        from .states.pause_state import PauseState
        from .states.game_over_state import GameOverState
        from .states.settings_state import SettingsState
        from .states.shop_state import ShopState
        from .states.save_select_state import SaveSelectState
        
        self.state_machine.register_state('menu', MenuState)
        self.state_machine.register_state('play', PlayState)
        self.state_machine.register_state('pause', PauseState)
        self.state_machine.register_state('game_over', GameOverState)
        self.state_machine.register_state('settings', SettingsState)
        self.state_machine.register_state('shop', ShopState)
        self.state_machine.register_state('save_select', SaveSelectState)
    
    def set_difficulty(self, difficulty: str) -> None:
        """
        设置游戏难度
        
        Args:
            difficulty: 难度字符串 ('easy', 'hard' 或 'hardcore')
        """
        if difficulty == 'easy':
            self.difficulty = DifficultySettings.EASY
        elif difficulty == 'hard':
            self.difficulty = DifficultySettings.HARD
        elif difficulty == 'hardcore':
            self.difficulty = DifficultySettings.HARDCORE
        else:
            print(f"未知难度: {difficulty}，使用默认简单模式")
            self.difficulty = DifficultySettings.EASY
        
        # 重置生命数
        self.lives = self.difficulty['player_lives']
    
    def reset_game_data(self) -> None:
        """重置游戏数据（开始新游戏时调用）"""
        from .core.player_config import PlayerConfig
        from .core.save_manager import SaveManager
        
        self.score = 0
        self.coins = 0
        
        # 基础生命数 + 生命强化升级提供的额外生命
        base_lives = self.difficulty['player_lives']
        
        # 加载存档中的升级和装备
        save_manager = SaveManager()
        save_data = save_manager.get_current_save()
        
        if save_data:
            # 应用升级和装备到配置
            config = PlayerConfig()
            config.apply_upgrades(save_data.get('upgrades', {}))
            config.apply_equipment(save_data.get('equipment', {}))
            
            # 添加额外生命
            extra_lives = config.extra_lives
            self.lives = base_lives + extra_lives
        else:
            self.lives = base_lives
    
    def add_score(self, points: int) -> None:
        """
        增加分数
        
        Args:
            points: 要增加的分数
        """
        self.score += points
        self.event_system.emit('score_update', {'score': self.score})
    
    def add_coins(self, count: int = 1) -> None:
        """
        增加金币
        
        Args:
            count: 金币数量
        """
        self.coins += count
        # 每100金币加一条命
        if self.coins >= 100:
            self.coins -= 100
            self.lives += 1
    
    def lose_life(self) -> bool:
        """
        失去一条生命
        
        Returns:
            如果还有生命返回True，否则返回False（游戏结束）
        """
        self.lives -= 1
        return self.lives > 0
    
    def run(self) -> None:
        """
        运行游戏主循环
        
        这是游戏的核心循环，按照固定帧率执行：
        1. 处理输入事件
        2. 更新游戏逻辑
        3. 渲染画面
        """
        # 预加载资源
        try:
            self.resource_manager.preload_all()
        except Exception as e:
            print(f"资源预加载警告: {e}")
        
        # 进入初始状态（菜单）
        self.state_machine.change_state('menu')
        
        # 主游戏循环
        while self.running:
            # 计算时间增量（秒）
            dt = self.clock.tick(FPS) / 1000.0
            
            # 处理事件
            self._handle_events()
            
            # 更新游戏状态
            self._update(dt)
            
            # 渲染画面
            self._render()
            
            # 更新显示
            pygame.display.flip()
        
        # 清理资源
        self._cleanup()
    
    def _handle_events(self) -> None:
        """处理Pygame事件"""
        for event in pygame.event.get():
            # 全局事件处理
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            # 全局快捷键
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # ESC键处理
                    current_state = self.state_machine.get_current_state_name()
                    if current_state == 'play':
                        self.state_machine.push_state('pause')
                    elif current_state == 'pause':
                        self.state_machine.pop_state()
                    elif current_state == 'menu':
                        self.running = False
                        return
            
            # 将事件传递给状态机
            self.state_machine.handle_event(event)
    
    def _update(self, dt: float) -> None:
        """
        更新游戏逻辑
        
        Args:
            dt: 时间增量（秒）
        """
        self.state_machine.update(dt)
    
    def _render(self) -> None:
        """渲染游戏画面"""
        # 渲染到游戏画布
        # 清屏（天空渐变色）
        self._draw_sky_gradient()
        
        # 渲染当前状态到游戏画布
        self.state_machine.render(self.game_surface)
        
        # 全屏模式下进行缩放
        if self.is_fullscreen:
            # 清空屏幕（黑边）
            self.screen.fill((0, 0, 0))
            
            # 缩放游戏画布
            scaled_w = int(SCREEN_WIDTH * self.scale_factor)
            scaled_h = int(SCREEN_HEIGHT * self.scale_factor)
            scaled_surface = pygame.transform.scale(self.game_surface, (scaled_w, scaled_h))
            
            # 居中绘制
            self.screen.blit(scaled_surface, self.render_offset)
        else:
            # 窗口模式直接绘制
            self.screen.blit(self.game_surface, (0, 0))
    
    def _draw_sky_gradient(self) -> None:
        """
        绘制天空渐变背景
        
        AI辅助生成: 创建从顶部到底部的渐变效果
        我添加了云朵和山丘装饰使背景更丰富
        """
        # 渲染目标是游戏画布
        target = self.game_surface
        
        # 绘制天空渐变
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(Colors.SKY_TOP[0] + (Colors.SKY_BOTTOM[0] - Colors.SKY_TOP[0]) * ratio)
            g = int(Colors.SKY_TOP[1] + (Colors.SKY_BOTTOM[1] - Colors.SKY_TOP[1]) * ratio)
            b = int(Colors.SKY_TOP[2] + (Colors.SKY_BOTTOM[2] - Colors.SKY_TOP[2]) * ratio)
            pygame.draw.line(target, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # 绘制远景山丘（深色）
        hill_color = (100, 140, 100)
        hill_positions = [(0, 320), (150, 300), (350, 330), (500, 290), (700, 320)]
        for hx, hy in hill_positions:
            points = [(hx - 80, SCREEN_HEIGHT), (hx, hy), (hx + 120, SCREEN_HEIGHT)]
            pygame.draw.polygon(target, hill_color, points)
        
        # 绘制近景山丘（浅色）
        hill_color2 = (120, 170, 120)
        hill_positions2 = [(80, 350), (280, 360), (480, 340), (650, 370)]
        for hx, hy in hill_positions2:
            points = [(hx - 100, SCREEN_HEIGHT), (hx, hy), (hx + 100, SCREEN_HEIGHT)]
            pygame.draw.polygon(target, hill_color2, points)
        
        # 绘制云朵
        cloud_color = (255, 255, 255)
        cloud_positions = [(100, 60), (300, 80), (550, 50), (750, 90)]
        for cx, cy in cloud_positions:
            # 云朵由多个圆组成
            pygame.draw.ellipse(target, cloud_color, (cx - 30, cy, 60, 30))
            pygame.draw.ellipse(target, cloud_color, (cx - 50, cy + 10, 50, 25))
            pygame.draw.ellipse(target, cloud_color, (cx + 10, cy + 8, 55, 28))
    
    def _cleanup(self) -> None:
        """清理资源并退出"""
        self.resource_manager.clear_cache()
        try:
            self.audio_manager.shutdown()
        except Exception:
            pass
        pygame.quit()
    
    def quit(self) -> None:
        """退出游戏"""
        self.running = False
    
    @classmethod
    def reset_instance(cls) -> None:
        """重置单例实例（主要用于测试）"""
        if cls._instance is not None:
            cls._instance._cleanup()
        cls._instance = None
