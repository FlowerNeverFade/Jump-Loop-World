"""
关卡模块
AI辅助生成: 实现关卡加载和管理

此模块包含Level类，负责关卡数据的加载、实体管理和更新。
支持随机关卡生成。
"""

import pygame
import random
from typing import List, Dict, Any, Optional, TYPE_CHECKING

from .tiles import (
    Tile, TileType, BrickTile, QuestionTile, PipeTile, 
    SpikeTile, MovingPlatform
)
from .camera import Camera
from ..settings import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, DifficultySettings, PLAYER_HEIGHT
from ..core.resource_manager import ResourceManager
from ..core.event_system import EventSystem, GameEvent
from ..entities.player import Player
from ..entities.enemies.goomba import Goomba
from ..entities.enemies.koopa import Koopa
from ..entities.enemies.flapper import Flapper
from ..entities.enemies.enemy import SafeZone
from ..entities.items.coin import Coin, BlockCoin
from ..entities.items.mushroom import Mushroom, Star

if TYPE_CHECKING:
    from ..entities.enemies.enemy import Enemy
    from ..entities.items.item import Item


class Level:
    """
    关卡类
    
    管理关卡的所有元素：瓦片、敌人、道具等。
    
    Attributes:
        width: 关卡宽度（瓦片数）
        height: 关卡高度（瓦片数）
        tiles: 瓦片列表
        enemies: 敌人列表
        items: 道具列表
        player_start: 玩家起始位置
        goal_position: 终点位置
        camera: 摄像机
        difficulty: 难度设置
    """
    
    def __init__(self, difficulty: Dict = None):
        """
        初始化关卡
        
        Args:
            difficulty: 难度设置字典
        """
        self.width = 0
        self.height = 0
        self.pixel_width = 0
        self.pixel_height = 0
        
        self.tiles: List[Tile] = []
        self.enemies: List['Enemy'] = []
        self.items: List['Item'] = []
        
        self.solid_rects: List[pygame.Rect] = []  # 用于碰撞检测的矩形
        
        self.player_start = (64, 400)
        self.goal_position = (2000, 400)
        
        # 安全区域（敌人禁入区域，如复活点）
        self.safe_zones: List[SafeZone] = []
        
        self.camera: Optional[Camera] = None
        self.difficulty = difficulty or DifficultySettings.EASY
        
        # 订阅事件
        self._subscribe_events()
    
    def _subscribe_events(self) -> None:
        """订阅游戏事件"""
        EventSystem().subscribe(GameEvent.BLOCK_HIT, self._on_block_hit)
    
    def _on_block_hit(self, data: Dict) -> None:
        """处理方块被击中事件"""
        x, y = data.get('x', 0), data.get('y', 0)
        contains = data.get('contains', 'coin')
        
        # 在方块上方生成道具
        spawn_x = x
        spawn_y = y - TILE_SIZE
        
        if contains == 'coin':
            coin = BlockCoin(spawn_x + TILE_SIZE // 4, spawn_y)
            self.items.append(coin)
        elif contains == 'mushroom':
            mushroom = Mushroom(spawn_x, spawn_y)
            mushroom.spawn_from_block(y)
            self.items.append(mushroom)
        elif contains == 'star':
            star = Star(spawn_x, spawn_y)
            star.spawn_from_block(y)
            self.items.append(star)
    
    def load_default_level(self) -> None:
        """
        加载随机生成的关卡
        
        AI辅助生成: 程序化随机生成关卡
        每次加载都会生成不同的关卡布局
        """
        self.width = random.randint(80, 120)  # 随机关卡长度
        self.height = 15
        self.pixel_width = self.width * TILE_SIZE
        self.pixel_height = self.height * TILE_SIZE
        
        # 创建摄像机
        self.camera = Camera(self.pixel_width, self.pixel_height)
        
        # 地面在第12行
        ground_y = 12
        
        # 随机生成地面间隙
        gap_positions = self._generate_random_gaps(ground_y)
        
        # 生成地面
        for x in range(self.width):
            if x in gap_positions:
                continue  # 间隙
            
            tile = Tile(x, ground_y, TileType.GROUND)
            self.tiles.append(tile)
            
            # 地下添加两层
            tile2 = Tile(x, ground_y + 1, TileType.GROUND)
            self.tiles.append(tile2)
            tile3 = Tile(x, ground_y + 2, TileType.GROUND)
            self.tiles.append(tile3)
        
        # 随机生成平台
        self._generate_random_platforms(ground_y, gap_positions)
        
        # 先生成管道（这样问号块可以避开管道）
        self._generate_random_pipes(ground_y, gap_positions)
        
        # 再生成问号块（检查管道位置）
        self._generate_random_question_blocks(ground_y)
        
        # 困难模式添加尖刺和移动平台
        if self.difficulty.get('has_traps', False):
            self._generate_traps(ground_y, gap_positions)
        
        # 生成敌人（随机位置）
        self._spawn_enemies_random(ground_y, gap_positions)
        
        # 生成金币（随机位置）
        self._spawn_coins_random(ground_y)
        
        # 设置玩家起始位置
        from ..settings import PLAYER_HEIGHT
        self.player_start = (2 * TILE_SIZE, ground_y * TILE_SIZE - PLAYER_HEIGHT)
        
        # 设置终点（旗子底部在地面上）
        self.goal_position = ((self.width - 5) * TILE_SIZE, ground_y * TILE_SIZE)
        
        # 更新实体碰撞矩形
        self._update_solid_rects()
    
    def _generate_random_gaps(self, ground_y: int) -> set:
        """随机生成地面间隙位置"""
        gaps = set()
        # 保护起始区域（前10格不生成间隙）
        # 保护终点区域（后10格不生成间隙）
        safe_start = 10
        safe_end = self.width - 10
        
        # 根据难度决定间隙数量
        if self.difficulty.get('has_traps', False):
            num_gaps = random.randint(4, 6)
            gap_width = 2
        else:
            num_gaps = random.randint(2, 4)
            gap_width = 2
        
        for _ in range(num_gaps):
            # 随机位置，避免重叠
            attempts = 0
            while attempts < 20:
                gap_start = random.randint(safe_start, safe_end - gap_width)
                # 检查是否与已有间隙重叠（保持间隙间距至少8格）
                overlaps = False
                for g in gaps:
                    if abs(gap_start - g) < 8:
                        overlaps = True
                        break
                if not overlaps:
                    for i in range(gap_width):
                        gaps.add(gap_start + i)
                    break
                attempts += 1
        
        return gaps
    
    def _generate_random_platforms(self, ground_y: int, gaps: set) -> None:
        """随机生成砖块平台（使用固定高度层级）"""
        # 定义平台可以出现的高度层级（跳跃可达的高度）
        platform_heights = [
            ground_y - 3,  # 低层平台（容易跳上）
            ground_y - 4,  # 中层平台
            ground_y - 5,  # 高层平台（需要从其他平台跳）
        ]
        
        num_platforms = random.randint(3, 6)
        used_positions = set()
        
        for _ in range(num_platforms):
            attempts = 0
            while attempts < 30:
                px = random.randint(12, self.width - 15)
                # 选择一个固定高度层级
                py = random.choice(platform_heights)
                length = random.randint(4, 8)  # 平台至少4格长
                
                # 检查是否与已有平台重叠或太近
                overlaps = False
                for pos in used_positions:
                    if abs(px - pos[0]) < length + 3 and abs(py - pos[1]) < 2:
                        overlaps = True
                        break
                
                # 检查是否会放在间隙上方（这样不好跳）
                in_gap = any(g in range(px, px + length) for g in gaps)
                
                if not overlaps and not in_gap:
                    used_positions.add((px, py))
                    for i in range(length):
                        if px + i < self.width - 5:
                            brick = BrickTile(px + i, py)
                            self.tiles.append(brick)
                    break
                attempts += 1
    
    def _generate_random_question_blocks(self, ground_y: int) -> None:
        """随机生成问号块（放在合理高度，避开管道）"""
        # 问号块的固定高度（玩家跳跃能够到的高度）
        block_height = ground_y - 3  # 固定在地面上方3格
        
        num_blocks = random.randint(4, 7)
        item_types = ['coin', 'coin', 'coin', 'mushroom', 'star']
        
        # 收集已有方块的位置（包括管道周围区域）
        occupied = set()
        for tile in self.tiles:
            occupied.add((tile.grid_x, tile.grid_y))
            # 如果是管道，标记周围区域也不能放置（管道是2格宽）
            if hasattr(tile, 'tile_type') and 'PIPE' in str(tile.tile_type):
                # 标记管道左右各1格也不能放
                occupied.add((tile.grid_x - 1, tile.grid_y))
                occupied.add((tile.grid_x + 1, tile.grid_y))
                occupied.add((tile.grid_x + 2, tile.grid_y))
        
        placed = 0
        attempts = 0
        while placed < num_blocks and attempts < 50:
            qx = random.randint(10, self.width - 15)
            qy = block_height
            
            # 检查位置是否已被占用（检查上下左右范围）
            area_clear = True
            for dx in range(-1, 3):  # 检查左右各1格和右边2格（管道宽度）
                for dy in range(-2, 3):  # 检查上下范围
                    if (qx + dx, qy + dy) in occupied:
                        area_clear = False
                        break
                if not area_clear:
                    break
            
            if area_clear:
                occupied.add((qx, qy))
                contains = random.choice(item_types)
                question = QuestionTile(qx, qy, contains)
                self.tiles.append(question)
                placed += 1
            
            attempts += 1
    
    def _generate_random_pipes(self, ground_y: int, gaps: set) -> None:
        """随机生成管道"""
        num_pipes = random.randint(3, 6)
        used_positions = set()
        
        for _ in range(num_pipes):
            attempts = 0
            while attempts < 30:
                px = random.randint(12, self.width - 15)
                
                # 检查是否在间隙上或与其他管道重叠
                valid = True
                if px in gaps or (px + 1) in gaps:
                    valid = False
                for pos in used_positions:
                    if abs(px - pos) < 10:
                        valid = False
                        break
                
                if valid:
                    used_positions.add(px)
                    # 随机管道高度 (1-3格)
                    pipe_height = random.randint(1, 3)
                    
                    # 管道顶部
                    self.tiles.append(PipeTile(px, ground_y - pipe_height - 1, is_top=True, is_left=True))
                    self.tiles.append(PipeTile(px + 1, ground_y - pipe_height - 1, is_top=True, is_left=False))
                    
                    # 管道主体
                    for h in range(pipe_height):
                        self.tiles.append(PipeTile(px, ground_y - pipe_height + h, is_top=False, is_left=True))
                        self.tiles.append(PipeTile(px + 1, ground_y - pipe_height + h, is_top=False, is_left=False))
                    break
                attempts += 1
    
    def _generate_traps(self, ground_y: int, gaps: set) -> None:
        """生成陷阱（困难模式）"""
        # 随机尖刺
        num_spikes = random.randint(3, 6)
        used_positions = set()
        
        for _ in range(num_spikes):
            attempts = 0
            while attempts < 30:
                sx = random.randint(15, self.width - 15)
                if sx not in gaps and sx not in used_positions:
                    # 确保尖刺周围有足够空间
                    if all(abs(sx - pos) >= 5 for pos in used_positions):
                        used_positions.add(sx)
                        spike = SpikeTile(sx, ground_y - 1, blinks=random.choice([True, False]))
                        self.tiles.append(spike)
                        break
                attempts += 1
        
        # 在间隙上方添加移动平台
        gap_list = sorted(list(gaps))
        if gap_list:
            # 找到间隙的起始位置
            gap_starts = []
            i = 0
            while i < len(gap_list):
                gap_starts.append(gap_list[i])
                # 跳过连续的间隙
                while i < len(gap_list) - 1 and gap_list[i + 1] == gap_list[i] + 1:
                    i += 1
                i += 1
            
            for gap_start in gap_starts:
                platform = MovingPlatform(
                    gap_start, ground_y - 3,
                    move_range=random.randint(2, 4),
                    horizontal=random.choice([True, False])
                )
                self.tiles.append(platform)
    
    def _spawn_enemies_random(self, ground_y: int, gaps: set) -> None:
        """随机生成敌人"""
        ground_top_y = ground_y * TILE_SIZE
        
        # 随机敌人数量
        num_goombas = random.randint(5, 10)
        num_koopas = random.randint(2, 5)
        
        speed_mult = self.difficulty.get('enemy_speed_multiplier', 1.0)
        used_positions = set()
        
        # 生成蘑菇怪
        for _ in range(num_goombas):
            attempts = 0
            while attempts < 30:
                pos = random.randint(10, self.width - 10)
                # 避开间隙、起始区域和已有敌人位置
                if pos not in gaps and pos not in used_positions and pos > 8:
                    if all(abs(pos - p) >= 4 for p in used_positions):
                        used_positions.add(pos)
                        goomba = Goomba(pos * TILE_SIZE, ground_top_y - TILE_SIZE)
                        goomba.apply_difficulty(speed_mult)
                        self.enemies.append(goomba)
                        break
                attempts += 1
        
        # 生成乌龟
        for _ in range(num_koopas):
            attempts = 0
            while attempts < 30:
                pos = random.randint(10, self.width - 10)
                if pos not in gaps and pos not in used_positions and pos > 8:
                    if all(abs(pos - p) >= 5 for p in used_positions):
                        used_positions.add(pos)
                        koopa = Koopa(pos * TILE_SIZE, ground_top_y - 40)
                        koopa.apply_difficulty(speed_mult)
                        self.enemies.append(koopa)
                        break
                attempts += 1
        
        # 困难模式添加飞行怪
        if self.difficulty.get('has_traps', False):
            num_flappers = random.randint(2, 4)
            for _ in range(num_flappers):
                pos = random.randint(20, self.width - 20)
                flapper = Flapper(pos * TILE_SIZE, ground_top_y - random.randint(3, 5) * TILE_SIZE)
                flapper.apply_difficulty(speed_mult)
                self.enemies.append(flapper)
        
        # 创建安全区域
        self._create_safe_zones()
        
        # 将安全区域设置给所有敌人
        for enemy in self.enemies:
            enemy.set_safe_zones(self.safe_zones)
    
    def _spawn_coins_random(self, ground_y: int) -> None:
        """随机生成金币（确保不会生成在方块内）"""
        num_coin_groups = random.randint(5, 10)
        used_positions = set()
        
        # 获取所有方块占用的网格位置
        occupied_tiles = set()
        for tile in self.tiles:
            # 使用网格坐标
            occupied_tiles.add((tile.grid_x, tile.grid_y))
        
        for _ in range(num_coin_groups):
            attempts = 0
            while attempts < 30:
                cx = random.randint(5, self.width - 10)
                cy = random.randint(ground_y - 6, ground_y - 2)
                
                # 检查是否与方块重叠
                if (cx, cy) in occupied_tiles:
                    attempts += 1
                    continue
                
                if (cx, cy) not in used_positions:
                    used_positions.add((cx, cy))
                    # 每组1-4个金币，但要检查每个位置是否被占用
                    group_size = random.randint(1, 4)
                    coins_spawned = 0
                    for i in range(group_size):
                        coin_x = cx + i
                        # 检查每个金币位置是否有效
                        if (coin_x < self.width - 5 and 
                            (coin_x, cy) not in occupied_tiles and
                            (coin_x, cy) not in used_positions):
                            coin = Coin(coin_x * TILE_SIZE + 4, cy * TILE_SIZE + 4)
                            self.items.append(coin)
                            coins_spawned += 1
                    
                    # 只有成功生成了金币才算成功
                    if coins_spawned > 0:
                        break
                attempts += 1
    
    
    def _create_safe_zones(self) -> None:
        """
        创建安全区域
        AI辅助生成: 在玩家复活点周围创建禁入区域，防止敌人堵点
        """
        # 复活点安全区域：以玩家起始位置为中心，向左右各扩展一定距离
        spawn_x, spawn_y = self.player_start
        
        # 安全区域：复活点左边2格到右边3格，高度覆盖玩家跳跃范围
        safe_width = 5 * TILE_SIZE  # 5格宽
        safe_height = 4 * TILE_SIZE  # 4格高
        safe_x = spawn_x - TILE_SIZE  # 向左1格
        safe_y = spawn_y - 2 * TILE_SIZE  # 向上2格
        
        spawn_safe_zone = SafeZone(safe_x, safe_y, safe_width, safe_height)
        self.safe_zones.append(spawn_safe_zone)
    
    
    def _update_solid_rects(self) -> None:
        """更新用于碰撞检测的实体矩形列表"""
        self.solid_rects.clear()
        for tile in self.tiles:
            if tile.solid:
                self.solid_rects.append(tile.rect)
    
    def update(self, dt: float, player: Player, skip_camera: bool = False) -> None:
        """
        更新关卡
        
        Args:
            dt: 时间增量
            player: 玩家实例
            skip_camera: 是否跳过摄像机更新（双人模式时由外部处理）
        """
        # 更新摄像机
        if self.camera and not skip_camera:
            self.camera.update(player, dt)
        
        # 更新瓦片
        for tile in self.tiles:
            tile.update(dt)
        
        # 更新敌人
        for enemy in self.enemies:
            if enemy.active:
                enemy.update(dt)
                enemy.apply_collision(self.solid_rects)
                enemy.check_edge(self.solid_rects)
        
        # 获取玩家位置和金币磁铁范围
        player_center_x = player.x + player.width / 2
        player_center_y = player.y + player.height / 2
        magnet_range = player.player_config.coin_magnet_range
        
        # 更新道具
        for item in self.items:
            if item.active and not item.collected:
                item.update(dt)
                item.apply_collision(self.solid_rects)
                
                # 金币磁铁效果
                if hasattr(item, 'update_magnet') and magnet_range > 0:
                    item.update_magnet(player_center_x, player_center_y, magnet_range)
        
        # 更新实体碰撞矩形（处理移动平台和破碎砖块）
        self._update_solid_rects()
    
    def check_tile_hits(self, player: Player) -> None:
        """
        检查玩家顶方块和下砸击碎砖块
        
        Args:
            player: 玩家实例
        """
        # 向上移动时顶方块
        if player.velocity_y < 0:
            # 检查玩家头顶与方块底部的碰撞
            # 使用玩家的实际精灵位置（而不是碰撞框），因为碰撞框有向下偏移
            player_head_rect = pygame.Rect(
                player.rect.x + 2, 
                int(player.y),  # 使用精灵顶部位置，而不是碰撞框位置
                player.rect.width - 4, 
                12  # 增大检测高度
            )
            
            for tile in self.tiles:
                if isinstance(tile, (QuestionTile, BrickTile)):
                    # 方块底部区域
                    tile_bottom_rect = pygame.Rect(
                        tile.rect.x,
                        tile.rect.bottom - 4,
                        tile.rect.width,
                        8
                    )
                    if player_head_rect.colliderect(tile_bottom_rect):
                        tile.on_hit_from_below(player)
        
        # 下砸时检查脚下的砖块
        if player.is_ground_pounding and player.velocity_y > 0:
            # 检查玩家脚底与砖块顶部的碰撞
            player_feet_rect = pygame.Rect(
                player.rect.x + 2,
                player.rect.bottom - 4,
                player.rect.width - 4,
                10
            )
            
            for tile in self.tiles:
                if isinstance(tile, BrickTile) and not tile.broken:
                    tile_top_rect = pygame.Rect(
                        tile.rect.x,
                        tile.rect.y,
                        tile.rect.width,
                        10
                    )
                    if player_feet_rect.colliderect(tile_top_rect):
                        tile.on_hit_from_above(player)
    
    def check_player_collisions(self, player: Player) -> None:
        """
        检查玩家与关卡元素的碰撞
        
        Args:
            player: 玩家实例
        """
        # 与敌人碰撞
        for enemy in self.enemies:
            if not enemy.active or enemy.is_dead:
                continue
            
            if player.rect.colliderect(enemy.rect):
                if player.is_invincible() and player.state.name == 'INVINCIBLE':
                    # 无敌状态直接击杀敌人
                    enemy.kill()
                elif enemy.on_player_collision(player):
                    # 玩家受伤
                    player.take_damage()
        
        # 与道具碰撞
        for item in self.items:
            if not item.active or item.collected:
                continue
            
            if player.rect.colliderect(item.rect) and item.auto_collect:
                item.on_collect(player)
        
        # 检查是否到达终点
        goal_rect = pygame.Rect(
            self.goal_position[0], self.goal_position[1] - TILE_SIZE * 3,
            TILE_SIZE, TILE_SIZE * 3
        )
        if player.rect.colliderect(goal_rect):
            EventSystem().emit(GameEvent.LEVEL_COMPLETE)
    
    def get_collision_tiles(self) -> List[pygame.Rect]:
        """获取碰撞瓦片列表"""
        return self.solid_rects
    
    def render(self, screen: pygame.Surface) -> None:
        """
        渲染关卡
        
        Args:
            screen: 渲染目标
        """
        if not self.camera:
            return
        
        camera_offset = self.camera.get_offset()
        
        # 渲染瓦片
        for tile in self.tiles:
            tile.render(screen, camera_offset)
        
        # 渲染道具
        for item in self.items:
            if item.active and not item.collected:
                item.render(screen, camera_offset)
        
        # 渲染敌人
        for enemy in self.enemies:
            if enemy.active:
                enemy.render(screen, camera_offset)
        
        # 渲染终点旗帜
        self._render_goal(screen, camera_offset)
    
    def _render_goal(self, screen: pygame.Surface, camera_offset: tuple) -> None:
        """渲染终点"""
        rm = ResourceManager()
        flag = rm.load_image('tiles/flag.png')
        
        # 旗子图片高度，底部对齐地面
        flag_height = flag.get_height() if flag else 96
        
        render_x = int(self.goal_position[0] - camera_offset[0])
        render_y = int(self.goal_position[1] - flag_height - camera_offset[1])
        
        screen.blit(flag, (render_x, render_y))
    
    def cleanup(self) -> None:
        """清理资源"""
        EventSystem().unsubscribe(GameEvent.BLOCK_HIT, self._on_block_hit)
        self.tiles.clear()
        self.enemies.clear()
        self.items.clear()
        self.solid_rects.clear()
