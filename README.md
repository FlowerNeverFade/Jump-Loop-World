# Jump Loop World

> 基于面向对象程序设计思想的马里奥风格平台跳跃游戏

## 项目概述

这是一款使用 Python + Pygame 开发的2D横版过关游戏，采用像素艺术风格。

### 游戏模式

- **冒险模式**：Roguelike玩法，包含商店升级系统，可购买永久强化、能力和装备
- **双人模式**：本地双人合作，共享屏幕，两个玩家一起闯关

### 难度设置

- **简单模式**：敌人较少，无陷阱，适合新手
- **困难模式**：敌人更多更快，有尖刺和移动平台
- **变态模式**：多层复式关卡，新敌人类型，危险障碍物

## 运行要求

- Python 3.8+
- Pygame 2.5+
- Pillow 10.0+

## 安装与运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 生成精灵图（首次运行需要）
python generate_sprites.py

# 3. 运行游戏
python main.py
```

## 打包为 Windows EXE

```powershell
# 1. 生成精灵图（首次打包需要）
python generate_sprites.py

# 2. 一键打包
.\build_exe.ps1
```

输出文件在 `dist\JumpLoopWorld.exe`。EXE 运行时的存档与配置保存在 `%LOCALAPPDATA%\JumpLoopWorld\`。

## 游戏操作

### 单人模式（两套按键均可使用）

| 按键 | 功能 |
|------|------|
| ← → 或 A D | 左右移动 |
| ↑ 或 W 或 空格 | 跳跃 |
| ↓ 或 S | 下蹲/下砸（需解锁） |
| Alt | 冲刺（需解锁） |
| H | 打开/关闭帮助面板 |
| ESC | 暂停/返回 |
| 鼠标点击右上角 ? | 打开帮助面板 |

### 双人模式

| 玩家 | 移动 | 跳跃 | 冲刺 |
|------|------|------|------|
| 玩家1 (红色) | WASD | W/空格 | 左Alt |
| 玩家2 (绿色) | 方向键 | ↑ | 右Alt |

## 游戏特性

### 商店系统（冒险模式）
- **升级**：移动速度、跳跃高度、生命上限、金币磁铁等
- **能力**：二段跳、冲刺、踢墙跳、下砸
- **装备**：帽子、鞋子、配饰（提供各种加成）

### 敌人类型
- 🍄 蘑菇怪（Goomba）：踩一下消灭
- 🐢 乌龟（Koopa）：踩一下变壳，再踩踢出
- 🦇 飞行怪（Flapper）：空中飞行
- 更多变态模式独有敌人...

### 道具
- ❓ 问号方块：顶出金币和道具
- 🍄 蘑菇：变大/增加生命
- ⭐ 无敌星：短暂无敌

### 帮助系统
游戏右上角有一个 **?** 图标，点击或按 **H** 键可打开帮助面板：
- 查看操作说明
- 了解敌人类型和特点
- 查看道具效果
- 使用左右方向键或点击面板翻页

## 项目结构

```
jump_loop_world/
├── main.py                     # 游戏入口，初始化游戏环境并启动主循环
├── build_exe.ps1               # Windows一键打包脚本，生成可执行文件
├── generate_sprites.py         # 精灵生成脚本，处理精灵图裁剪、格式化与批量加载
├── requirements.txt            # 项目依赖清单，记录pygame等第三方库版本信息
├── README.md                   # 项目说明文档，含功能、运行方式、设计思路等
├── config/                     # 配置文件目录，存储用户自定义设置
│   ├── key_bindings.json       # 按键绑定配置，支持自定义操作映射
│   └── audio_settings.json     # 音频设置，音量等参数配置
├── saves/                      # 存档文件目录，保存游戏进度数据
├── docs/
│   └── design_document.md      # 设计文档，记录架构、设计模式、核心逻辑等
├── src/
│   ├── game.py                 # 游戏主类，封装主循环、模块调度与全局状态管理
│   ├── settings.py             # 配置常量中心，管理重力、速度、尺寸等固定参数
│   ├── core/                   # 全局核心支撑模块
│   │   ├── state_machine.py    # 状态机实现，管控游戏/实体状态切换
│   │   ├── resource_manager.py # 单例资源管理器，统一加载缓存精灵、音效等资源
│   │   ├── event_system.py     # 事件分发系统，解耦实体间交互逻辑
│   │   ├── audio_manager.py    # 音频管理器，统一管理背景音乐和音效播放
│   │   ├── save_manager.py     # 存档管理器，处理游戏进度的保存与加载
│   │   ├── player_config.py    # 玩家配置管理，维护玩家永久属性与解锁状态
│   │   ├── roguelike_data.py   # Roguelike数据，管理随机事件与奖励配置
│   │   └── key_bindings.py     # 按键绑定管理，支持运行时修改按键映射
│   ├── entities/               # 游戏实体模块，封装所有可交互对象
│   │   ├── entity.py           # 所有实体的抽象基类，定义基础属性与接口
│   │   ├── player.py           # 玩家类，实现移动、跳跃、状态管理等核心行为
│   │   ├── enemies/            # 敌人类目录，包含各种敌人子类
│   │   │   ├── enemy.py        # 敌人基类，定义敌人通用行为
│   │   │   ├── goomba.py       # 蘑菇怪，基础敌人，踩一下消灭
│   │   │   ├── koopa.py        # 乌龟怪，可踩成龟壳并踢出
│   │   │   ├── flapper.py      # 飞行怪，空中飞行模式
│   │   │   ├── jumper.py       # 跳跃怪，周期性跳跃攻击
│   │   │   ├── shooter.py      # 射击怪，远程发射弹幕
│   │   │   ├── ghost.py        # 幽灵，可穿墙追踪玩家
│   │   │   ├── giant.py        # 巨人怪，高血量大体型
│   │   │   └── spikeball.py    # 刺球怪，接触即伤害
│   │   ├── items/              # 道具类目录，包含各种可拾取物品
│   │   │   ├── item.py         # 道具基类，定义拾取与效果接口
│   │   │   ├── coin.py         # 金币，增加分数与货币
│   │   │   └── mushroom.py     # 蘑菇，变大或增加生命
│   │   └── obstacles/          # 障碍物类目录，包含各种机关陷阱
│   │       ├── spring.py       # 弹簧，踩上去弹跳
│   │       ├── saw.py          # 锯齿，移动的伤害障碍
│   │       └── laser.py        # 激光，周期性发射光线
│   ├── levels/                 # 关卡模块，负责关卡加载、地图解析与进度控制
│   │   ├── level.py            # 普通关卡类，管理地图生成与实体布置
│   │   ├── hardcore_level.py   # 变态模式关卡，高难度随机生成
│   │   ├── camera.py           # 摄像机系统，处理视角跟随与边界限制
│   │   └── tiles.py            # 地图方块定义，各类型方块属性与行为
│   ├── ui/                     # 交互界面模块，实现菜单、计分板等UI交互
│   │   ├── ui_manager.py       # UI管理器，统一管理界面元素生命周期
│   │   ├── hud.py              # 游戏HUD，显示分数、生命、金币等信息
│   │   ├── menu.py             # 菜单组件，处理菜单布局与交互逻辑
│   │   ├── button.py           # 按钮组件，可点击的交互元素
│   │   └── slider.py           # 滑块组件，用于音量等数值调节
│   ├── states/                 # 游戏全局状态模块，管理游戏各阶段状态
│   │   ├── game_state.py       # 状态基类，定义状态生命周期接口
│   │   ├── menu_state.py       # 主菜单状态，游戏入口界面
│   │   ├── play_state.py       # 游戏进行状态，核心游戏逻辑执行
│   │   ├── pause_state.py      # 暂停状态，游戏暂停与恢复
│   │   ├── shop_state.py       # 商店状态，购买升级与道具
│   │   ├── settings_state.py   # 设置状态，调整游戏选项
│   │   ├── save_select_state.py # 存档选择状态，加载与管理存档
│   │   └── game_over_state.py  # 游戏结束状态，显示结算与重试
│   ├── graphics/               # 图形渲染模块，处理精灵绘制与特效
│   │   └── sprite_generator.py # 精灵生成器，动态创建精灵图像
│   └── factories/              # 工厂类模块，批量创建实例简化初始化
│       ├── entity_factory.py   # 实体工厂，创建敌人/道具/障碍物实例
│       └── level_factory.py    # 关卡工厂，生成关卡配置与布局
└── assets/
    ├── audio/                  # 音频资源目录
    │   ├── music/              # 背景音乐，游戏与菜单BGM
    │   └── sfx/                # 音效文件，跳跃、碰撞、拾取等
    └── sprites/                # 精灵图资源目录，存放可视化素材
        ├── player/             # 玩家精灵，各状态动画帧
        ├── enemies/            # 敌人精灵，各类型敌人图像
        ├── tiles/              # 地图方块，地形与装饰元素
        ├── items/              # 道具精灵，可拾取物品图像
        └── obstacles/          # 障碍物精灵，机关陷阱图像
```

## 设计模式应用

本项目应用了以下设计模式：

1. **单例模式** - Game、ResourceManager、EventSystem、PlayerConfig
2. **工厂模式** - EntityFactory、LevelFactory
3. **状态模式** - GameState及其子类（MenuState、PlayState、ShopState等）
4. **观察者模式** - EventSystem事件订阅与发布
5. **策略模式** - DifficultySettings难度配置

## AI辅助声明

本项目部分代码由AI辅助生成，所有AI生成的代码段均在文件头部和关键位置标注说明。AI生成的代码经过人工审核和修改以符合项目需求。

## 许可证

仅供学习使用
