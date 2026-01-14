# Jump Loop World - 设计文档

## 目录

1. [需求分析](#1-需求分析)
2. [类设计](#2-类设计)
3. [代码实现](#3-代码实现)
4. [功能测试](#4-功能测试)
5. [设计模式应用](#5-设计模式应用)
6. [AI辅助说明](#6-ai辅助说明)

---

## 1. 需求分析

### 1.1 游戏选型说明

**游戏类型**：2D横版平台跳跃游戏（马里奥风格）

**选型理由**：
- 规则清晰：跳跃、移动、踩敌人、收集道具
- 逻辑简单：基于物理的跳跃和碰撞检测
- 适合OOP设计：实体类型多样，继承关系明确
- 可扩展性强：易于添加新敌人、道具、关卡

### 1.2 功能需求

#### 核心玩法
- [x] 玩家移动和跳跃（惯性系统）
- [x] 敌人AI巡逻和边缘检测
- [x] 踩敌人击杀机制
- [x] 道具收集系统
- [x] 分数和生命系统
- [x] 关卡通关判定
- [x] 随机生成关卡

#### 游戏模式
- [x] 冒险模式：Roguelike玩法，商店升级系统
- [x] 双人模式：本地双人合作，共享屏幕

#### 难度系统
- [x] 简单模式：敌人较少，无陷阱
- [x] 困难模式：敌人更多更快，有尖刺和移动平台
- [x] 变态模式：多层复式关卡，新敌人类型，危险障碍物

#### 商店系统（冒险模式）
- [x] 永久升级：移动速度、跳跃高度、生命上限等
- [x] 可解锁能力：二段跳、冲刺、踢墙跳、下砸
- [x] 装备系统：帽子、鞋子、配饰

#### 界面功能
- [x] 主菜单（模式选择）
- [x] 存档选择界面
- [x] 商店界面
- [x] 设置界面（按键绑定）
- [x] 游戏HUD（分数、金币、生命、难度）
- [x] 帮助面板
- [x] 游戏结束/胜利界面

### 1.3 非功能需求

- **性能**：稳定60FPS
- **可维护性**：模块化设计，代码规范
- **可扩展性**：易于添加新内容
- **健壮性**：完善的异常处理

---

## 2. 类设计

### 2.1 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                           Game (单例)                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │StateMachine │  │ResourceMgr │  │    EventSystem          │ │
│  └──────┬──────┘  └─────────────┘  └─────────────────────────┘ │
└─────────┼───────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                        GameState (抽象)                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐│
│  │MenuState │  │PlayState │  │PauseState│  │GameOverState    ││
│  └──────────┘  └────┬─────┘  └──────────┘  └──────────────────┘│
└─────────────────────┼───────────────────────────────────────────┘
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
    ┌──────────┐ ┌─────────┐ ┌──────────┐
    │  Level   │ │ Player  │ │   HUD    │
    └────┬─────┘ └─────────┘ └──────────┘
         │
    ┌────┴────┬──────────┐
    ▼         ▼          ▼
┌───────┐ ┌────────┐ ┌────────┐
│ Tiles │ │Enemies │ │ Items  │
└───────┘ └────────┘ └────────┘
```

### 2.2 核心类说明

#### 游戏核心层

| 类名 | 职责 | 设计模式 |
|------|------|----------|
| `Game` | 游戏主循环、全局资源管理 | 单例模式 |
| `StateMachine` | 管理游戏状态切换 | 状态模式 |
| `ResourceManager` | 资源加载与缓存 | 单例模式 |
| `EventSystem` | 事件发布与订阅 | 观察者模式 |

#### 实体层

| 类名 | 父类 | 职责 |
|------|------|------|
| `Entity` | - | 所有实体的抽象基类 |
| `AnimatedEntity` | Entity | 带动画的实体 |
| `Player` | AnimatedEntity | 玩家角色控制 |
| `Enemy` | AnimatedEntity | 敌人抽象基类 |
| `Goomba` | Enemy | 蘑菇怪敌人 |
| `Koopa` | Enemy | 乌龟壳怪敌人 |
| `Flapper` | Enemy | 飞行怪敌人 |
| `Item` | AnimatedEntity | 道具抽象基类 |
| `Coin` | Item | 金币道具 |
| `Mushroom` | Item | 变大蘑菇 |
| `Star` | Item | 无敌星星 |

#### 关卡层

| 类名 | 职责 |
|------|------|
| `Level` | 关卡数据与逻辑管理 |
| `Tile` | 瓦片基类 |
| `BrickTile` | 可打碎的砖块 |
| `QuestionTile` | 问号方块 |
| `SpikeTile` | 尖刺陷阱 |
| `MovingPlatform` | 移动平台 |
| `Camera` | 跟随摄像机 |

#### 工厂层

| 类名 | 职责 |
|------|------|
| `EntityFactory` | 创建敌人和道具实体 |
| `LevelFactory` | 创建关卡实例 |

### 2.3 UML类图

```
┌─────────────────────────────────────────────────────────────┐
│                         Entity                               │
├─────────────────────────────────────────────────────────────┤
│ - x: float                                                   │
│ - y: float                                                   │
│ - width: int                                                 │
│ - height: int                                                │
│ - velocity_x: float                                          │
│ - velocity_y: float                                          │
│ - active: bool                                               │
├─────────────────────────────────────────────────────────────┤
│ + update(dt: float): void                                    │
│ + render(screen: Surface, offset: tuple): void               │
│ + collides_with(other: Entity): bool                         │
└─────────────────────────────────────────────────────────────┘
                            △
                            │
              ┌─────────────┴─────────────┐
              │                           │
┌─────────────────────────┐  ┌─────────────────────────┐
│    AnimatedEntity       │  │         Tile            │
├─────────────────────────┤  ├─────────────────────────┤
│ - animations: dict      │  │ - tile_type: TileType   │
│ - current_animation     │  │ - solid: bool           │
│ - animation_frame       │  ├─────────────────────────┤
├─────────────────────────┤  │ + on_hit_from_below()   │
│ + add_animation()       │  └─────────────────────────┘
│ + play_animation()      │              △
│ + update_animation()    │              │
└─────────────────────────┘    ┌─────────┴─────────┐
          △                    │                   │
          │              ┌───────────┐      ┌───────────┐
    ┌─────┴─────┐        │BrickTile  │      │QuestionTile│
    │           │        └───────────┘      └───────────┘
┌───────┐  ┌────────┐
│Player │  │ Enemy  │
└───────┘  └────────┘
               △
               │
    ┌──────────┼──────────┐
    │          │          │
┌───────┐  ┌───────┐  ┌────────┐
│Goomba │  │Koopa  │  │Flapper │
└───────┘  └───────┘  └────────┘
```

---

## 3. 代码实现

### 3.1 项目结构

```
src/
├── __init__.py           # 包初始化
├── game.py               # 游戏主类 (200+ 行)
├── settings.py           # 配置常量 (150+ 行)
├── core/
│   ├── state_machine.py  # 状态机 (180+ 行)
│   ├── resource_manager.py # 资源管理 (250+ 行)
│   └── event_system.py   # 事件系统 (120+ 行)
├── entities/
│   ├── entity.py         # 实体基类 (200+ 行)
│   ├── player.py         # 玩家类 (280+ 行)
│   └── enemies/
│       ├── enemy.py      # 敌人基类 (180+ 行)
│       ├── goomba.py     # 蘑菇怪 (100+ 行)
│       ├── koopa.py      # 乌龟壳怪 (160+ 行)
│       └── flapper.py    # 飞行怪 (120+ 行)
├── levels/
│   ├── level.py          # 关卡类 (300+ 行)
│   ├── tiles.py          # 瓦片类 (280+ 行)
│   └── camera.py         # 摄像机 (100+ 行)
├── graphics/
│   └── sprite_generator.py # 精灵生成 (800+ 行)
├── ui/
│   ├── button.py         # 按钮组件 (120+ 行)
│   ├── hud.py            # 游戏HUD (100+ 行)
│   └── menu.py           # 菜单界面 (130+ 行)
└── states/
    ├── menu_state.py     # 菜单状态 (80+ 行)
    ├── play_state.py     # 游戏状态 (200+ 行)
    ├── pause_state.py    # 暂停状态 (60+ 行)
    └── game_over_state.py # 结束状态 (100+ 行)
```

### 3.2 核心代码示例

#### 状态模式实现

```python
# src/core/state_machine.py

class GameState(ABC):
    """游戏状态抽象基类"""
    
    @abstractmethod
    def enter(self, **kwargs) -> None:
        """进入状态时调用"""
        pass
    
    @abstractmethod
    def exit(self) -> None:
        """退出状态时调用"""
        pass
    
    @abstractmethod
    def update(self, dt: float) -> None:
        """更新状态逻辑"""
        pass
    
    @abstractmethod
    def render(self, screen: pygame.Surface) -> None:
        """渲染状态画面"""
        pass


class StateMachine:
    """状态机 - 管理游戏状态切换"""
    
    def change_state(self, state_name: str, **kwargs) -> None:
        """切换到指定状态"""
        if self.current_state:
            self.current_state.exit()
        
        state_class = self.states[state_name]
        self.current_state = state_class(self.game, self)
        self.current_state.enter(**kwargs)
```

#### 工厂模式实现

```python
# src/factories/entity_factory.py

class EntityFactory:
    """实体工厂 - 统一创建游戏实体"""
    
    ENEMY_TYPES = {
        'goomba': Goomba,
        'koopa': Koopa,
        'flapper': Flapper,
    }
    
    def create_enemy(self, enemy_type: str, x: float, y: float) -> Enemy:
        """根据类型创建敌人"""
        enemy_class = self.ENEMY_TYPES[enemy_type]
        enemy = enemy_class(x, y)
        enemy.apply_difficulty(self.difficulty_multiplier)
        return enemy
```

#### 观察者模式实现

```python
# src/core/event_system.py

class EventSystem:
    """事件系统 - 发布订阅模式"""
    
    def subscribe(self, event: GameEvent, callback: Callable) -> None:
        """订阅事件"""
        self._listeners[event].append(callback)
    
    def emit(self, event: GameEvent, data: dict = None) -> None:
        """发布事件"""
        for callback in self._listeners[event]:
            callback(data)
```

---

## 4. 功能测试

### 4.1 测试用例

| 测试项 | 预期结果 | 测试状态 |
|--------|----------|----------|
| 游戏启动 | 显示主菜单 | ✅ 通过 |
| 简单模式开始 | 进入游戏，敌人正常速度 | ✅ 通过 |
| 困难模式开始 | 进入游戏，敌人速度加倍，有飞行怪 | ✅ 通过 |
| 玩家移动 | 左右移动流畅 | ✅ 通过 |
| 玩家跳跃 | 跳跃高度正常，可变高跳 | ✅ 通过 |
| 踩敌人 | 敌人死亡，玩家反弹 | ✅ 通过 |
| 碰撞敌人 | 玩家受伤或死亡 | ✅ 通过 |
| 收集金币 | 金币数增加，分数增加 | ✅ 通过 |
| 顶问号块 | 弹出道具 | ✅ 通过 |
| 吃蘑菇 | 玩家变大 | ✅ 通过 |
| 吃星星 | 玩家无敌 | ✅ 通过 |
| 暂停游戏 | 按ESC暂停 | ✅ 通过 |
| 游戏结束 | 显示结果界面 | ✅ 通过 |
| 通关 | 显示胜利界面 | ✅ 通过 |

### 4.2 异常处理测试

| 异常场景 | 处理方式 | 测试状态 |
|----------|----------|----------|
| 精灵文件缺失 | 使用占位图形 | ✅ 通过 |
| 关卡文件损坏 | 加载默认关卡 | ✅ 通过 |
| 玩家越界 | 触发死亡 | ✅ 通过 |

---

## 5. 设计模式应用

### 5.1 单例模式 (Singleton)

**应用场景**：Game、ResourceManager、EventSystem

**解决问题**：确保全局只有一个实例，提供统一访问点

**代码实现**：
```python
class Game:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

### 5.2 工厂模式 (Factory)

**应用场景**：EntityFactory、LevelFactory

**解决问题**：解耦对象创建，便于扩展新类型

**扩展性体现**：添加新敌人只需在ENEMY_TYPES字典中注册

### 5.3 状态模式 (State)

**应用场景**：GameState及子类、PlayerState

**解决问题**：消除条件分支，状态行为封装

### 5.4 观察者模式 (Observer)

**应用场景**：EventSystem

**解决问题**：组件间松耦合通信

### 5.5 策略模式 (Strategy)

**应用场景**：DifficultySettings

**解决问题**：封装不同难度的配置策略

---

## 6. AI辅助说明

### 6.1 AI辅助范围

本项目使用AI辅助完成以下工作：

1. **架构设计**：类结构设计、模块划分
2. **代码生成**：基础框架代码、像素精灵生成算法
3. **文档编写**：README、设计文档

### 6.2 AI代码标注

所有AI生成的代码段均在文件头部或函数前添加如下标注：

```python
"""
模块名称
AI辅助生成: 功能说明

...
"""

def some_function():
    """
    函数说明
    
    AI辅助生成: 具体实现说明
    我修改了XXX逻辑以符合XXX原则
    """
    pass
```

### 6.3 人工修改说明

主要人工修改内容：

1. **碰撞检测优化**：调整AABB碰撞的分离轴判定逻辑
2. **动画系统**：修改动画帧切换时机和缓存机制
3. **难度平衡**：调整敌人参数和关卡布局
4. **UI美化**：调整颜色搭配和布局

---

## 附录

### A. 技术栈

- Python 3.8+
- Pygame 2.5+ (游戏引擎)
- Pillow 10.0+ (图像生成)

### B. 开发环境

- 操作系统：Windows 10/11
- IDE：任意Python IDE
- 版本控制：Git

### C. 参考资料

- Pygame官方文档
- 《游戏设计模式》
- 经典马里奥游戏机制分析
