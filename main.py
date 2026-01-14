#!/usr/bin/env python3
"""
Jump Loop World - 马里奥风格平台跳跃游戏
AI辅助生成: 游戏主入口

运行方式:
    python main.py

游戏模式:
    - 冒险模式: Roguelike玩法，商店升级系统，永久强化
    - 双人模式: 本地双人合作，共享屏幕

操作说明:
    单人模式:
        - 移动: WASD 或 方向键
        - 跳跃: W / 空格 / ↑
        - 下蹲/下砸: S / ↓
        - 冲刺: Shift（需解锁）
    
    双人模式:
        - 玩家1 (红色): WASD + 左Shift
        - 玩家2 (绿色): 方向键 + 右Shift
    
    帮助系统:
        - 点击右上角 ? 图标查看游戏帮助
        - 按 H 键打开/关闭帮助面板
        - 左右方向键或点击翻页

难度设置:
    - 简单模式: 敌人较少，无陷阱
    - 困难模式: 敌人更多更快，有尖刺和移动平台
    - 变态模式: 多层复式关卡，新敌人类型，危险障碍物

游戏特性:
    - 问号方块: 顶出金币和道具
    - 可解锁能力: 二段跳、冲刺、踢墙跳、下砸
    - 装备系统: 帽子、鞋子、配饰
    - 多种敌人: 蘑菇怪、乌龟、飞行怪等

面向对象设计:
    - 状态模式: 管理菜单、游戏、商店等状态
    - 工厂模式: 创建关卡和游戏实体
    - 单例模式: 资源管理器、事件系统
    - 观察者模式: 游戏事件通知
    - 策略模式: 难度配置
"""

import sys
import os

# 确保可以导入src包
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 在导入pygame前设置环境变量以隐藏pygame欢迎信息
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'


def main():
    """
    游戏主入口函数
    
    初始化游戏并运行主循环
    """
    try:
        # 导入游戏类
        from src.game import Game
        
        # 创建游戏实例
        game = Game()
        
        # 运行游戏
        game.run()
        
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保已安装所有依赖: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"游戏运行错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    print("=" * 50)
    print("Jump Loop World")
    print("面向对象程序设计游戏项目")
    print("=" * 50)
    print()
    
    main()
