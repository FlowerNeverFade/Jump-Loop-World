"""
游戏状态模块
AI辅助生成: 实现游戏进行中的状态

游戏状态是主要的游戏逻辑所在，处理玩家控制、关卡更新等。
支持单人和双人模式。
"""

import pygame
from typing import TYPE_CHECKING, Optional, List

from .game_state import GameState
from ..levels.level import Level
from ..levels.hardcore_level import HardcoreLevel
from ..entities.player import Player
from ..ui.hud import HUD
from ..settings import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
from ..core.event_system import EventSystem, GameEvent
from ..core.save_manager import SaveManager

if TYPE_CHECKING:
    from ..game import Game
    from ..core.state_machine import StateMachine


class PlayState(GameState):
    """
    游戏进行状态
    
    处理游戏的主要逻辑，包括玩家控制、碰撞检测、关卡更新等。
    支持单人和双人模式。
    """
    
    def __init__(self, game: 'Game', state_machine: 'StateMachine'):
        super().__init__(game, state_machine)
        
        self.level: Optional[Level] = None
        self.player: Optional[Player] = None
        self.player2: Optional[Player] = None  # 第二个玩家
        self.hud: Optional[HUD] = None
        
        # 双人模式
        self.two_player_mode = False
        
        # 变态模式
        self.hardcore_mode = False
        
        # 游戏状态
        self.paused = False
        self.level_complete = False
        self.game_over = False
        
        # 死亡后的重生计时器
        self.respawn_timer = 0.0
        self.respawn_delay = 2.0
        
        # 双人模式下的死亡状态
        self.player1_dead = False
        self.player2_dead = False
    
    def enter(self, **kwargs) -> None:
        """进入游戏状态"""
        # 游戏背景音乐
        try:
            self.game.audio_manager.play_music('game')
        except Exception:
            pass
        # 检查是否是双人模式
        self.two_player_mode = kwargs.get('two_player', False)
        
        # 保存双人模式状态到 Game 对象（用于重新开始时恢复）
        self.game.two_player_mode = self.two_player_mode
        
        # 双人模式清除当前存档，避免加载冒险模式的能力
        if self.two_player_mode:
            from ..core.save_manager import SaveManager
            SaveManager().clear_current_save()
        
        # 检查是否是变态模式
        self.hardcore_mode = kwargs.get('hardcore', False)
        
        # 创建关卡
        if self.hardcore_mode:
            self.level = HardcoreLevel()
            self.level.load_level()
        else:
            self.level = Level(self.game.difficulty)
            self.level.load_default_level()
        
        # 创建玩家1（红色，WASD控制）
        start_x, start_y = self.level.player_start
        self.player = Player(start_x, start_y, 'red', player_id=1, two_player_mode=self.two_player_mode)
        
        # 双人模式：创建玩家2（绿色，方向键控制）
        if self.two_player_mode:
            self.player2 = Player(start_x + 50, start_y, 'green', player_id=2, two_player_mode=True)
            self.player1_dead = False
            self.player2_dead = False
        
        # 创建HUD
        self.hud = HUD(self.game)
        
        # 订阅事件
        self._subscribe_events()
        
        # 重置状态
        self.level_complete = False
        self.game_over = False
        self.respawn_timer = 0.0
    
    def exit(self) -> None:
        """退出游戏状态"""
        # 取消订阅事件
        self._unsubscribe_events()
        
        # 清理资源
        if self.level:
            self.level.cleanup()
        
        self.level = None
        self.player = None
        self.player2 = None
        self.hud = None
    
    def _subscribe_events(self) -> None:
        """订阅游戏事件"""
        EventSystem().subscribe(GameEvent.PLAYER_DEATH, self._on_player_death)
        EventSystem().subscribe(GameEvent.LEVEL_COMPLETE, self._on_level_complete)
        EventSystem().subscribe(GameEvent.COIN_COLLECT, self._on_coin_collect)
        EventSystem().subscribe(GameEvent.ENEMY_STOMP, self._on_enemy_stomp)
        EventSystem().subscribe(GameEvent.ENEMY_DEATH, self._on_enemy_death)
        EventSystem().subscribe(GameEvent.ITEM_COLLECT, self._on_item_collect)
    
    def _unsubscribe_events(self) -> None:
        """取消订阅事件"""
        EventSystem().unsubscribe(GameEvent.PLAYER_DEATH, self._on_player_death)
        EventSystem().unsubscribe(GameEvent.LEVEL_COMPLETE, self._on_level_complete)
        EventSystem().unsubscribe(GameEvent.COIN_COLLECT, self._on_coin_collect)
        EventSystem().unsubscribe(GameEvent.ENEMY_STOMP, self._on_enemy_stomp)
        EventSystem().unsubscribe(GameEvent.ENEMY_DEATH, self._on_enemy_death)
        EventSystem().unsubscribe(GameEvent.ITEM_COLLECT, self._on_item_collect)
    
    def _on_player_death(self, data: dict) -> None:
        """处理玩家死亡事件"""
        if self.two_player_mode:
            # 双人模式：检查是哪个玩家死亡
            player = data.get('player')
            if player == self.player:
                self.player1_dead = True
            elif player == self.player2:
                self.player2_dead = True
            
            if self.player1_dead and self.player2_dead:
                # 双人模式：两个都死了，消耗一条命
                if not self.game.lose_life():
                    # 没有生命了，游戏结束
                    self.game_over = True
                    self.respawn_timer = self.respawn_delay
                else:
                    # 还有生命，准备重生
                    self.respawn_timer = self.respawn_delay
        else:
            # 单人模式
            if not self.game.lose_life():
                self.game_over = True
                self._save_run_coins(multiplier=0.5)
            else:
                self.respawn_timer = self.respawn_delay
    
    def _on_level_complete(self, data: dict) -> None:
        """处理通关事件"""
        self.level_complete = True
        self.game.add_score(5000)
        self._save_run_coins(multiplier=1.0, bonus=50)
    
    def _on_coin_collect(self, data: dict) -> None:
        """处理金币收集事件"""
        self.game.add_coins(data.get('value', 1))
        self.game.add_score(200)
    
    def _on_enemy_stomp(self, data: dict) -> None:
        """处理踩敌人事件"""
        score = data.get('score', 100)
        self.game.add_score(score)

    def _on_enemy_death(self, data: dict) -> None:
        """处理敌人死亡事件（例如：无敌/龟壳撞击击杀）"""
        score = data.get('score', 100)
        self.game.add_score(score)
    
    def _on_item_collect(self, data: dict) -> None:
        """处理道具收集事件"""
        score = data.get('score', 0)
        self.game.add_score(score)
    
    def _save_run_coins(self, multiplier: float = 1.0, bonus: int = 0) -> None:
        """保存本次运行收集的金币到存档"""
        save_manager = SaveManager()
        if save_manager.current_save_id is None:
            return
        
        collected_coins = self.game.coins
        final_coins = int(collected_coins * multiplier) + bonus
        
        if final_coins > 0:
            save_manager.add_coins(final_coins)
            save_manager.save_current()
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """处理事件"""
        if self.hud and self.hud.handle_event(event):
            return
    
    def update(self, dt: float) -> None:
        """更新游戏逻辑"""
        if self.game_over:
            self.respawn_timer -= dt
            if self.respawn_timer <= 0:
                self.state_machine.change_state('game_over', won=False)
            return
        
        if self.level_complete:
            self.respawn_timer -= dt
            if self.respawn_timer <= -1:
                self.state_machine.change_state('game_over', won=True)
            return
        
        # 处理重生
        if self.respawn_timer > 0:
            self.respawn_timer -= dt
            if self.respawn_timer <= 0:
                if self.two_player_mode:
                    # 双人模式：重生两个玩家
                    self._respawn_both_players()
                else:
                    self._respawn_player()
            return
        
        # 处理玩家输入
        keys = pygame.key.get_pressed()
        
        # 玩家1：WASD控制
        if self.player and self.player.active:
            self._handle_player1_input(keys)
        
        # 玩家2：方向键控制（双人模式）
        if self.two_player_mode and self.player2 and self.player2.active:
            self._handle_player2_input(keys)
        
        # 更新玩家1
        if self.player and self.player.active:
            self.player.update(dt)
            if self.level:
                self.level.check_tile_hits(self.player)
                collision_tiles = self.level.get_collision_tiles()
                self.player.apply_collision(
                    collision_tiles,
                    self.level.pixel_width,
                    self.level.pixel_height
                )
                # 双人模式：限制在摄像机范围内
                if self.two_player_mode:
                    self._constrain_player_to_camera(self.player)
        
        # 更新玩家2
        if self.two_player_mode and self.player2 and self.player2.active:
            self.player2.update(dt)
            if self.level:
                self.level.check_tile_hits(self.player2)
                collision_tiles = self.level.get_collision_tiles()
                self.player2.apply_collision(
                    collision_tiles,
                    self.level.pixel_width,
                    self.level.pixel_height
                )
                self._constrain_player_to_camera(self.player2)
        
        # 更新关卡
        if self.level and self.player:
            # 双人模式：手动更新摄像机跟随中心位置
            if self.two_player_mode and self.level.camera and self.player2:
                center = self._get_center_player()
                if center:
                    self.level.camera.update(center, dt)
                # 使用玩家1更新关卡逻辑（敌人AI等）
                self.level.update(dt, self.player, skip_camera=True)
            else:
                self.level.update(dt, self.player)
            
            if self.player.active:
                self.level.check_player_collisions(self.player)
            if self.two_player_mode and self.player2 and self.player2.active:
                self.level.check_player_collisions(self.player2)
    
    def _handle_player1_input(self, keys) -> None:
        """处理玩家1的输入（WASD）"""
        # 创建一个模拟的按键状态，只响应WASD和空格
        from ..core.key_bindings import KeyBindings
        key_bindings = KeyBindings()
        
        # 直接调用玩家的输入处理，使用默认绑定（包含WASD）
        self.player.handle_input(keys)
    
    def _handle_player2_input(self, keys) -> None:
        """处理玩家2的输入（方向键）"""
        from ..settings import PLAYER_ACCELERATION, JUMP_POWER, FRICTION, AIR_FRICTION, PLAYER_SPEED
        
        # 获取玩家2的配置
        effective_speed = PLAYER_SPEED
        effective_accel = PLAYER_ACCELERATION
        effective_jump = JUMP_POWER
        
        if self.player2.on_ground:
            effective_friction = FRICTION
        else:
            effective_friction = AIR_FRICTION
        
        # 方向键控制
        moving = False
        move_direction = 0
        
        if keys[pygame.K_LEFT]:
            move_direction = -1
            self.player2.facing_right = False
            moving = True
        elif keys[pygame.K_RIGHT]:
            move_direction = 1
            self.player2.facing_right = True
            moving = True
        
        if not self.player2.is_dashing:
            if moving:
                self.player2.velocity_x += effective_accel * move_direction
            
            if abs(self.player2.velocity_x) > effective_speed:
                self.player2.velocity_x = effective_speed if self.player2.velocity_x > 0 else -effective_speed
            
            if not moving:
                self.player2.velocity_x *= effective_friction
                if abs(self.player2.velocity_x) < 0.1:
                    self.player2.velocity_x = 0
        
        # 上键跳跃
        jump_pressed = keys[pygame.K_UP]
        
        if self.player2.on_ground:
            self.player2.can_jump = True
            if self.player2.has_double_jump:
                self.player2.air_jumps_remaining = 1
        
        if jump_pressed:
            if self.player2.on_ground and self.player2.can_jump:
                self.player2.velocity_y = effective_jump
                self.player2.is_jumping = True
                self.player2.can_jump = False
                self.player2.jump_held = True
                self.player2.jump_timer = 0.0
                self.player2.on_ground = False
            elif self.player2.has_double_jump and not self.player2.on_ground and self.player2.air_jumps_remaining > 0 and not self.player2.jump_held:
                self.player2.velocity_y = effective_jump * 0.85
                self.player2.is_jumping = True
                self.player2.air_jumps_remaining -= 1
                self.player2.jump_held = True
            elif self.player2.is_jumping and self.player2.jump_held:
                if self.player2.jump_timer < self.player2.max_jump_time and self.player2.velocity_y < 0:
                    self.player2.velocity_y = effective_jump * (1 - self.player2.jump_timer / self.player2.max_jump_time * 0.5)
        else:
            self.player2.jump_held = False
        
        # 下键下砸
        if self.player2.has_ground_pound and not self.player2.on_ground and keys[pygame.K_DOWN]:
            self.player2._start_ground_pound()
    
    def _get_center_player(self) -> Optional[Player]:
        """获取两个玩家中心位置的虚拟玩家（用于摄像机）"""
        if not self.player or not self.player2:
            return self.player or self.player2
        
        # 检查哪些玩家还活着
        p1_alive = self.player.active
        p2_alive = self.player2.active
        
        # 如果只有一个玩家存活，摄像机只跟随存活的玩家
        if p1_alive and not p2_alive:
            return self.player
        elif p2_alive and not p1_alive:
            return self.player2
        elif not p1_alive and not p2_alive:
            # 两个都死了，返回玩家1的位置（等待重生）
            return self.player
        
        # 两个玩家都存活，计算中心位置
        # 创建一个临时的位置对象
        class CenterPosition:
            def __init__(self, x, y, width, height):
                self.x = x
                self.y = y
                self.width = width
                self.height = height
                self.rect = pygame.Rect(x, y, width, height)
        
        center_x = (self.player.x + self.player2.x) / 2
        center_y = (self.player.y + self.player2.y) / 2
        
        return CenterPosition(center_x, center_y, self.player.width, self.player.height)
    
    def _constrain_player_to_camera(self, player: Player) -> None:
        """限制玩家在摄像机视野范围内"""
        if not self.level or not self.level.camera:
            return
        
        camera_offset = self.level.camera.get_offset()
        
        # 计算摄像机可视区域
        left_bound = camera_offset[0] + 10
        right_bound = camera_offset[0] + SCREEN_WIDTH - player.width - 10
        
        # 限制X坐标
        if player.x < left_bound:
            player.x = left_bound
            player.velocity_x = max(0, player.velocity_x)  # 阻止继续向左
        elif player.x > right_bound:
            player.x = right_bound
            player.velocity_x = min(0, player.velocity_x)  # 阻止继续向右
        
        player.update_rect()
    
    def _respawn_player(self) -> None:
        """重生玩家（单人模式）"""
        if self.player and self.level:
            start_x, start_y = self.level.player_start
            self.player.reset(start_x, start_y)
            
            if self.level.camera:
                self.level.camera.reset()
    
    def _respawn_both_players(self) -> None:
        """重生两个玩家（双人模式）"""
        if self.level:
            start_x, start_y = self.level.player_start
            
            # 重生玩家1
            if self.player:
                self.player.reset(start_x, start_y)
                self.player1_dead = False
            
            # 重生玩家2
            if self.player2:
                self.player2.reset(start_x + 50, start_y)
                self.player2_dead = False
            
            # 重置摄像机
            if self.level.camera:
                self.level.camera.reset()
    
    def render(self, screen: pygame.Surface) -> None:
        """渲染游戏画面"""
        # 渲染关卡
        if self.level:
            self.level.render(screen)
        
        # 渲染玩家
        camera_offset = (0, 0)
        if self.level and self.level.camera:
            camera_offset = self.level.camera.get_offset()
        
        if self.player:
            self.player.render(screen, camera_offset)
        
        if self.two_player_mode and self.player2:
            self.player2.render(screen, camera_offset)
        
        # 渲染HUD
        if self.hud:
            self.hud.render(screen)
        
        # 双人模式提示
        if self.two_player_mode:
            self._render_two_player_hints(screen)
        
        # 渲染特殊状态提示
        if self.game_over:
            self._render_game_over_overlay(screen)
        elif self.level_complete:
            self._render_victory_overlay(screen)
        elif self.respawn_timer > 0:
            self._render_respawn_overlay(screen)
    
    def _render_two_player_hints(self, screen: pygame.Surface) -> None:
        """渲染双人模式提示"""
        try:
            font = pygame.font.SysFont('microsoftyahei', 12)
        except:
            font = pygame.font.Font(None, 14)
        
        # 玩家1提示
        p1_text = font.render("P1: WASD+空格", True, (255, 100, 100))
        screen.blit(p1_text, (10, SCREEN_HEIGHT - 40))
        
        # 玩家2提示
        p2_text = font.render("P2: 方向键", True, (100, 255, 100))
        screen.blit(p2_text, (10, SCREEN_HEIGHT - 22))
    
    def _render_game_over_overlay(self, screen: pygame.Surface) -> None:
        """渲染游戏结束遮罩"""
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        try:
            font = pygame.font.SysFont('microsoftyahei', 48)
        except:
            font = pygame.font.Font(None, 56)
        
        text = font.render("游戏结束", True, (255, 100, 100))
        rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(text, rect)
    
    def _render_victory_overlay(self, screen: pygame.Surface) -> None:
        """渲染胜利遮罩"""
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((255, 215, 0, 100))
        screen.blit(overlay, (0, 0))
        
        try:
            font = pygame.font.SysFont('microsoftyahei', 48)
        except:
            font = pygame.font.Font(None, 56)
        
        text = font.render("恭喜通关!", True, (255, 255, 255))
        rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(text, rect)
    
    def _render_respawn_overlay(self, screen: pygame.Surface) -> None:
        """渲染重生等待遮罩"""
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))
        
        try:
            font = pygame.font.SysFont('microsoftyahei', 36)
        except:
            font = pygame.font.Font(None, 42)
        
        lives_text = f"剩余生命: {self.game.lives}"
        text = font.render(lives_text, True, (255, 255, 255))
        rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(text, rect)
