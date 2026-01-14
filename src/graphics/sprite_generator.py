"""
像素精灵生成器模块
AI辅助生成: 使用Pillow程序化生成像素风格精灵图（PNG透明背景）

此模块实现了PixelSpriteGenerator类，用于生成游戏中所有的像素艺术精灵。
所有精灵都以透明背景PNG格式保存，支持动画帧生成。

设计模式应用:
- 工厂模式: 通过统一接口创建不同类型的精灵
- 策略模式: 不同的绘制策略生成不同风格的精灵
"""

from PIL import Image, ImageDraw
import os
from typing import Dict, List, Tuple, Optional


class PixelSpriteGenerator:
    """
    像素精灵生成器类
    
    使用Pillow库程序化生成马里奥风格的像素艺术精灵。
    所有精灵使用透明背景，适合游戏中的精灵渲染。
    
    Attributes:
        output_dir: 精灵输出目录
        palette: 颜色调色板
    """
    
    # 颜色调色板 - 定义所有精灵使用的颜色
    # AI辅助生成: 参考经典马里奥配色，但使用原创设计
    PALETTE = {
        # 红帽跳跃者配色
        'red_jumper': {
            'hat': '#E52521',           # 经典红色帽子
            'hat_dark': '#B01E1A',       # 帽子阴影
            'skin': '#FFCC99',           # 肤色
            'skin_dark': '#E6B080',      # 肤色阴影
            'outfit': '#0039A6',         # 蓝色工装
            'outfit_dark': '#002970',    # 工装阴影
            'shoes': '#6B3E26',          # 棕色鞋
            'buttons': '#FFD700',        # 金色纽扣
            'eye': '#000000',            # 眼睛
            'eye_white': '#FFFFFF',      # 眼白
        },
        # 绿帽跳跃者配色
        'green_jumper': {
            'hat': '#3AA655',
            'hat_dark': '#2D8042',
            'skin': '#FFCC99',
            'skin_dark': '#E6B080',
            'outfit': '#0039A6',
            'outfit_dark': '#002970',
            'shoes': '#6B3E26',
            'buttons': '#FFD700',
            'eye': '#000000',
            'eye_white': '#FFFFFF',
        },
        # 蘑菇小怪配色
        'mushling': {
            'cap': '#A0522D',            # 蘑菇帽棕色
            'cap_dark': '#7A3E22',       # 蘑菇帽阴影
            'cap_spot': '#FFDEAD',       # 蘑菇斑点
            'body': '#FFDEAD',           # 米色身体
            'body_dark': '#DEB887',      # 身体阴影
            'feet': '#4A3728',           # 深棕脚
            'eye': '#000000',
            'eye_white': '#FFFFFF',
            'brow': '#5C4033',           # 眉毛
        },
        # 乌龟壳怪配色
        'shellback': {
            'shell': '#228B22',          # 绿色壳
            'shell_dark': '#1A6B1A',     # 壳阴影
            'shell_pattern': '#90EE90',  # 壳花纹
            'body': '#FFFF99',           # 黄色身体
            'body_dark': '#E6E680',      # 身体阴影
            'feet': '#8B4513',
            'eye': '#000000',
            'eye_white': '#FFFFFF',
        },
        # 飞行怪配色
        'flapper': {
            'body': '#4169E1',           # 蓝色身体
            'body_dark': '#2E4FA3',
            'wing': '#87CEEB',           # 天蓝翅膀
            'wing_dark': '#5BA3C9',
            'eye': '#FF4500',            # 橙红眼睛
            'beak': '#FFD700',
        },
        # 方块配色
        'tiles': {
            'ground': '#8B4513',         # 地面棕
            'ground_dark': '#6B3510',
            'ground_light': '#A0522D',
            'brick': '#CD853F',          # 砖色
            'brick_dark': '#A0682F',
            'brick_line': '#8B6914',     # 砖缝
            'question': '#FFD700',       # 问号块金色
            'question_dark': '#DAA520',
            'question_symbol': '#8B4513',
            'pipe': '#228B22',           # 管道绿
            'pipe_dark': '#1A6B1A',
            'pipe_light': '#32CD32',
            'spike': '#808080',          # 尖刺灰
            'spike_tip': '#C0C0C0',
        },
        # 道具配色
        'items': {
            'coin': '#FFD700',           # 金币
            'coin_dark': '#DAA520',
            'coin_shine': '#FFFFE0',
            'mushroom_cap': '#FF0000',   # 蘑菇道具
            'mushroom_cap_dark': '#CC0000',
            'mushroom_spot': '#FFFFFF',
            'mushroom_stem': '#FFDEAD',
            'star': '#FFD700',           # 星星
            'star_dark': '#FFA500',
            'star_eye': '#000000',
        },
    }
    
    def __init__(self, output_dir: str):
        """
        初始化精灵生成器
        
        Args:
            output_dir: 精灵输出的根目录
        """
        self.output_dir = output_dir
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """确保输出目录存在"""
        subdirs = ['player', 'enemies', 'tiles', 'items']
        for subdir in subdirs:
            path = os.path.join(self.output_dir, subdir)
            os.makedirs(path, exist_ok=True)
    
    def _hex_to_rgba(self, hex_color: str, alpha: int = 255) -> Tuple[int, int, int, int]:
        """
        将十六进制颜色转换为RGBA元组
        
        Args:
            hex_color: 十六进制颜色字符串（如 '#FF0000'）
            alpha: 透明度（0-255）
            
        Returns:
            RGBA颜色元组
        """
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b, alpha)
    
    def _create_canvas(self, width: int, height: int) -> Tuple[Image.Image, ImageDraw.ImageDraw]:
        """
        创建透明画布
        
        Args:
            width: 画布宽度
            height: 画布高度
            
        Returns:
            (Image对象, ImageDraw对象) 元组
        """
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        return image, draw
    
    def _draw_pixel(self, draw: ImageDraw.ImageDraw, x: int, y: int, 
                    color: str, scale: int = 1) -> None:
        """
        绘制一个像素（可缩放）
        
        Args:
            draw: ImageDraw对象
            x: X坐标
            y: Y坐标
            color: 颜色（十六进制）
            scale: 像素缩放比例
        """
        rgba = self._hex_to_rgba(color)
        draw.rectangle(
            [x * scale, y * scale, (x + 1) * scale - 1, (y + 1) * scale - 1],
            fill=rgba
        )
    
    def _draw_pixels(self, draw: ImageDraw.ImageDraw, pixels: List[Tuple[int, int, str]], 
                     scale: int = 1, offset_x: int = 0, offset_y: int = 0) -> None:
        """
        批量绘制像素
        
        Args:
            draw: ImageDraw对象
            pixels: 像素列表 [(x, y, color), ...]
            scale: 像素缩放比例
            offset_x: X偏移
            offset_y: Y偏移
        """
        for x, y, color in pixels:
            self._draw_pixel(draw, x + offset_x, y + offset_y, color, scale)
    
    # ==================== 玩家精灵生成 ====================
    
    def generate_player_idle(self, color_scheme: str = 'red_jumper') -> Image.Image:
        """
        生成玩家站立精灵
        
        AI辅助生成: 基于像素艺术设计原则，创建32x48的角色精灵
        我修改了原始设计以增加更多细节和阴影层次
        
        Args:
            color_scheme: 配色方案 ('red_jumper' 或 'green_jumper')
            
        Returns:
            PIL Image对象
        """
        width, height = 32, 48
        scale = 2  # 每个逻辑像素占2个实际像素
        image, draw = self._create_canvas(width, height)
        
        colors = self.PALETTE[color_scheme]
        
        # 定义像素图案 - 16x24逻辑像素，缩放2倍到32x48
        # 帽子（顶部）
        hat_pixels = [
            # 帽子主体
            (5, 0, colors['hat']), (6, 0, colors['hat']), (7, 0, colors['hat']),
            (8, 0, colors['hat']), (9, 0, colors['hat']), (10, 0, colors['hat']),
            (4, 1, colors['hat']), (5, 1, colors['hat']), (6, 1, colors['hat']),
            (7, 1, colors['hat']), (8, 1, colors['hat']), (9, 1, colors['hat']),
            (10, 1, colors['hat']), (11, 1, colors['hat']),
            (3, 2, colors['hat']), (4, 2, colors['hat']), (5, 2, colors['hat']),
            (6, 2, colors['hat']), (7, 2, colors['hat']), (8, 2, colors['hat']),
            (9, 2, colors['hat']), (10, 2, colors['hat']), (11, 2, colors['hat']),
            (12, 2, colors['hat']),
            # 帽子阴影
            (4, 2, colors['hat_dark']), (5, 2, colors['hat_dark']),
        ]
        
        # 脸部
        face_pixels = [
            # 肤色
            (5, 3, colors['skin']), (6, 3, colors['skin']), (7, 3, colors['skin']),
            (8, 3, colors['skin']), (9, 3, colors['skin']), (10, 3, colors['skin']),
            (4, 4, colors['skin']), (5, 4, colors['skin']), (6, 4, colors['skin']),
            (7, 4, colors['skin']), (8, 4, colors['skin']), (9, 4, colors['skin']),
            (10, 4, colors['skin']), (11, 4, colors['skin']),
            (4, 5, colors['skin']), (5, 5, colors['skin']), (6, 5, colors['skin']),
            (7, 5, colors['skin']), (8, 5, colors['skin']), (9, 5, colors['skin']),
            (10, 5, colors['skin']), (11, 5, colors['skin']),
            (5, 6, colors['skin']), (6, 6, colors['skin']), (7, 6, colors['skin']),
            (8, 6, colors['skin']), (9, 6, colors['skin']), (10, 6, colors['skin']),
            # 眼睛
            (5, 4, colors['eye_white']), (6, 4, colors['eye']),
            (9, 4, colors['eye_white']), (10, 4, colors['eye']),
            # 肤色阴影
            (4, 5, colors['skin_dark']), (11, 5, colors['skin_dark']),
        ]
        
        # 身体（工装）
        body_pixels = [
            # 工装主体
            (4, 7, colors['outfit']), (5, 7, colors['outfit']), (6, 7, colors['outfit']),
            (7, 7, colors['outfit']), (8, 7, colors['outfit']), (9, 7, colors['outfit']),
            (10, 7, colors['outfit']), (11, 7, colors['outfit']),
            (3, 8, colors['outfit']), (4, 8, colors['outfit']), (5, 8, colors['outfit']),
            (6, 8, colors['outfit']), (7, 8, colors['outfit']), (8, 8, colors['outfit']),
            (9, 8, colors['outfit']), (10, 8, colors['outfit']), (11, 8, colors['outfit']),
            (12, 8, colors['outfit']),
            (3, 9, colors['outfit']), (4, 9, colors['outfit']), (5, 9, colors['outfit']),
            (6, 9, colors['outfit']), (7, 9, colors['outfit']), (8, 9, colors['outfit']),
            (9, 9, colors['outfit']), (10, 9, colors['outfit']), (11, 9, colors['outfit']),
            (12, 9, colors['outfit']),
            (4, 10, colors['outfit']), (5, 10, colors['outfit']), (6, 10, colors['outfit']),
            (7, 10, colors['outfit']), (8, 10, colors['outfit']), (9, 10, colors['outfit']),
            (10, 10, colors['outfit']), (11, 10, colors['outfit']),
            # 纽扣
            (7, 8, colors['buttons']), (8, 8, colors['buttons']),
            # 阴影
            (3, 9, colors['outfit_dark']), (12, 9, colors['outfit_dark']),
        ]
        
        # 手臂（肤色）
        arm_pixels = [
            (2, 8, colors['skin']), (2, 9, colors['skin']), (2, 10, colors['skin']),
            (13, 8, colors['skin']), (13, 9, colors['skin']), (13, 10, colors['skin']),
        ]
        
        # 腿和鞋
        legs_pixels = [
            # 腿（工装）
            (5, 11, colors['outfit']), (6, 11, colors['outfit']),
            (9, 11, colors['outfit']), (10, 11, colors['outfit']),
            (5, 12, colors['outfit']), (6, 12, colors['outfit']),
            (9, 12, colors['outfit']), (10, 12, colors['outfit']),
            # 鞋子
            (4, 13, colors['shoes']), (5, 13, colors['shoes']), (6, 13, colors['shoes']),
            (7, 13, colors['shoes']),
            (8, 13, colors['shoes']), (9, 13, colors['shoes']), (10, 13, colors['shoes']),
            (11, 13, colors['shoes']),
        ]
        
        # 绘制所有像素 - 向下偏移10个逻辑像素，使脚底在图像底部
        # 角色脚底在y=13，图像高度24逻辑像素，需要移动到y=23，偏移=10
        all_pixels = hat_pixels + face_pixels + body_pixels + arm_pixels + legs_pixels
        self._draw_pixels(draw, all_pixels, scale, offset_y=10)
        
        return image
    
    def generate_player_run(self, color_scheme: str = 'red_jumper', frame: int = 1) -> Image.Image:
        """
        生成玩家跑步动画帧
        
        Args:
            color_scheme: 配色方案
            frame: 动画帧号 (1-4)
            
        Returns:
            PIL Image对象
        """
        width, height = 32, 48
        scale = 2
        image, draw = self._create_canvas(width, height)
        colors = self.PALETTE[color_scheme]
        
        # 基础帧 - 与站立类似但腿部不同
        # 帽子
        hat_pixels = [
            (5, 0, colors['hat']), (6, 0, colors['hat']), (7, 0, colors['hat']),
            (8, 0, colors['hat']), (9, 0, colors['hat']), (10, 0, colors['hat']),
            (4, 1, colors['hat']), (5, 1, colors['hat']), (6, 1, colors['hat']),
            (7, 1, colors['hat']), (8, 1, colors['hat']), (9, 1, colors['hat']),
            (10, 1, colors['hat']), (11, 1, colors['hat']),
            (3, 2, colors['hat']), (4, 2, colors['hat']), (5, 2, colors['hat']),
            (6, 2, colors['hat']), (7, 2, colors['hat']), (8, 2, colors['hat']),
            (9, 2, colors['hat']), (10, 2, colors['hat']), (11, 2, colors['hat']),
            (12, 2, colors['hat']),
        ]
        
        # 脸部
        face_pixels = [
            (5, 3, colors['skin']), (6, 3, colors['skin']), (7, 3, colors['skin']),
            (8, 3, colors['skin']), (9, 3, colors['skin']), (10, 3, colors['skin']),
            (4, 4, colors['skin']), (5, 4, colors['skin']), (6, 4, colors['skin']),
            (7, 4, colors['skin']), (8, 4, colors['skin']), (9, 4, colors['skin']),
            (10, 4, colors['skin']), (11, 4, colors['skin']),
            (4, 5, colors['skin']), (5, 5, colors['skin']), (6, 5, colors['skin']),
            (7, 5, colors['skin']), (8, 5, colors['skin']), (9, 5, colors['skin']),
            (10, 5, colors['skin']), (11, 5, colors['skin']),
            (5, 6, colors['skin']), (6, 6, colors['skin']), (7, 6, colors['skin']),
            (8, 6, colors['skin']), (9, 6, colors['skin']), (10, 6, colors['skin']),
            (5, 4, colors['eye_white']), (6, 4, colors['eye']),
            (9, 4, colors['eye_white']), (10, 4, colors['eye']),
        ]
        
        # 身体
        body_pixels = [
            (4, 7, colors['outfit']), (5, 7, colors['outfit']), (6, 7, colors['outfit']),
            (7, 7, colors['outfit']), (8, 7, colors['outfit']), (9, 7, colors['outfit']),
            (10, 7, colors['outfit']), (11, 7, colors['outfit']),
            (3, 8, colors['outfit']), (4, 8, colors['outfit']), (5, 8, colors['outfit']),
            (6, 8, colors['outfit']), (7, 8, colors['outfit']), (8, 8, colors['outfit']),
            (9, 8, colors['outfit']), (10, 8, colors['outfit']), (11, 8, colors['outfit']),
            (12, 8, colors['outfit']),
            (3, 9, colors['outfit']), (4, 9, colors['outfit']), (5, 9, colors['outfit']),
            (6, 9, colors['outfit']), (7, 9, colors['outfit']), (8, 9, colors['outfit']),
            (9, 9, colors['outfit']), (10, 9, colors['outfit']), (11, 9, colors['outfit']),
            (12, 9, colors['outfit']),
            (4, 10, colors['outfit']), (5, 10, colors['outfit']), (6, 10, colors['outfit']),
            (7, 10, colors['outfit']), (8, 10, colors['outfit']), (9, 10, colors['outfit']),
            (10, 10, colors['outfit']), (11, 10, colors['outfit']),
            (7, 8, colors['buttons']), (8, 8, colors['buttons']),
        ]
        
        # 根据帧号调整腿部位置
        if frame == 1:
            legs_pixels = [
                (5, 11, colors['outfit']), (6, 11, colors['outfit']),
                (9, 11, colors['outfit']), (10, 11, colors['outfit']),
                (4, 12, colors['outfit']), (5, 12, colors['outfit']),
                (10, 12, colors['outfit']), (11, 12, colors['outfit']),
                (3, 13, colors['shoes']), (4, 13, colors['shoes']), (5, 13, colors['shoes']),
                (10, 13, colors['shoes']), (11, 13, colors['shoes']), (12, 13, colors['shoes']),
            ]
        elif frame == 2:
            legs_pixels = [
                (6, 11, colors['outfit']), (7, 11, colors['outfit']),
                (8, 11, colors['outfit']), (9, 11, colors['outfit']),
                (6, 12, colors['outfit']), (7, 12, colors['outfit']),
                (8, 12, colors['outfit']), (9, 12, colors['outfit']),
                (5, 13, colors['shoes']), (6, 13, colors['shoes']), (7, 13, colors['shoes']),
                (8, 13, colors['shoes']), (9, 13, colors['shoes']), (10, 13, colors['shoes']),
            ]
        elif frame == 3:
            legs_pixels = [
                (5, 11, colors['outfit']), (6, 11, colors['outfit']),
                (9, 11, colors['outfit']), (10, 11, colors['outfit']),
                (6, 12, colors['outfit']), (7, 12, colors['outfit']),
                (8, 12, colors['outfit']), (9, 12, colors['outfit']),
                (5, 13, colors['shoes']), (6, 13, colors['shoes']), (7, 13, colors['shoes']),
                (8, 13, colors['shoes']), (9, 13, colors['shoes']), (10, 13, colors['shoes']),
            ]
        else:  # frame == 4
            legs_pixels = [
                (5, 11, colors['outfit']), (6, 11, colors['outfit']),
                (9, 11, colors['outfit']), (10, 11, colors['outfit']),
                (5, 12, colors['outfit']), (6, 12, colors['outfit']),
                (9, 12, colors['outfit']), (10, 12, colors['outfit']),
                (4, 13, colors['shoes']), (5, 13, colors['shoes']), (6, 13, colors['shoes']),
                (9, 13, colors['shoes']), (10, 13, colors['shoes']), (11, 13, colors['shoes']),
            ]
        
        # 手臂摆动
        if frame in [1, 3]:
            arm_pixels = [
                (1, 8, colors['skin']), (2, 9, colors['skin']), (2, 10, colors['skin']),
                (13, 8, colors['skin']), (14, 9, colors['skin']),
            ]
        else:
            arm_pixels = [
                (2, 8, colors['skin']), (1, 9, colors['skin']),
                (14, 8, colors['skin']), (13, 9, colors['skin']), (13, 10, colors['skin']),
            ]
        
        all_pixels = hat_pixels + face_pixels + body_pixels + arm_pixels + legs_pixels
        # 向下偏移10个逻辑像素，使脚底在图像底部
        self._draw_pixels(draw, all_pixels, scale, offset_y=10)
        
        return image
    
    def generate_player_jump(self, color_scheme: str = 'red_jumper') -> Image.Image:
        """
        生成玩家跳跃精灵
        
        Args:
            color_scheme: 配色方案
            
        Returns:
            PIL Image对象
        """
        width, height = 32, 48
        scale = 2
        image, draw = self._create_canvas(width, height)
        colors = self.PALETTE[color_scheme]
        
        # 帽子
        hat_pixels = [
            (5, 0, colors['hat']), (6, 0, colors['hat']), (7, 0, colors['hat']),
            (8, 0, colors['hat']), (9, 0, colors['hat']), (10, 0, colors['hat']),
            (4, 1, colors['hat']), (5, 1, colors['hat']), (6, 1, colors['hat']),
            (7, 1, colors['hat']), (8, 1, colors['hat']), (9, 1, colors['hat']),
            (10, 1, colors['hat']), (11, 1, colors['hat']),
            (3, 2, colors['hat']), (4, 2, colors['hat']), (5, 2, colors['hat']),
            (6, 2, colors['hat']), (7, 2, colors['hat']), (8, 2, colors['hat']),
            (9, 2, colors['hat']), (10, 2, colors['hat']), (11, 2, colors['hat']),
            (12, 2, colors['hat']),
        ]
        
        # 脸部
        face_pixels = [
            (5, 3, colors['skin']), (6, 3, colors['skin']), (7, 3, colors['skin']),
            (8, 3, colors['skin']), (9, 3, colors['skin']), (10, 3, colors['skin']),
            (4, 4, colors['skin']), (5, 4, colors['skin']), (6, 4, colors['skin']),
            (7, 4, colors['skin']), (8, 4, colors['skin']), (9, 4, colors['skin']),
            (10, 4, colors['skin']), (11, 4, colors['skin']),
            (4, 5, colors['skin']), (5, 5, colors['skin']), (6, 5, colors['skin']),
            (7, 5, colors['skin']), (8, 5, colors['skin']), (9, 5, colors['skin']),
            (10, 5, colors['skin']), (11, 5, colors['skin']),
            (5, 6, colors['skin']), (6, 6, colors['skin']), (7, 6, colors['skin']),
            (8, 6, colors['skin']), (9, 6, colors['skin']), (10, 6, colors['skin']),
            (5, 4, colors['eye_white']), (6, 4, colors['eye']),
            (9, 4, colors['eye_white']), (10, 4, colors['eye']),
        ]
        
        # 身体
        body_pixels = [
            (4, 7, colors['outfit']), (5, 7, colors['outfit']), (6, 7, colors['outfit']),
            (7, 7, colors['outfit']), (8, 7, colors['outfit']), (9, 7, colors['outfit']),
            (10, 7, colors['outfit']), (11, 7, colors['outfit']),
            (3, 8, colors['outfit']), (4, 8, colors['outfit']), (5, 8, colors['outfit']),
            (6, 8, colors['outfit']), (7, 8, colors['outfit']), (8, 8, colors['outfit']),
            (9, 8, colors['outfit']), (10, 8, colors['outfit']), (11, 8, colors['outfit']),
            (12, 8, colors['outfit']),
            (4, 9, colors['outfit']), (5, 9, colors['outfit']), (6, 9, colors['outfit']),
            (7, 9, colors['outfit']), (8, 9, colors['outfit']), (9, 9, colors['outfit']),
            (10, 9, colors['outfit']), (11, 9, colors['outfit']),
            (7, 8, colors['buttons']), (8, 8, colors['buttons']),
        ]
        
        # 跳跃姿势 - 手臂向上，腿弯曲
        arm_pixels = [
            (1, 6, colors['skin']), (2, 7, colors['skin']),
            (13, 6, colors['skin']), (14, 7, colors['skin']),
        ]
        
        legs_pixels = [
            (4, 10, colors['outfit']), (5, 10, colors['outfit']), (6, 10, colors['outfit']),
            (9, 10, colors['outfit']), (10, 10, colors['outfit']), (11, 10, colors['outfit']),
            (3, 11, colors['outfit']), (4, 11, colors['outfit']),
            (11, 11, colors['outfit']), (12, 11, colors['outfit']),
            (2, 12, colors['shoes']), (3, 12, colors['shoes']), (4, 12, colors['shoes']),
            (11, 12, colors['shoes']), (12, 12, colors['shoes']), (13, 12, colors['shoes']),
        ]
        
        all_pixels = hat_pixels + face_pixels + body_pixels + arm_pixels + legs_pixels
        # 向下偏移11个逻辑像素，使脚底在图像底部（跳跃精灵脚在y=12）
        self._draw_pixels(draw, all_pixels, scale, offset_y=11)
        
        return image
    
    # ==================== 敌人精灵生成 ====================
    
    def generate_mushling(self, frame: int = 1, squashed: bool = False) -> Image.Image:
        """
        生成蘑菇小怪精灵
        
        AI辅助生成: 设计了一个可爱但有威胁感的蘑菇敌人
        
        Args:
            frame: 动画帧号 (1-2)
            squashed: 是否被踩扁状态
            
        Returns:
            PIL Image对象
        """
        width, height = 32, 32
        scale = 2
        image, draw = self._create_canvas(width, height)
        colors = self.PALETTE['mushling']
        
        if squashed:
            # 被踩扁状态 - 扁平
            pixels = [
                # 扁平的蘑菇帽
                (3, 10, colors['cap']), (4, 10, colors['cap']), (5, 10, colors['cap']),
                (6, 10, colors['cap']), (7, 10, colors['cap']), (8, 10, colors['cap']),
                (9, 10, colors['cap']), (10, 10, colors['cap']), (11, 10, colors['cap']),
                (12, 10, colors['cap']),
                (2, 11, colors['cap']), (3, 11, colors['cap']), (4, 11, colors['cap']),
                (5, 11, colors['cap']), (6, 11, colors['cap']), (7, 11, colors['cap']),
                (8, 11, colors['cap']), (9, 11, colors['cap']), (10, 11, colors['cap']),
                (11, 11, colors['cap']), (12, 11, colors['cap']), (13, 11, colors['cap']),
                # 斑点
                (5, 10, colors['cap_spot']), (10, 10, colors['cap_spot']),
                # X眼睛
                (5, 12, colors['eye']), (7, 12, colors['eye']),
                (9, 12, colors['eye']), (11, 12, colors['eye']),
            ]
        else:
            # 正常状态
            # 蘑菇帽
            cap_pixels = [
                (4, 0, colors['cap']), (5, 0, colors['cap']), (6, 0, colors['cap']),
                (7, 0, colors['cap']), (8, 0, colors['cap']), (9, 0, colors['cap']),
                (10, 0, colors['cap']), (11, 0, colors['cap']),
                (3, 1, colors['cap']), (4, 1, colors['cap']), (5, 1, colors['cap']),
                (6, 1, colors['cap']), (7, 1, colors['cap']), (8, 1, colors['cap']),
                (9, 1, colors['cap']), (10, 1, colors['cap']), (11, 1, colors['cap']),
                (12, 1, colors['cap']),
                (2, 2, colors['cap']), (3, 2, colors['cap']), (4, 2, colors['cap']),
                (5, 2, colors['cap']), (6, 2, colors['cap']), (7, 2, colors['cap']),
                (8, 2, colors['cap']), (9, 2, colors['cap']), (10, 2, colors['cap']),
                (11, 2, colors['cap']), (12, 2, colors['cap']), (13, 2, colors['cap']),
                (2, 3, colors['cap']), (3, 3, colors['cap']), (4, 3, colors['cap']),
                (5, 3, colors['cap']), (6, 3, colors['cap']), (7, 3, colors['cap']),
                (8, 3, colors['cap']), (9, 3, colors['cap']), (10, 3, colors['cap']),
                (11, 3, colors['cap']), (12, 3, colors['cap']), (13, 3, colors['cap']),
                (3, 4, colors['cap']), (4, 4, colors['cap']), (5, 4, colors['cap']),
                (6, 4, colors['cap']), (7, 4, colors['cap']), (8, 4, colors['cap']),
                (9, 4, colors['cap']), (10, 4, colors['cap']), (11, 4, colors['cap']),
                (12, 4, colors['cap']),
                # 斑点
                (5, 2, colors['cap_spot']), (6, 2, colors['cap_spot']),
                (9, 2, colors['cap_spot']), (10, 2, colors['cap_spot']),
                (4, 3, colors['cap_spot']), (11, 3, colors['cap_spot']),
            ]
            
            # 脸部
            face_pixels = [
                (4, 5, colors['body']), (5, 5, colors['body']), (6, 5, colors['body']),
                (7, 5, colors['body']), (8, 5, colors['body']), (9, 5, colors['body']),
                (10, 5, colors['body']), (11, 5, colors['body']),
                (3, 6, colors['body']), (4, 6, colors['body']), (5, 6, colors['body']),
                (6, 6, colors['body']), (7, 6, colors['body']), (8, 6, colors['body']),
                (9, 6, colors['body']), (10, 6, colors['body']), (11, 6, colors['body']),
                (12, 6, colors['body']),
                (3, 7, colors['body']), (4, 7, colors['body']), (5, 7, colors['body']),
                (6, 7, colors['body']), (7, 7, colors['body']), (8, 7, colors['body']),
                (9, 7, colors['body']), (10, 7, colors['body']), (11, 7, colors['body']),
                (12, 7, colors['body']),
                (4, 8, colors['body']), (5, 8, colors['body']), (6, 8, colors['body']),
                (7, 8, colors['body']), (8, 8, colors['body']), (9, 8, colors['body']),
                (10, 8, colors['body']), (11, 8, colors['body']),
                # 眉毛
                (4, 5, colors['brow']), (5, 5, colors['brow']),
                (10, 5, colors['brow']), (11, 5, colors['brow']),
                # 眼睛
                (5, 6, colors['eye_white']), (6, 6, colors['eye']),
                (9, 6, colors['eye_white']), (10, 6, colors['eye']),
            ]
            
            # 脚 - 根据帧号调整位置
            if frame == 1:
                feet_pixels = [
                    (3, 9, colors['feet']), (4, 9, colors['feet']), (5, 9, colors['feet']),
                    (10, 9, colors['feet']), (11, 9, colors['feet']), (12, 9, colors['feet']),
                    (2, 10, colors['feet']), (3, 10, colors['feet']), (4, 10, colors['feet']),
                    (11, 10, colors['feet']), (12, 10, colors['feet']), (13, 10, colors['feet']),
                ]
            else:
                feet_pixels = [
                    (4, 9, colors['feet']), (5, 9, colors['feet']), (6, 9, colors['feet']),
                    (9, 9, colors['feet']), (10, 9, colors['feet']), (11, 9, colors['feet']),
                    (3, 10, colors['feet']), (4, 10, colors['feet']), (5, 10, colors['feet']),
                    (10, 10, colors['feet']), (11, 10, colors['feet']), (12, 10, colors['feet']),
                ]
            
            pixels = cap_pixels + face_pixels + feet_pixels
        
        # 向下偏移5个逻辑像素，使脚底在图像底部（脚在y=10，图像高16逻辑像素）
        self._draw_pixels(draw, pixels, scale, offset_y=5)
        return image
    
    def generate_shellback(self, frame: int = 1, shell_mode: bool = False) -> Image.Image:
        """
        生成乌龟壳怪精灵
        
        Args:
            frame: 动画帧号 (1-2)
            shell_mode: 是否为壳模式（被踩后）
            
        Returns:
            PIL Image对象
        """
        width, height = 32, 40
        scale = 2
        image, draw = self._create_canvas(width, height)
        colors = self.PALETTE['shellback']
        
        if shell_mode:
            # 壳模式 - 只有壳
            shell_pixels = [
                (4, 6, colors['shell']), (5, 6, colors['shell']), (6, 6, colors['shell']),
                (7, 6, colors['shell']), (8, 6, colors['shell']), (9, 6, colors['shell']),
                (10, 6, colors['shell']), (11, 6, colors['shell']),
                (3, 7, colors['shell']), (4, 7, colors['shell']), (5, 7, colors['shell']),
                (6, 7, colors['shell']), (7, 7, colors['shell']), (8, 7, colors['shell']),
                (9, 7, colors['shell']), (10, 7, colors['shell']), (11, 7, colors['shell']),
                (12, 7, colors['shell']),
                (2, 8, colors['shell']), (3, 8, colors['shell']), (4, 8, colors['shell']),
                (5, 8, colors['shell']), (6, 8, colors['shell']), (7, 8, colors['shell']),
                (8, 8, colors['shell']), (9, 8, colors['shell']), (10, 8, colors['shell']),
                (11, 8, colors['shell']), (12, 8, colors['shell']), (13, 8, colors['shell']),
                (2, 9, colors['shell']), (3, 9, colors['shell']), (4, 9, colors['shell']),
                (5, 9, colors['shell']), (6, 9, colors['shell']), (7, 9, colors['shell']),
                (8, 9, colors['shell']), (9, 9, colors['shell']), (10, 9, colors['shell']),
                (11, 9, colors['shell']), (12, 9, colors['shell']), (13, 9, colors['shell']),
                (3, 10, colors['shell']), (4, 10, colors['shell']), (5, 10, colors['shell']),
                (6, 10, colors['shell']), (7, 10, colors['shell']), (8, 10, colors['shell']),
                (9, 10, colors['shell']), (10, 10, colors['shell']), (11, 10, colors['shell']),
                (12, 10, colors['shell']),
                # 花纹
                (6, 8, colors['shell_pattern']), (7, 8, colors['shell_pattern']),
                (8, 8, colors['shell_pattern']), (9, 8, colors['shell_pattern']),
                (5, 9, colors['shell_pattern']), (10, 9, colors['shell_pattern']),
            ]
            self._draw_pixels(draw, shell_pixels, scale)
        else:
            # 正常行走状态
            # 头部
            head_pixels = [
                (3, 0, colors['body']), (4, 0, colors['body']), (5, 0, colors['body']),
                (2, 1, colors['body']), (3, 1, colors['body']), (4, 1, colors['body']),
                (5, 1, colors['body']), (6, 1, colors['body']),
                (2, 2, colors['body']), (3, 2, colors['body']), (4, 2, colors['body']),
                (5, 2, colors['body']), (6, 2, colors['body']),
                (3, 3, colors['body']), (4, 3, colors['body']), (5, 3, colors['body']),
                # 眼睛
                (3, 1, colors['eye_white']), (4, 1, colors['eye']),
            ]
            
            # 壳
            shell_pixels = [
                (5, 2, colors['shell']), (6, 2, colors['shell']), (7, 2, colors['shell']),
                (8, 2, colors['shell']), (9, 2, colors['shell']), (10, 2, colors['shell']),
                (11, 2, colors['shell']),
                (4, 3, colors['shell']), (5, 3, colors['shell']), (6, 3, colors['shell']),
                (7, 3, colors['shell']), (8, 3, colors['shell']), (9, 3, colors['shell']),
                (10, 3, colors['shell']), (11, 3, colors['shell']), (12, 3, colors['shell']),
                (4, 4, colors['shell']), (5, 4, colors['shell']), (6, 4, colors['shell']),
                (7, 4, colors['shell']), (8, 4, colors['shell']), (9, 4, colors['shell']),
                (10, 4, colors['shell']), (11, 4, colors['shell']), (12, 4, colors['shell']),
                (4, 5, colors['shell']), (5, 5, colors['shell']), (6, 5, colors['shell']),
                (7, 5, colors['shell']), (8, 5, colors['shell']), (9, 5, colors['shell']),
                (10, 5, colors['shell']), (11, 5, colors['shell']), (12, 5, colors['shell']),
                (5, 6, colors['shell']), (6, 6, colors['shell']), (7, 6, colors['shell']),
                (8, 6, colors['shell']), (9, 6, colors['shell']), (10, 6, colors['shell']),
                (11, 6, colors['shell']),
                # 花纹
                (7, 4, colors['shell_pattern']), (8, 4, colors['shell_pattern']),
                (9, 4, colors['shell_pattern']),
                (6, 5, colors['shell_pattern']), (10, 5, colors['shell_pattern']),
            ]
            
            # 脚
            if frame == 1:
                feet_pixels = [
                    (3, 7, colors['feet']), (4, 7, colors['feet']), (5, 7, colors['feet']),
                    (10, 7, colors['feet']), (11, 7, colors['feet']), (12, 7, colors['feet']),
                    (2, 8, colors['feet']), (3, 8, colors['feet']),
                    (12, 8, colors['feet']), (13, 8, colors['feet']),
                ]
            else:
                feet_pixels = [
                    (4, 7, colors['feet']), (5, 7, colors['feet']), (6, 7, colors['feet']),
                    (9, 7, colors['feet']), (10, 7, colors['feet']), (11, 7, colors['feet']),
                    (3, 8, colors['feet']), (4, 8, colors['feet']),
                    (11, 8, colors['feet']), (12, 8, colors['feet']),
                ]
            
            pixels = head_pixels + shell_pixels + feet_pixels
            # 向下偏移11个逻辑像素，使脚底在图像底部（脚在y=8，图像高20逻辑像素）
            self._draw_pixels(draw, pixels, scale, offset_y=11)
        
        return image
    
    def generate_flapper(self, frame: int = 1) -> Image.Image:
        """
        生成飞行怪精灵（困难模式）
        
        Args:
            frame: 动画帧号 (1-4)
            
        Returns:
            PIL Image对象
        """
        width, height = 32, 32
        scale = 2
        image, draw = self._create_canvas(width, height)
        colors = self.PALETTE['flapper']
        
        # 身体
        body_pixels = [
            (6, 4, colors['body']), (7, 4, colors['body']), (8, 4, colors['body']),
            (9, 4, colors['body']),
            (5, 5, colors['body']), (6, 5, colors['body']), (7, 5, colors['body']),
            (8, 5, colors['body']), (9, 5, colors['body']), (10, 5, colors['body']),
            (5, 6, colors['body']), (6, 6, colors['body']), (7, 6, colors['body']),
            (8, 6, colors['body']), (9, 6, colors['body']), (10, 6, colors['body']),
            (5, 7, colors['body']), (6, 7, colors['body']), (7, 7, colors['body']),
            (8, 7, colors['body']), (9, 7, colors['body']), (10, 7, colors['body']),
            (6, 8, colors['body']), (7, 8, colors['body']), (8, 8, colors['body']),
            (9, 8, colors['body']),
            # 眼睛
            (6, 5, colors['eye']), (9, 5, colors['eye']),
            # 嘴/喙
            (7, 7, colors['beak']), (8, 7, colors['beak']),
        ]
        
        # 翅膀 - 根据帧号调整位置
        if frame == 1:
            wing_pixels = [
                (2, 3, colors['wing']), (3, 3, colors['wing']),
                (1, 4, colors['wing']), (2, 4, colors['wing']), (3, 4, colors['wing']),
                (4, 4, colors['wing']),
                (12, 3, colors['wing']), (13, 3, colors['wing']),
                (11, 4, colors['wing']), (12, 4, colors['wing']), (13, 4, colors['wing']),
                (14, 4, colors['wing']),
            ]
        elif frame == 2:
            wing_pixels = [
                (2, 4, colors['wing']), (3, 4, colors['wing']),
                (1, 5, colors['wing']), (2, 5, colors['wing']), (3, 5, colors['wing']),
                (4, 5, colors['wing']),
                (12, 4, colors['wing']), (13, 4, colors['wing']),
                (11, 5, colors['wing']), (12, 5, colors['wing']), (13, 5, colors['wing']),
                (14, 5, colors['wing']),
            ]
        elif frame == 3:
            wing_pixels = [
                (2, 5, colors['wing']), (3, 5, colors['wing']),
                (1, 6, colors['wing']), (2, 6, colors['wing']), (3, 6, colors['wing']),
                (4, 6, colors['wing']),
                (12, 5, colors['wing']), (13, 5, colors['wing']),
                (11, 6, colors['wing']), (12, 6, colors['wing']), (13, 6, colors['wing']),
                (14, 6, colors['wing']),
            ]
        else:
            wing_pixels = [
                (2, 4, colors['wing']), (3, 4, colors['wing']),
                (1, 5, colors['wing']), (2, 5, colors['wing']), (3, 5, colors['wing']),
                (4, 5, colors['wing']),
                (12, 4, colors['wing']), (13, 4, colors['wing']),
                (11, 5, colors['wing']), (12, 5, colors['wing']), (13, 5, colors['wing']),
                (14, 5, colors['wing']),
            ]
        
        pixels = body_pixels + wing_pixels
        self._draw_pixels(draw, pixels, scale)
        
        return image
    
    # ==================== 方块精灵生成 ====================
    
    def generate_ground_tile(self) -> Image.Image:
        """生成地面方块精灵"""
        width, height = 32, 32
        scale = 2
        image, draw = self._create_canvas(width, height)
        colors = self.PALETTE['tiles']
        
        # 填充整个方块
        for y in range(16):
            for x in range(16):
                # 创建砖块纹理
                if y < 2:
                    color = colors['ground_light']
                elif (x + y) % 4 == 0:
                    color = colors['ground_dark']
                else:
                    color = colors['ground']
                self._draw_pixel(draw, x, y, color, scale)
        
        # 添加边缘高光和阴影
        for x in range(16):
            self._draw_pixel(draw, x, 0, colors['ground_light'], scale)
            self._draw_pixel(draw, x, 15, colors['ground_dark'], scale)
        
        return image
    
    def generate_brick(self) -> Image.Image:
        """生成砖块精灵"""
        width, height = 32, 32
        scale = 2
        image, draw = self._create_canvas(width, height)
        colors = self.PALETTE['tiles']
        
        # 砖块图案 - 4x2砖块布局
        for y in range(16):
            for x in range(16):
                # 确定是否在砖缝位置
                brick_row = y // 4
                is_line_y = y % 4 == 0
                
                # 交错砖缝
                offset = 4 if brick_row % 2 == 1 else 0
                is_line_x = (x + offset) % 8 == 0
                
                if is_line_y or is_line_x:
                    color = colors['brick_line']
                elif y % 4 == 1:
                    color = colors['brick']  # 高光
                else:
                    color = colors['brick_dark'] if (x + y) % 3 == 0 else colors['brick']
                
                self._draw_pixel(draw, x, y, color, scale)
        
        return image
    
    def generate_question_block(self, frame: int = 1) -> Image.Image:
        """
        生成问号方块精灵
        
        Args:
            frame: 动画帧号 (1-4)
            
        Returns:
            PIL Image对象
        """
        width, height = 32, 32
        scale = 2
        image, draw = self._create_canvas(width, height)
        colors = self.PALETTE['tiles']
        
        # 背景色 - 根据帧号变化亮度
        brightness_map = {1: colors['question'], 2: colors['question_dark'], 
                         3: colors['question'], 4: '#FFEC8B'}
        bg_color = brightness_map.get(frame, colors['question'])
        
        # 填充背景
        for y in range(16):
            for x in range(16):
                if x == 0 or y == 0:
                    color = '#FFFACD'  # 高光边缘
                elif x == 15 or y == 15:
                    color = colors['question_dark']  # 阴影边缘
                else:
                    color = bg_color
                self._draw_pixel(draw, x, y, color, scale)
        
        # 绘制问号
        question_mark = [
            (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3),
            (4, 4), (5, 4), (10, 4), (11, 4),
            (10, 5), (11, 5),
            (9, 6), (10, 6),
            (8, 7), (9, 7),
            (7, 8), (8, 8),
            (7, 9), (8, 9),
            (7, 11), (8, 11),
            (7, 12), (8, 12),
        ]
        
        for x, y in question_mark:
            self._draw_pixel(draw, x, y, colors['question_symbol'], scale)
        
        return image
    
    def generate_empty_block(self) -> Image.Image:
        """生成空方块（问号块被顶后）"""
        width, height = 32, 32
        scale = 2
        image, draw = self._create_canvas(width, height)
        
        # 深色方块
        for y in range(16):
            for x in range(16):
                if x == 0 or y == 0:
                    color = '#5A5A5A'
                elif x == 15 or y == 15:
                    color = '#2A2A2A'
                else:
                    color = '#404040'
                self._draw_pixel(draw, x, y, color, scale)
        
        return image
    
    def generate_pipe(self) -> Image.Image:
        """生成管道精灵（64x64）"""
        width, height = 64, 64
        scale = 2
        image, draw = self._create_canvas(width, height)
        colors = self.PALETTE['tiles']
        
        # 管道顶部（较宽）
        for y in range(8):
            for x in range(32):
                if x < 2 or x >= 30:
                    color = colors['pipe_dark']
                elif x < 4:
                    color = colors['pipe_light']
                elif x >= 28:
                    color = colors['pipe_dark']
                else:
                    color = colors['pipe']
                self._draw_pixel(draw, x, y, color, scale)
        
        # 管道主体（较窄）
        for y in range(8, 32):
            for x in range(4, 28):
                if x < 6:
                    color = colors['pipe_light']
                elif x >= 26:
                    color = colors['pipe_dark']
                else:
                    color = colors['pipe']
                self._draw_pixel(draw, x, y, color, scale)
        
        return image
    
    def generate_spike(self, blink: bool = False) -> Image.Image:
        """
        生成尖刺精灵（困难模式陷阱）
        
        Args:
            blink: 是否为闪烁状态（困难模式）
        """
        width, height = 32, 32
        scale = 2
        image, draw = self._create_canvas(width, height)
        colors = self.PALETTE['tiles']
        
        if blink:
            # 闪烁状态 - 半透明效果（使用不同颜色模拟）
            spike_color = '#A0A0A0'
            tip_color = '#D0D0D0'
        else:
            spike_color = colors['spike']
            tip_color = colors['spike_tip']
        
        # 绘制三个尖刺
        for spike_x in [2, 7, 12]:
            # 尖刺形状（三角形）
            for row in range(8):
                width_at_row = row + 1
                start_x = spike_x + (4 - width_at_row // 2)
                for i in range(width_at_row):
                    y = 8 + row
                    x = start_x + i
                    if row < 2:
                        color = tip_color
                    else:
                        color = spike_color
                    self._draw_pixel(draw, x, y, color, scale)
        
        return image
    
    def generate_platform(self) -> Image.Image:
        """生成移动平台精灵（96x16）"""
        width, height = 96, 16
        scale = 2
        image, draw = self._create_canvas(width, height)
        
        # 平台颜色
        platform_color = '#8B7355'
        platform_light = '#A08060'
        platform_dark = '#6B5344'
        
        for y in range(8):
            for x in range(48):
                if y == 0:
                    color = platform_light
                elif y == 7:
                    color = platform_dark
                elif x < 2 or x >= 46:
                    color = platform_dark
                else:
                    color = platform_color
                self._draw_pixel(draw, x, y, color, scale)
        
        return image
    
    # ==================== 道具精灵生成 ====================
    
    def generate_coin(self, frame: int = 1) -> Image.Image:
        """
        生成金币精灵
        
        Args:
            frame: 动画帧号 (1-4) 表示旋转
        """
        width, height = 24, 24
        scale = 2
        image, draw = self._create_canvas(width, height)
        colors = self.PALETTE['items']
        
        # 根据帧号调整金币宽度（模拟旋转）
        widths = {1: 6, 2: 4, 3: 2, 4: 4}
        coin_width = widths.get(frame, 6)
        offset_x = (6 - coin_width) // 2
        
        # 绘制椭圆形金币
        for y in range(12):
            for x in range(coin_width):
                # 计算是否在椭圆内
                cx = coin_width / 2
                cy = 6
                rx = coin_width / 2
                ry = 5
                
                dx = (x + 0.5 - cx) / rx
                dy = (y + 0.5 - cy) / ry
                
                if dx * dx + dy * dy <= 1:
                    # 根据位置决定颜色
                    if y < 2 or x < 1:
                        color = colors['coin_shine']
                    elif y > 9 or x >= coin_width - 1:
                        color = colors['coin_dark']
                    else:
                        color = colors['coin']
                    self._draw_pixel(draw, x + offset_x, y, color, scale)
        
        return image
    
    def generate_mushroom_item(self) -> Image.Image:
        """生成蘑菇道具精灵（变大效果）"""
        width, height = 32, 32
        scale = 2
        image, draw = self._create_canvas(width, height)
        colors = self.PALETTE['items']
        
        # 蘑菇帽
        cap_pixels = [
            (4, 0, colors['mushroom_cap']), (5, 0, colors['mushroom_cap']),
            (6, 0, colors['mushroom_cap']), (7, 0, colors['mushroom_cap']),
            (8, 0, colors['mushroom_cap']), (9, 0, colors['mushroom_cap']),
            (10, 0, colors['mushroom_cap']), (11, 0, colors['mushroom_cap']),
            (3, 1, colors['mushroom_cap']), (4, 1, colors['mushroom_cap']),
            (5, 1, colors['mushroom_cap']), (6, 1, colors['mushroom_cap']),
            (7, 1, colors['mushroom_cap']), (8, 1, colors['mushroom_cap']),
            (9, 1, colors['mushroom_cap']), (10, 1, colors['mushroom_cap']),
            (11, 1, colors['mushroom_cap']), (12, 1, colors['mushroom_cap']),
            (2, 2, colors['mushroom_cap']), (3, 2, colors['mushroom_cap']),
            (4, 2, colors['mushroom_cap']), (5, 2, colors['mushroom_cap']),
            (6, 2, colors['mushroom_cap']), (7, 2, colors['mushroom_cap']),
            (8, 2, colors['mushroom_cap']), (9, 2, colors['mushroom_cap']),
            (10, 2, colors['mushroom_cap']), (11, 2, colors['mushroom_cap']),
            (12, 2, colors['mushroom_cap']), (13, 2, colors['mushroom_cap']),
            (2, 3, colors['mushroom_cap']), (3, 3, colors['mushroom_cap']),
            (4, 3, colors['mushroom_cap']), (5, 3, colors['mushroom_cap']),
            (6, 3, colors['mushroom_cap']), (7, 3, colors['mushroom_cap']),
            (8, 3, colors['mushroom_cap']), (9, 3, colors['mushroom_cap']),
            (10, 3, colors['mushroom_cap']), (11, 3, colors['mushroom_cap']),
            (12, 3, colors['mushroom_cap']), (13, 3, colors['mushroom_cap']),
            (3, 4, colors['mushroom_cap']), (4, 4, colors['mushroom_cap']),
            (5, 4, colors['mushroom_cap']), (6, 4, colors['mushroom_cap']),
            (7, 4, colors['mushroom_cap']), (8, 4, colors['mushroom_cap']),
            (9, 4, colors['mushroom_cap']), (10, 4, colors['mushroom_cap']),
            (11, 4, colors['mushroom_cap']), (12, 4, colors['mushroom_cap']),
            # 白色斑点
            (5, 1, colors['mushroom_spot']), (6, 1, colors['mushroom_spot']),
            (9, 1, colors['mushroom_spot']), (10, 1, colors['mushroom_spot']),
            (4, 2, colors['mushroom_spot']), (5, 2, colors['mushroom_spot']),
            (10, 2, colors['mushroom_spot']), (11, 2, colors['mushroom_spot']),
            (7, 3, colors['mushroom_spot']), (8, 3, colors['mushroom_spot']),
        ]
        
        # 蘑菇茎
        stem_pixels = [
            (5, 5, colors['mushroom_stem']), (6, 5, colors['mushroom_stem']),
            (7, 5, colors['mushroom_stem']), (8, 5, colors['mushroom_stem']),
            (9, 5, colors['mushroom_stem']), (10, 5, colors['mushroom_stem']),
            (5, 6, colors['mushroom_stem']), (6, 6, colors['mushroom_stem']),
            (7, 6, colors['mushroom_stem']), (8, 6, colors['mushroom_stem']),
            (9, 6, colors['mushroom_stem']), (10, 6, colors['mushroom_stem']),
            (6, 7, colors['mushroom_stem']), (7, 7, colors['mushroom_stem']),
            (8, 7, colors['mushroom_stem']), (9, 7, colors['mushroom_stem']),
        ]
        
        pixels = cap_pixels + stem_pixels
        self._draw_pixels(draw, pixels, scale)
        
        return image
    
    def generate_star(self, frame: int = 1) -> Image.Image:
        """
        生成星星道具精灵（无敌效果）
        
        Args:
            frame: 动画帧号 (1-4) 表示闪烁
        """
        width, height = 28, 28
        scale = 2
        image, draw = self._create_canvas(width, height)
        colors = self.PALETTE['items']
        
        # 根据帧号调整颜色
        if frame in [1, 3]:
            star_color = colors['star']
        else:
            star_color = colors['star_dark']
        
        # 星星形状（5角星）
        star_pixels = [
            # 顶部尖角
            (6, 0, star_color), (7, 0, star_color),
            (5, 1, star_color), (6, 1, star_color), (7, 1, star_color), (8, 1, star_color),
            (5, 2, star_color), (6, 2, star_color), (7, 2, star_color), (8, 2, star_color),
            # 中间宽部分
            (0, 3, star_color), (1, 3, star_color), (2, 3, star_color), (3, 3, star_color),
            (4, 3, star_color), (5, 3, star_color), (6, 3, star_color), (7, 3, star_color),
            (8, 3, star_color), (9, 3, star_color), (10, 3, star_color), (11, 3, star_color),
            (12, 3, star_color), (13, 3, star_color),
            (1, 4, star_color), (2, 4, star_color), (3, 4, star_color), (4, 4, star_color),
            (5, 4, star_color), (6, 4, star_color), (7, 4, star_color), (8, 4, star_color),
            (9, 4, star_color), (10, 4, star_color), (11, 4, star_color), (12, 4, star_color),
            (2, 5, star_color), (3, 5, star_color), (4, 5, star_color), (5, 5, star_color),
            (6, 5, star_color), (7, 5, star_color), (8, 5, star_color), (9, 5, star_color),
            (10, 5, star_color), (11, 5, star_color),
            (3, 6, star_color), (4, 6, star_color), (5, 6, star_color), (6, 6, star_color),
            (7, 6, star_color), (8, 6, star_color), (9, 6, star_color), (10, 6, star_color),
            # 底部两个尖角
            (2, 7, star_color), (3, 7, star_color), (4, 7, star_color),
            (9, 7, star_color), (10, 7, star_color), (11, 7, star_color),
            (1, 8, star_color), (2, 8, star_color), (3, 8, star_color),
            (10, 8, star_color), (11, 8, star_color), (12, 8, star_color),
            (0, 9, star_color), (1, 9, star_color), (2, 9, star_color),
            (11, 9, star_color), (12, 9, star_color), (13, 9, star_color),
            # 眼睛
            (5, 4, colors['star_eye']), (8, 4, colors['star_eye']),
        ]
        
        self._draw_pixels(draw, star_pixels, scale)
        
        return image
    
    def generate_flag(self) -> Image.Image:
        """生成终点旗帜精灵"""
        width, height = 32, 64
        scale = 2
        image, draw = self._create_canvas(width, height)
        
        # 旗杆
        pole_color = '#8B4513'
        for y in range(32):
            self._draw_pixel(draw, 7, y, pole_color, scale)
            self._draw_pixel(draw, 8, y, pole_color, scale)
        
        # 旗帜（三角形）
        flag_color = '#FF0000'
        flag_dark = '#CC0000'
        for row in range(10):
            for col in range(row + 1):
                x = 9 + col
                y = 2 + row
                color = flag_color if col < row else flag_dark
                self._draw_pixel(draw, x, y, color, scale)
        
        # 旗杆顶部圆球
        ball_color = '#FFD700'
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if abs(dx) + abs(dy) <= 1:
                    self._draw_pixel(draw, 7 + dx, dy, ball_color, scale)
        
        return image
    
    # ==================== 批量生成方法 ====================
    
    def generate_all_sprites(self) -> Dict[str, str]:
        """
        生成所有游戏精灵并保存到对应目录
        
        Returns:
            生成的精灵文件路径字典
        """
        generated_files = {}
        
        # 玩家精灵
        print("生成玩家精灵...")
        for color_scheme in ['red_jumper', 'green_jumper']:
            prefix = color_scheme.replace('_jumper', '')
            
            # 站立
            img = self.generate_player_idle(color_scheme)
            path = os.path.join(self.output_dir, 'player', f'{prefix}_idle.png')
            img.save(path)
            generated_files[f'{prefix}_idle'] = path
            
            # 跑步动画
            for frame in range(1, 5):
                img = self.generate_player_run(color_scheme, frame)
                path = os.path.join(self.output_dir, 'player', f'{prefix}_run_{frame}.png')
                img.save(path)
                generated_files[f'{prefix}_run_{frame}'] = path
            
            # 跳跃
            img = self.generate_player_jump(color_scheme)
            path = os.path.join(self.output_dir, 'player', f'{prefix}_jump.png')
            img.save(path)
            generated_files[f'{prefix}_jump'] = path
        
        # 敌人精灵
        print("生成敌人精灵...")
        # 蘑菇怪
        for frame in range(1, 3):
            img = self.generate_mushling(frame)
            path = os.path.join(self.output_dir, 'enemies', f'mushling_walk_{frame}.png')
            img.save(path)
            generated_files[f'mushling_walk_{frame}'] = path
        
        img = self.generate_mushling(squashed=True)
        path = os.path.join(self.output_dir, 'enemies', 'mushling_squashed.png')
        img.save(path)
        generated_files['mushling_squashed'] = path
        
        # 乌龟壳怪
        for frame in range(1, 3):
            img = self.generate_shellback(frame)
            path = os.path.join(self.output_dir, 'enemies', f'shellback_walk_{frame}.png')
            img.save(path)
            generated_files[f'shellback_walk_{frame}'] = path
        
        img = self.generate_shellback(shell_mode=True)
        path = os.path.join(self.output_dir, 'enemies', 'shellback_shell.png')
        img.save(path)
        generated_files['shellback_shell'] = path
        
        # 飞行怪
        for frame in range(1, 5):
            img = self.generate_flapper(frame)
            path = os.path.join(self.output_dir, 'enemies', f'flapper_{frame}.png')
            img.save(path)
            generated_files[f'flapper_{frame}'] = path
        
        # 方块精灵
        print("生成方块精灵...")
        img = self.generate_ground_tile()
        path = os.path.join(self.output_dir, 'tiles', 'ground.png')
        img.save(path)
        generated_files['ground'] = path
        
        img = self.generate_brick()
        path = os.path.join(self.output_dir, 'tiles', 'brick.png')
        img.save(path)
        generated_files['brick'] = path
        
        for frame in range(1, 5):
            img = self.generate_question_block(frame)
            path = os.path.join(self.output_dir, 'tiles', f'question_block_{frame}.png')
            img.save(path)
            generated_files[f'question_block_{frame}'] = path
        
        img = self.generate_empty_block()
        path = os.path.join(self.output_dir, 'tiles', 'empty_block.png')
        img.save(path)
        generated_files['empty_block'] = path
        
        img = self.generate_pipe()
        path = os.path.join(self.output_dir, 'tiles', 'pipe.png')
        img.save(path)
        generated_files['pipe'] = path
        
        for blink in [False, True]:
            img = self.generate_spike(blink)
            suffix = '_blink' if blink else ''
            path = os.path.join(self.output_dir, 'tiles', f'spike{suffix}.png')
            img.save(path)
            generated_files[f'spike{suffix}'] = path
        
        img = self.generate_platform()
        path = os.path.join(self.output_dir, 'tiles', 'platform.png')
        img.save(path)
        generated_files['platform'] = path
        
        img = self.generate_flag()
        path = os.path.join(self.output_dir, 'tiles', 'flag.png')
        img.save(path)
        generated_files['flag'] = path
        
        # 道具精灵
        print("生成道具精灵...")
        for frame in range(1, 5):
            img = self.generate_coin(frame)
            path = os.path.join(self.output_dir, 'items', f'coin_{frame}.png')
            img.save(path)
            generated_files[f'coin_{frame}'] = path
        
        img = self.generate_mushroom_item()
        path = os.path.join(self.output_dir, 'items', 'mushroom.png')
        img.save(path)
        generated_files['mushroom'] = path
        
        for frame in range(1, 5):
            img = self.generate_star(frame)
            path = os.path.join(self.output_dir, 'items', f'star_{frame}.png')
            img.save(path)
            generated_files[f'star_{frame}'] = path
        
        print(f"完成！共生成 {len(generated_files)} 个精灵文件。")
        return generated_files


# ==================== 主函数 ====================
if __name__ == '__main__':
    # 获取项目根目录
    import sys
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    sprites_dir = os.path.join(project_root, 'assets', 'sprites')
    
    # 生成所有精灵
    generator = PixelSpriteGenerator(sprites_dir)
    files = generator.generate_all_sprites()
    
    print("\n生成的文件列表:")
    for name, path in files.items():
        print(f"  {name}: {path}")
