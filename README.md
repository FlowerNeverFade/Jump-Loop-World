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

## 游戏操作

### 单人模式（两套按键均可使用）

| 按键 | 功能 |
|------|------|
| ← → 或 A D | 左右移动 |
| ↑ 或 W 或 空格 | 跳跃 |
| ↓ 或 S | 下蹲/下砸（需解锁） |
| Shift | 冲刺（需解锁） |
| H | 打开/关闭帮助面板 |
| ESC | 暂停/返回 |
| 鼠标点击右上角 ? | 打开帮助面板 |

### 双人模式

| 玩家 | 移动 | 跳跃 | 冲刺 |
|------|------|------|------|
| 玩家1 (红色) | WASD | W/空格 | 左Shift |
| 玩家2 (绿色) | 方向键 | ↑ | 右Shift |

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
├── main.py                     # 游戏入口
├── generate_sprites.py         # 精灵生成脚本
├── requirements.txt            # 依赖列表
├── README.md                   # 本文件
├── config/                     # 配置文件
│   └── key_bindings.json       # 按键绑定
├── saves/                      # 存档文件
├── docs/
│   └── design_document.md      # 设计文档
├── src/
│   ├── game.py                 # 游戏主类
│   ├── settings.py             # 配置常量
│   ├── core/                   # 核心模块
│   │   ├── state_machine.py    # 状态机
│   │   ├── resource_manager.py # 资源管理器
│   │   ├── event_system.py     # 事件系统
│   │   ├── save_manager.py     # 存档管理
│   │   ├── player_config.py    # 玩家配置
│   │   └── key_bindings.py     # 按键绑定
│   ├── entities/               # 实体模块
│   │   ├── entity.py           # 实体基类
│   │   ├── player.py           # 玩家类
│   │   ├── enemies/            # 敌人类
│   │   ├── items/              # 道具类
│   │   └── obstacles/          # 障碍物类
│   ├── levels/                 # 关卡模块
│   │   ├── level.py            # 普通关卡
│   │   ├── hardcore_level.py   # 变态模式关卡
│   │   └── camera.py           # 摄像机
│   ├── ui/                     # UI模块
│   │   ├── hud.py              # 游戏HUD
│   │   ├── menu.py             # 菜单
│   │   └── button.py           # 按钮
│   ├── states/                 # 游戏状态
│   │   ├── menu_state.py       # 主菜单
│   │   ├── play_state.py       # 游戏进行
│   │   ├── shop_state.py       # 商店
│   │   └── settings_state.py   # 设置
│   └── factories/              # 工厂类
└── assets/
    └── sprites/                # 精灵图资源
        ├── player/             # 玩家精灵
        ├── enemies/            # 敌人精灵
        ├── tiles/              # 地图方块
        ├── items/              # 道具
        └── obstacles/          # 障碍物
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
