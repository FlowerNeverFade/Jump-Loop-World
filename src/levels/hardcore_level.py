"""
变态模式关卡生成器
AI辅助生成: 实现多层复式结构的复杂关卡

变态模式特点：
- 多层平台结构
- 新敌人类型
- 危险障碍物
- 更长更复杂的关卡
"""

import pygame
import random
from typing import List, Dict, Optional, TYPE_CHECKING

from .tiles import Tile, TileType, QuestionTile, BrickTile
from ..entities.enemies.goomba import Goomba
from ..entities.enemies.koopa import Koopa
from ..entities.enemies.flapper import Flapper
from ..entities.enemies.jumper import Jumper
from ..entities.enemies.shooter import Shooter
from ..entities.enemies.ghost import Ghost
from ..entities.enemies.giant import Giant
from ..entities.enemies.spikeball import SpikeBall
from ..entities.enemies.enemy import SafeZone
from ..entities.obstacles.spring import Spring
from ..entities.obstacles.laser import Laser
from ..entities.obstacles.saw import MovingSaw
from ..entities.items.coin import Coin
from ..settings import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
from .camera import Camera
from ..core.event_system import EventSystem, GameEvent
from ..core.resource_manager import ResourceManager

if TYPE_CHECKING:
    from ..entities.player import Player


class HardcoreLevel:
    """
    变态模式关卡类
    
    生成多层复式结构的复杂关卡。
    """
    
    def __init__(self):
        self.width = 0
        self.height = 0
        self.pixel_width = 0
        self.pixel_height = 0
        
        self.tiles: List[Tile] = []
        self.enemies: List = []
        self.items: List = []
        self.obstacles: List = []  # 新增：障碍物列表
        
        self.player_start = (64, 400)
        self.goal_position = (2000, 400)
        
        self.camera: Optional[Camera] = None
        self.solid_rects: List[pygame.Rect] = []
        
        # 安全区域（敌人禁入区域，如出生点）
        self.safe_zones: List[SafeZone] = []
        
        # 订阅事件
        EventSystem().subscribe(GameEvent.BLOCK_HIT, self._on_block_hit)
    
    def _on_block_hit(self, data: dict) -> None:
        """处理方块被击中事件"""
        pass
    
    def load_level(self) -> None:
        """生成变态模式关卡"""
        # 更长的关卡
        self.width = random.randint(150, 200)
        self.height = 20  # 更高以支持多层
        self.pixel_width = self.width * TILE_SIZE
        self.pixel_height = self.height * TILE_SIZE
        
        # 创建摄像机
        self.camera = Camera(self.pixel_width, self.pixel_height)
        
        # 定义多个层级（适配屏幕高度，确保可见）
        floors = [
            {'y': 13, 'name': 'ground'},      # 地面层（屏幕下方）
            {'y': 10, 'name': 'middle'},      # 中间层
            {'y': 7, 'name': 'upper'},        # 上层
            {'y': 4, 'name': 'top'},          # 顶层
        ]
        
        # 生成每一层
        for floor in floors:
            self._generate_floor(floor['y'], floor['name'])
        
        # 生成连接各层的楼梯/平台
        self._generate_connectors(floors)
        
        # 生成危险障碍物
        self._generate_obstacles(floors)
        
        # 生成敌人（各种类型）
        self._spawn_hardcore_enemies(floors)
        
        # 生成金币
        self._spawn_coins(floors)
        
        # 设置玩家起始位置（在地面层）
        from ..settings import PLAYER_HEIGHT
        ground_y = floors[0]['y']
        self.player_start = (3 * TILE_SIZE, ground_y * TILE_SIZE - PLAYER_HEIGHT)
        
        # 设置终点
        self.goal_position = ((self.width - 5) * TILE_SIZE, ground_y * TILE_SIZE)
        
        # 创建安全区域并下发给所有敌人（出生点附近禁止进入）
        self._create_safe_zones()
        for enemy in self.enemies:
            # 幽灵也需要设置安全区（它自定义了移动逻辑）
            enemy.set_safe_zones(self.safe_zones)
        
        # 更新碰撞矩形
        self._update_solid_rects()
        
        # 初始化摄像机位置到玩家起始位置
        if self.camera:
            self.camera.set_position(
                self.player_start[0] - SCREEN_WIDTH * 0.35,
                self.player_start[1] - SCREEN_HEIGHT * 0.5
            )

    def _create_safe_zones(self) -> None:
        """
        创建安全区域：出生点附近敌人不可进入
        """
        self.safe_zones.clear()
        spawn_x, spawn_y = self.player_start
        
        # 安全区域：出生点左2格到右8格，高度覆盖玩家可活动范围
        safe_x = spawn_x - 2 * TILE_SIZE
        safe_y = spawn_y - 4 * TILE_SIZE
        safe_width = 10 * TILE_SIZE
        safe_height = 8 * TILE_SIZE
        
        self.safe_zones.append(SafeZone(safe_x, safe_y, safe_width, safe_height))
    
    def _generate_floor(self, floor_y: int, floor_name: str) -> None:
        """生成一个楼层"""
        # 地面层是完整的
        if floor_name == 'ground':
            gaps = self._generate_gaps()
            for x in range(self.width):
                if x not in gaps:
                    tile = Tile(x, floor_y, TileType.GROUND)
                    self.tiles.append(tile)
                    # 地下填充
                    for dy in range(1, 4):
                        if floor_y + dy < self.height:
                            tile2 = Tile(x, floor_y + dy, TileType.GROUND)
                            self.tiles.append(tile2)
        else:
            # 其他层是分段的平台
            self._generate_platform_segments(floor_y, floor_name)
    
    def _generate_gaps(self) -> set:
        """生成地面间隙"""
        gaps = set()
        # 保护起始和结束区域
        safe_start = 10
        safe_end = self.width - 10
        
        num_gaps = random.randint(5, 10)
        for _ in range(num_gaps):
            gap_start = random.randint(safe_start, safe_end - 5)
            gap_width = random.randint(2, 4)
            for x in range(gap_start, min(gap_start + gap_width, safe_end)):
                gaps.add(x)
        
        return gaps
    
    def _generate_platform_segments(self, floor_y: int, floor_name: str) -> None:
        """生成平台段"""
        x = 5
        while x < self.width - 10:
            # 随机决定是否生成平台
            if random.random() < 0.6:
                platform_width = random.randint(4, 12)
                
                # 随机选择平台类型
                platform_type = random.choice(['brick', 'normal', 'ice'])
                
                for px in range(platform_width):
                    if x + px < self.width - 5:
                        if platform_type == 'brick':
                            tile = BrickTile(x + px, floor_y)
                        else:
                            tile = Tile(x + px, floor_y, TileType.GROUND)
                        self.tiles.append(tile)
                
                # 可能在平台上放问号块
                if random.random() < 0.3 and platform_width > 3:
                    qx = x + platform_width // 2
                    qy = floor_y - 3
                    question = QuestionTile(qx, qy, 'coin')
                    self.tiles.append(question)
                
                x += platform_width + random.randint(3, 8)
            else:
                x += random.randint(2, 5)
    
    def _generate_connectors(self, floors: List[Dict]) -> None:
        """生成连接各层的通道"""
        num_connectors = random.randint(8, 15)
        
        # 缓存固体瓦片占用格子，避免连接器/障碍物刷进砖块里
        solid_cells = {(t.grid_x, t.grid_y) for t in self.tiles if getattr(t, "solid", False)}
        
        for _ in range(num_connectors):
            x = random.randint(15, self.width - 20)
            
            # 随机选择连接哪两层
            floor_idx = random.randint(0, len(floors) - 2)
            lower_y = floors[floor_idx]['y']
            upper_y = floors[floor_idx + 1]['y']
            
            # 生成楼梯或垂直平台
            connector_type = random.choice(['stairs', 'platforms', 'spring'])
            
            if connector_type == 'stairs':
                # 楼梯
                step_count = lower_y - upper_y
                for step in range(step_count):
                    tile = Tile(x + step, lower_y - step - 1, TileType.GROUND)
                    self.tiles.append(tile)
            
            elif connector_type == 'platforms':
                # 垂直分布的小平台
                for py in range(upper_y + 1, lower_y, 2):
                    offset = random.randint(-1, 1)
                    tile = Tile(x + offset, py, TileType.GROUND)
                    self.tiles.append(tile)
            
            elif connector_type == 'spring':
                # 弹簧
                gx, gy = x, lower_y - 1
                # 不能放在砖块/平台/楼梯等固体格子里
                if (gx, gy) not in solid_cells:
                    spring = Spring(gx * TILE_SIZE, gy * TILE_SIZE)
                    self.obstacles.append(spring)
    
    def _generate_obstacles(self, floors: List[Dict]) -> None:
        """生成危险障碍物"""
        # 安全区域：玩家出生点附近不放置危险障碍物
        safe_zone_start = 0
        safe_zone_end = 12  # 前12格是安全区域
        
        # 固体瓦片占用格子（避免刷进砖块里）
        solid_cells = {(t.grid_x, t.grid_y) for t in self.tiles if getattr(t, "solid", False)}
        # 已放置障碍物占用格子（避免互相重叠）
        obstacle_cells = set()
        for ob in self.obstacles:
            gx = int(ob.x // TILE_SIZE)
            gy = int(ob.y // TILE_SIZE)
            obstacle_cells.add((gx, gy))
        
        # 激光发射器
        num_lasers = random.randint(3, 8)
        for _ in range(num_lasers):
            for _attempt in range(30):
                x = random.randint(safe_zone_end + 8, self.width - 25)
                floor = random.choice(floors[1:])  # 不放在地面
                y = floor['y'] - 2
                
                if (x, y) in solid_cells or (x, y) in obstacle_cells:
                    continue
                # 放激光时也要求下面一格有平台/砖块支撑，避免悬空塞进结构里
                if (x, y + 1) not in solid_cells:
                    continue
                
                direction = random.choice([-1, 1])
                laser = Laser(x * TILE_SIZE, y * TILE_SIZE, direction)
                self.obstacles.append(laser)
                obstacle_cells.add((x, y))
                break
        
        # 移动锯齿 - 远离出生点
        num_saws = random.randint(5, 12)
        for _ in range(num_saws):
            for _attempt in range(30):
                x = random.randint(safe_zone_end + 5, self.width - 20)
                floor = random.choice(floors)
                y = floor['y'] - 1
                
                if (x, y) in solid_cells or (x, y) in obstacle_cells:
                    continue
                if (x, y + 1) not in solid_cells:
                    continue
                
                vertical = random.random() < 0.3
                move_range = random.randint(3, 6)
                saw = MovingSaw(x * TILE_SIZE, y * TILE_SIZE, move_range, vertical)
                self.obstacles.append(saw)
                obstacle_cells.add((x, y))
                break
        
        # 弹簧 - 可以放近一些（不危险）
        num_springs = random.randint(5, 10)
        for _ in range(num_springs):
            for _attempt in range(30):
                x = random.randint(safe_zone_end, self.width - 15)
                floor = random.choice(floors)
                y = floor['y'] - 1
                
                if (x, y) in solid_cells or (x, y) in obstacle_cells:
                    continue
                # 弹簧必须放在平台/砖块上
                if (x, y + 1) not in solid_cells:
                    continue
                
                spring = Spring(x * TILE_SIZE, y * TILE_SIZE)
                self.obstacles.append(spring)
                obstacle_cells.add((x, y))
                break
    
    def _spawn_hardcore_enemies(self, floors: List[Dict]) -> None:
        """生成各种敌人"""
        # 安全区域：玩家出生点附近不放置敌人
        safe_zone_end = 15  # 前15格是安全区域
        
        enemy_types = [
            (Goomba, 15, 'ground'),      # 普通蘑菇怪
            (Koopa, 10, 'ground'),       # 乌龟
            (Flapper, 8, 'air'),         # 飞行怪
            (Jumper, 8, 'any'),          # 跳跃怪
            (Shooter, 5, 'platform'),    # 发射怪
            (Ghost, 4, 'any'),           # 幽灵
            (Giant, 3, 'ground'),        # 巨型怪
            (SpikeBall, 6, 'ground'),    # 滚动尖球
        ]
        
        for enemy_class, count, spawn_type in enemy_types:
            for _ in range(count):
                x = random.randint(safe_zone_end, self.width - 15)
                
                if spawn_type == 'ground':
                    y = floors[0]['y'] - 1
                elif spawn_type == 'air':
                    y = random.randint(floors[-1]['y'], floors[0]['y'] - 3)
                elif spawn_type == 'platform':
                    floor = random.choice(floors[1:])
                    y = floor['y'] - 1
                else:
                    floor = random.choice(floors)
                    y = floor['y'] - 1
                
                # 特殊处理巨型怪（需要更多空间）
                if enemy_class == Giant:
                    y = floors[0]['y'] - 2
                
                enemy = enemy_class(x * TILE_SIZE, y * TILE_SIZE)
                self.enemies.append(enemy)
    
    def _spawn_coins(self, floors: List[Dict]) -> None:
        """生成金币"""
        # 收集所有已占用的格子位置
        occupied = set()
        for tile in self.tiles:
            occupied.add((tile.grid_x, tile.grid_y))
            # 也标记方块上方一格为占用（避免金币生成在方块顶部边缘）
            occupied.add((tile.grid_x, tile.grid_y - 1))
        
        num_coins = random.randint(50, 100)
        placed = 0
        attempts = 0
        max_attempts = num_coins * 3
        
        while placed < num_coins and attempts < max_attempts:
            attempts += 1
            x = random.randint(5, self.width - 10)
            floor = random.choice(floors)
            y = floor['y'] - random.randint(2, 5)  # 生成在平台上方
            
            # 检查该位置是否被占用
            if (x, y) not in occupied:
                coin = Coin(x * TILE_SIZE + 4, y * TILE_SIZE + 4)
                self.items.append(coin)
                occupied.add((x, y))  # 标记该位置已被金币占用
                placed += 1
    
    def _update_solid_rects(self) -> None:
        """更新碰撞矩形列表"""
        self.solid_rects = [tile.rect for tile in self.tiles if tile.solid]
    
    def get_collision_tiles(self) -> List[pygame.Rect]:
        """获取碰撞瓦片"""
        return self.solid_rects
    
    def update(self, dt: float, player: 'Player', skip_camera: bool = False) -> None:
        """更新关卡"""
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
                enemy.check_edge(self.solid_rects)  # 边缘检测，防止掉坑
                
                # 设置目标玩家（针对追踪型敌人）
                if hasattr(enemy, 'set_target'):
                    enemy.set_target(player)
                
                # 更新发射怪的子弹
                if hasattr(enemy, 'update_bullets'):
                    enemy.update_bullets(self.solid_rects)
        
        # 更新道具
        for item in self.items:
            if item.active and not item.collected:
                item.update(dt)
                item.apply_collision(self.solid_rects)
        
        # 更新障碍物
        for obstacle in self.obstacles:
            if obstacle.active:
                obstacle.update(dt)
        
        self._update_solid_rects()
    
    def check_player_collisions(self, player: 'Player') -> None:
        """检查玩家碰撞"""
        # 与敌人碰撞
        for enemy in self.enemies:
            if not enemy.active or enemy.is_dead:
                continue
            
            if player.rect.colliderect(enemy.rect):
                if player.is_invincible() and player.state.name == 'INVINCIBLE':
                    enemy.kill()
                elif enemy.on_player_collision(player):
                    player.take_damage()
            
            # 检查发射怪的子弹
            if hasattr(enemy, 'check_bullet_hit_player'):
                if enemy.check_bullet_hit_player(player):
                    player.take_damage()
        
        # 与道具碰撞
        for item in self.items:
            if item.active and not item.collected:
                if player.rect.colliderect(item.rect) and item.auto_collect:
                    item.on_collect(player)
        
        # 与障碍物碰撞
        for obstacle in self.obstacles:
            if not obstacle.active:
                continue
            
            if isinstance(obstacle, Spring):
                obstacle.check_player_collision(player)
            elif isinstance(obstacle, (Laser, MovingSaw)):
                if obstacle.check_player_collision(player):
                    player.take_damage()
        
        # 检查是否到达终点
        goal_rect = pygame.Rect(
            self.goal_position[0], self.goal_position[1] - TILE_SIZE * 3,
            TILE_SIZE, TILE_SIZE * 3
        )
        if player.rect.colliderect(goal_rect):
            EventSystem().emit(GameEvent.LEVEL_COMPLETE)
    
    def check_tile_hits(self, player: 'Player') -> None:
        """检查玩家与方块的碰撞"""
        if player.velocity_y < 0:
            # 使用玩家的实际精灵位置（而不是碰撞框），因为碰撞框有向下偏移
            player_head_rect = pygame.Rect(
                player.rect.x + 2, 
                int(player.y),  # 使用精灵顶部位置
                player.rect.width - 4, 
                12  # 增大检测高度
            )
            for tile in self.tiles:
                if isinstance(tile, (QuestionTile, BrickTile)):
                    tile_bottom_rect = pygame.Rect(
                        tile.rect.x, tile.rect.bottom - 4, tile.rect.width, 8
                    )
                    if player_head_rect.colliderect(tile_bottom_rect):
                        tile.on_hit_from_below(player)
    
    def render(self, screen: pygame.Surface) -> None:
        """渲染关卡"""
        camera_offset = self.camera.get_offset() if self.camera else (0, 0)
        
        # 背景
        self._render_background(screen, camera_offset)
        
        # 渲染瓦片
        for tile in self.tiles:
            tile.render(screen, camera_offset)
        
        # 渲染道具
        for item in self.items:
            if item.active:
                item.render(screen, camera_offset)
        
        # 渲染障碍物
        for obstacle in self.obstacles:
            if obstacle.active:
                obstacle.render(screen, camera_offset)
        
        # 渲染敌人
        for enemy in self.enemies:
            if enemy.active:
                enemy.render(screen, camera_offset)
        
        # 渲染终点
        self._render_goal(screen, camera_offset)
    
    def _render_background(self, screen: pygame.Surface, camera_offset: tuple) -> None:
        """渲染背景（变态模式特殊背景 - 暗夜主题）"""
        # 使用渐变填充而不是画线
        screen.fill((20, 15, 40))  # 深紫色基底
        
        # 画一个大的渐变矩形
        gradient_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            # 从深紫到深蓝的渐变
            progress = y / SCREEN_HEIGHT
            r = int(20 + progress * 10)
            g = int(15 + progress * 20)
            b = int(40 + progress * 30)
            pygame.draw.line(gradient_surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        screen.blit(gradient_surface, (0, 0))
        
        # 添加星星效果（固定位置）
        star_positions = [
            (50, 30), (150, 80), (300, 50), (400, 100), (500, 40),
            (600, 90), (700, 60), (100, 150), (250, 130), (450, 160),
            (550, 120), (650, 140), (750, 110), (200, 200), (350, 180)
        ]
        for x, y in star_positions:
            pygame.draw.circle(screen, (150, 150, 180), (x % SCREEN_WIDTH, y), 2)
            pygame.draw.circle(screen, (200, 200, 220), (x % SCREEN_WIDTH, y), 1)
    
    def _render_goal(self, screen: pygame.Surface, camera_offset: tuple) -> None:
        """渲染终点"""
        rm = ResourceManager()
        flag = rm.load_image('tiles/flag.png')
        
        flag_height = flag.get_height() if flag else 96
        render_x = int(self.goal_position[0] - camera_offset[0])
        render_y = int(self.goal_position[1] - flag_height - camera_offset[1])
        
        if flag:
            screen.blit(flag, (render_x, render_y))
    
    def cleanup(self) -> None:
        """清理资源"""
        EventSystem().unsubscribe(GameEvent.BLOCK_HIT, self._on_block_hit)
        self.tiles.clear()
        self.enemies.clear()
        self.items.clear()
        self.obstacles.clear()
