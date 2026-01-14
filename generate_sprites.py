#!/usr/bin/env python3
"""
精灵生成脚本
AI辅助生成: 独立运行此脚本生成所有游戏精灵

运行方式:
    python generate_sprites.py

此脚本会在 assets/sprites/ 目录下生成所有游戏所需的像素精灵图。
所有精灵都是透明背景的PNG格式。
"""

import os
import sys

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.graphics.sprite_generator import PixelSpriteGenerator


def main():
    """主函数 - 生成所有精灵"""
    print("=" * 50)
    print("Jump Loop World - 精灵生成器")
    print("=" * 50)
    print()
    
    # 确定输出目录
    sprites_dir = os.path.join(project_root, 'assets', 'sprites')
    
    # 确保目录存在
    os.makedirs(os.path.join(sprites_dir, 'player'), exist_ok=True)
    os.makedirs(os.path.join(sprites_dir, 'enemies'), exist_ok=True)
    os.makedirs(os.path.join(sprites_dir, 'tiles'), exist_ok=True)
    os.makedirs(os.path.join(sprites_dir, 'items'), exist_ok=True)
    
    print(f"输出目录: {sprites_dir}")
    print()
    
    # 创建生成器并生成所有精灵
    try:
        generator = PixelSpriteGenerator(sprites_dir)
        files = generator.generate_all_sprites()
        
        print()
        print("=" * 50)
        print(f"成功生成 {len(files)} 个精灵文件!")
        print("=" * 50)
        
        # 按类别统计
        categories = {
            'player': 0,
            'enemies': 0,
            'tiles': 0,
            'items': 0
        }
        
        for path in files.values():
            for cat in categories:
                if cat in path:
                    categories[cat] += 1
                    break
        
        print("\n生成统计:")
        for cat, count in categories.items():
            print(f"  {cat}: {count} 个文件")
        
    except ImportError as e:
        print(f"错误: 缺少依赖库 - {e}")
        print("请运行: pip install Pillow")
        sys.exit(1)
    except Exception as e:
        print(f"生成过程中出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
