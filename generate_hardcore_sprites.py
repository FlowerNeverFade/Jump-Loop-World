"""
变态模式精灵生成器
使用Pillow生成新敌人和障碍物的像素艺术图片
"""

from PIL import Image, ImageDraw
import os

# 确保目录存在
os.makedirs('assets/sprites/enemies', exist_ok=True)
os.makedirs('assets/sprites/obstacles', exist_ok=True)

TILE_SIZE = 32


def create_jumper_sprites():
    """创建跳跃怪精灵 - 弹簧腿的蓝色生物"""
    # 基础帧
    for i, state in enumerate(['idle', 'jump']):
        img = Image.new('RGBA', (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 身体 - 蓝色圆形
        body_color = (80, 150, 255)
        if state == 'jump':
            # 跳跃时身体拉长
            draw.ellipse([8, 2, 24, 20], fill=body_color, outline=(50, 100, 200))
        else:
            draw.ellipse([6, 8, 26, 26], fill=body_color, outline=(50, 100, 200))
        
        # 眼睛
        draw.ellipse([10, 12 if state == 'idle' else 6, 14, 16 if state == 'idle' else 10], fill='white')
        draw.ellipse([18, 12 if state == 'idle' else 6, 22, 16 if state == 'idle' else 10], fill='white')
        draw.ellipse([11, 13 if state == 'idle' else 7, 13, 15 if state == 'idle' else 9], fill='black')
        draw.ellipse([19, 13 if state == 'idle' else 7, 21, 15 if state == 'idle' else 9], fill='black')
        
        # 弹簧腿
        spring_color = (200, 200, 200)
        if state == 'jump':
            # 伸展的弹簧
            for y in range(20, 32, 3):
                draw.line([12, y, 12, y+2], fill=spring_color, width=2)
                draw.line([20, y, 20, y+2], fill=spring_color, width=2)
        else:
            # 压缩的弹簧
            for y in range(26, 32, 2):
                draw.line([10, y, 14, y], fill=spring_color, width=2)
                draw.line([18, y, 22, y], fill=spring_color, width=2)
        
        img.save(f'assets/sprites/enemies/jumper_{state}.png')
    
    print("跳跃怪精灵已生成")


def create_shooter_sprites():
    """创建发射怪精灵 - 会发射子弹的炮塔"""
    for i, state in enumerate(['idle', 'shoot']):
        img = Image.new('RGBA', (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 底座 - 紫色
        base_color = (150, 80, 180)
        draw.rectangle([4, 20, 28, 32], fill=base_color, outline=(100, 50, 130))
        
        # 炮管
        cannon_color = (100, 100, 120)
        if state == 'shoot':
            # 发射时炮管后坐
            draw.rectangle([8, 8, 24, 20], fill=cannon_color, outline=(70, 70, 90))
            draw.ellipse([10, 4, 22, 12], fill=(200, 100, 50))  # 火焰
        else:
            draw.rectangle([6, 8, 26, 20], fill=cannon_color, outline=(70, 70, 90))
        
        # 炮口
        draw.ellipse([10, 6, 22, 14], fill=(50, 50, 60))
        
        # 眼睛（在炮管上）
        draw.ellipse([12, 12, 16, 16], fill=(255, 50, 50))
        draw.ellipse([18, 12, 22, 16], fill=(255, 50, 50))
        
        img.save(f'assets/sprites/enemies/shooter_{state}.png')
    
    # 子弹
    bullet = Image.new('RGBA', (12, 12), (0, 0, 0, 0))
    draw = ImageDraw.Draw(bullet)
    draw.ellipse([0, 0, 11, 11], fill=(255, 100, 50), outline=(200, 50, 0))
    draw.ellipse([3, 3, 7, 7], fill=(255, 200, 100))
    bullet.save('assets/sprites/enemies/bullet.png')
    
    print("发射怪精灵已生成")


def create_ghost_sprites():
    """创建幽灵怪精灵 - 可以穿墙的半透明敌人"""
    for i in range(2):
        img = Image.new('RGBA', (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 幽灵身体 - 半透明白色
        ghost_color = (220, 220, 255, 180)
        
        # 波浪形底部
        points = [(6, 10), (16, 8), (26, 10), (28, 20), (26, 28 + i*2), 
                  (22, 26 - i*2), (18, 28 + i*2), (14, 26 - i*2), 
                  (10, 28 + i*2), (6, 26 - i*2), (4, 20)]
        draw.polygon(points, fill=ghost_color)
        
        # 眼睛 - 空洞的黑色
        draw.ellipse([8, 12, 14, 20], fill='black')
        draw.ellipse([18, 12, 24, 20], fill='black')
        
        # 瞳孔 - 发光的白点
        draw.ellipse([10, 14 + i, 12, 16 + i], fill='white')
        draw.ellipse([20, 14 + i, 22, 16 + i], fill='white')
        
        img.save(f'assets/sprites/enemies/ghost_{i+1}.png')
    
    print("幽灵怪精灵已生成")


def create_giant_sprites():
    """创建巨型怪精灵 - 需要踩三次才能消灭"""
    for state in ['normal', 'hurt1', 'hurt2']:
        img = Image.new('RGBA', (TILE_SIZE * 2, TILE_SIZE * 2), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 颜色随受伤程度变化
        if state == 'normal':
            body_color = (200, 50, 50)
        elif state == 'hurt1':
            body_color = (200, 100, 50)
        else:
            body_color = (200, 150, 50)
        
        # 巨大的身体
        draw.ellipse([8, 16, 56, 56], fill=body_color, outline=(150, 30, 30))
        
        # 大眼睛
        draw.ellipse([14, 24, 28, 40], fill='white', outline='black')
        draw.ellipse([36, 24, 50, 40], fill='white', outline='black')
        
        # 愤怒的瞳孔
        draw.ellipse([18, 28, 24, 36], fill='black')
        draw.ellipse([40, 28, 46, 36], fill='black')
        
        # 愤怒的眉毛
        draw.line([14, 22, 28, 26], fill='black', width=3)
        draw.line([50, 26, 36, 22], fill='black', width=3)
        
        # 脚
        draw.ellipse([12, 52, 24, 62], fill=body_color, outline=(150, 30, 30))
        draw.ellipse([40, 52, 52, 62], fill=body_color, outline=(150, 30, 30))
        
        img.save(f'assets/sprites/enemies/giant_{state}.png')
    
    print("巨型怪精灵已生成")


def create_spike_ball_sprites():
    """创建滚动尖球 - 沿着平台滚动"""
    for i in range(4):  # 4帧旋转动画
        img = Image.new('RGBA', (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 主体 - 灰色金属球
        draw.ellipse([2, 2, 30, 30], fill=(100, 100, 110), outline=(60, 60, 70))
        
        # 尖刺 - 围绕球旋转
        import math
        for j in range(8):
            angle = (j * 45 + i * 15) * math.pi / 180
            cx, cy = 16, 16
            r = 14
            sx = cx + int(r * math.cos(angle))
            sy = cy + int(r * math.sin(angle))
            ex = cx + int((r + 6) * math.cos(angle))
            ey = cy + int((r + 6) * math.sin(angle))
            draw.line([sx, sy, ex, ey], fill=(180, 180, 190), width=3)
        
        img.save(f'assets/sprites/enemies/spikeball_{i+1}.png')
    
    print("滚动尖球精灵已生成")


def create_spring_obstacle():
    """创建弹簧障碍物 - 踩上去会弹跳"""
    for state in ['idle', 'compressed']:
        img = Image.new('RGBA', (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 底座
        draw.rectangle([4, 28, 28, 32], fill=(150, 100, 50), outline=(100, 70, 30))
        
        # 弹簧
        spring_color = (220, 180, 50)
        if state == 'compressed':
            # 压缩状态
            for y in range(20, 28, 2):
                draw.line([6, y, 26, y], fill=spring_color, width=2)
        else:
            # 正常状态
            for y in range(8, 28, 3):
                offset = (y // 3) % 2 * 4
                draw.line([8 + offset, y, 24 - offset, y], fill=spring_color, width=2)
        
        # 顶部平台
        top_y = 6 if state == 'idle' else 18
        draw.ellipse([6, top_y, 26, top_y + 8], fill=(255, 100, 100), outline=(200, 50, 50))
        
        img.save(f'assets/sprites/obstacles/spring_{state}.png')
    
    print("弹簧障碍物已生成")


def create_portal_obstacle():
    """创建传送门 - 传送玩家到另一个位置"""
    for color, name in [((100, 150, 255), 'blue'), ((255, 150, 100), 'orange')]:
        for i in range(4):  # 动画帧
            img = Image.new('RGBA', (TILE_SIZE, TILE_SIZE * 2), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # 门框
            draw.rectangle([2, 2, 30, 62], fill=None, outline=(50, 50, 70), width=3)
            
            # 旋转的能量
            import math
            for j in range(12):
                angle = (j * 30 + i * 20) * math.pi / 180
                r = 10 + (j % 3) * 3
                cx, cy = 16, 32
                x = cx + int(r * math.cos(angle))
                y = cy + int(r * math.sin(angle))
                alpha = 150 + (j % 3) * 30
                c = (*color, alpha)
                draw.ellipse([x-2, y-2, x+2, y+2], fill=c)
            
            # 中心光芒
            center_color = (255, 255, 255, 200)
            draw.ellipse([10, 26, 22, 38], fill=center_color)
            
            img.save(f'assets/sprites/obstacles/portal_{name}_{i+1}.png')
    
    print("传送门障碍物已生成")


def create_laser_obstacle():
    """创建激光障碍物 - 周期性发射激光"""
    # 发射器
    for state in ['off', 'charging', 'on']:
        img = Image.new('RGBA', (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 发射器外壳
        draw.rectangle([4, 8, 28, 24], fill=(80, 80, 90), outline=(50, 50, 60))
        
        # 发射口
        if state == 'off':
            draw.ellipse([10, 12, 22, 20], fill=(40, 40, 50))
        elif state == 'charging':
            draw.ellipse([10, 12, 22, 20], fill=(200, 50, 50))
        else:
            draw.ellipse([10, 12, 22, 20], fill=(255, 100, 100))
            # 发光效果
            draw.ellipse([8, 10, 24, 22], fill=None, outline=(255, 150, 150), width=1)
        
        img.save(f'assets/sprites/obstacles/laser_emitter_{state}.png')
    
    # 激光束
    laser = Image.new('RGBA', (TILE_SIZE * 8, 8), (0, 0, 0, 0))
    draw = ImageDraw.Draw(laser)
    draw.rectangle([0, 2, TILE_SIZE * 8, 6], fill=(255, 50, 50, 200))
    draw.rectangle([0, 3, TILE_SIZE * 8, 5], fill=(255, 200, 200, 255))
    laser.save('assets/sprites/obstacles/laser_beam.png')
    
    print("激光障碍物已生成")


def create_crumbling_platform():
    """创建碎裂平台 - 踩上去会碎"""
    for state in ['solid', 'cracking', 'broken']:
        img = Image.new('RGBA', (TILE_SIZE, TILE_SIZE // 2), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        platform_color = (180, 140, 100)
        
        if state == 'solid':
            draw.rectangle([0, 0, 32, 16], fill=platform_color, outline=(140, 100, 60))
        elif state == 'cracking':
            # 裂纹
            draw.rectangle([0, 0, 32, 16], fill=platform_color, outline=(140, 100, 60))
            draw.line([8, 0, 12, 16], fill=(100, 60, 40), width=1)
            draw.line([20, 0, 16, 16], fill=(100, 60, 40), width=1)
            draw.line([0, 8, 32, 8], fill=(100, 60, 40), width=1)
        else:
            # 碎片
            for x, y, w, h in [(0, 0, 10, 8), (12, 2, 8, 6), (22, 0, 10, 8), (4, 10, 8, 6), (16, 8, 10, 8)]:
                draw.rectangle([x, y, x+w, y+h], fill=platform_color, outline=(140, 100, 60))
        
        img.save(f'assets/sprites/obstacles/crumble_{state}.png')
    
    print("碎裂平台已生成")


def create_moving_saw():
    """创建移动锯齿 - 沿轨道移动的危险障碍"""
    for i in range(4):
        img = Image.new('RGBA', (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        import math
        cx, cy = 16, 16
        
        # 锯齿外圈
        for j in range(16):
            angle = (j * 22.5 + i * 10) * math.pi / 180
            inner_r = 8
            outer_r = 14 if j % 2 == 0 else 10
            x1 = cx + int(inner_r * math.cos(angle))
            y1 = cy + int(inner_r * math.sin(angle))
            x2 = cx + int(outer_r * math.cos(angle))
            y2 = cy + int(outer_r * math.sin(angle))
            draw.line([x1, y1, x2, y2], fill=(180, 180, 190), width=2)
        
        # 中心
        draw.ellipse([8, 8, 24, 24], fill=(100, 100, 110), outline=(70, 70, 80))
        draw.ellipse([12, 12, 20, 20], fill=(60, 60, 70))
        
        img.save(f'assets/sprites/obstacles/saw_{i+1}.png')
    
    print("移动锯齿已生成")


def create_ice_platform():
    """创建冰面平台 - 滑动效果"""
    img = Image.new('RGBA', (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 冰蓝色平台
    draw.rectangle([0, 0, 32, 32], fill=(180, 220, 255, 200), outline=(150, 200, 255))
    
    # 光泽
    draw.line([4, 4, 12, 4], fill=(255, 255, 255, 150), width=2)
    draw.line([4, 4, 4, 12], fill=(255, 255, 255, 150), width=2)
    
    # 裂纹纹理
    draw.line([8, 16, 24, 12], fill=(200, 230, 255), width=1)
    draw.line([16, 20, 28, 24], fill=(200, 230, 255), width=1)
    
    img.save('assets/sprites/tiles/ice_platform.png')
    print("冰面平台已生成")


def create_lava_tile():
    """创建岩浆地形"""
    for i in range(4):
        img = Image.new('RGBA', (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 岩浆底色
        draw.rectangle([0, 0, 32, 32], fill=(200, 50, 0))
        
        # 气泡和波纹
        import random
        random.seed(i)
        for _ in range(5):
            x = random.randint(4, 28)
            y = random.randint(4, 28)
            r = random.randint(2, 5)
            draw.ellipse([x-r, y-r, x+r, y+r], fill=(255, 150, 0, 200))
        
        # 亮色条纹
        draw.line([0, 8 + i*2, 32, 12 + i*2], fill=(255, 200, 50), width=2)
        draw.line([0, 20 + i, 32, 24 + i], fill=(255, 180, 30), width=1)
        
        img.save(f'assets/sprites/tiles/lava_{i+1}.png')
    
    print("岩浆地形已生成")


def main():
    """生成所有变态模式精灵"""
    print("=" * 50)
    print("开始生成变态模式精灵...")
    print("=" * 50)
    
    # 敌人精灵
    create_jumper_sprites()
    create_shooter_sprites()
    create_ghost_sprites()
    create_giant_sprites()
    create_spike_ball_sprites()
    
    # 障碍物精灵
    create_spring_obstacle()
    create_portal_obstacle()
    create_laser_obstacle()
    create_crumbling_platform()
    create_moving_saw()
    
    # 地形精灵
    create_ice_platform()
    create_lava_tile()
    
    print("=" * 50)
    print("所有变态模式精灵生成完成!")
    print("=" * 50)


if __name__ == '__main__':
    main()
