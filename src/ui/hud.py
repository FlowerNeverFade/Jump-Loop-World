"""
HUD模块
AI辅助生成: 实现游戏内界面显示

HUD (Heads-Up Display) 显示玩家的分数、生命、金币等信息。
"""

import pygame
from typing import TYPE_CHECKING, Optional

from ..settings import Colors, SCREEN_WIDTH, SCREEN_HEIGHT

if TYPE_CHECKING:
    from ..game import Game


class HUD:
    """
    游戏内显示类
    
    在游戏过程中显示玩家状态信息。
    
    Attributes:
        game: 游戏实例引用
        font: 显示字体
        small_font: 小号字体
    """
    
    def __init__(self, game: 'Game'):
        """
        初始化HUD
        
        Args:
            game: 游戏实例
        """
        self.game = game
        
        # 字体
        self.font: Optional[pygame.font.Font] = None
        self.small_font: Optional[pygame.font.Font] = None
        self._init_fonts()
        
        # 图标缓存
        self.coin_icon: Optional[pygame.Surface] = None
        self.life_icon: Optional[pygame.Surface] = None
        self._load_icons()
        
        # 帮助面板
        self.help_panel = HelpPanel()
        self.show_help = False
        
        # 帮助按钮位置
        self.help_button_rect = pygame.Rect(SCREEN_WIDTH - 80, 8, 24, 24)
    
    def _init_fonts(self) -> None:
        """初始化字体"""
        try:
            self.font = pygame.font.SysFont('microsoftyahei', 28)
            self.small_font = pygame.font.SysFont('microsoftyahei', 20)
        except:
            self.font = pygame.font.Font(None, 32)
            self.small_font = pygame.font.Font(None, 24)
    
    def _load_icons(self) -> None:
        """加载图标"""
        from ..core.resource_manager import ResourceManager
        rm = ResourceManager()
        
        try:
            # 使用金币和玩家头像作为图标
            coin_frames = rm.load_item_sprites().get('coin', [])
            if coin_frames:
                self.coin_icon = pygame.transform.scale(coin_frames[0], (20, 20))
            
            player_sprite = rm.load_image('player/red_idle.png')
            if player_sprite:
                self.life_icon = pygame.transform.scale(player_sprite, (24, 24))
        except Exception as e:
            print(f"HUD图标加载失败: {e}")
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        处理事件
        
        Returns:
            是否消费了事件（帮助面板打开时消费所有点击）
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # 点击帮助按钮
            if self.help_button_rect.collidepoint(event.pos):
                self.show_help = not self.show_help
                self.help_panel.current_page = 0  # 重置到第一页
                return True
            
            # 帮助面板打开时处理翻页点击
            if self.show_help:
                # 检查是否点击了翻页区域
                panel_width = 500
                panel_x = (SCREEN_WIDTH - panel_width) // 2
                panel_height = 380
                panel_y = (SCREEN_HEIGHT - panel_height) // 2
                
                # 左半边点击 - 上一页
                left_area = pygame.Rect(panel_x, panel_y, panel_width // 2, panel_height)
                # 右半边点击 - 下一页
                right_area = pygame.Rect(panel_x + panel_width // 2, panel_y, panel_width // 2, panel_height)
                
                if left_area.collidepoint(event.pos):
                    self.help_panel.prev_page()
                    return True
                elif right_area.collidepoint(event.pos):
                    if self.help_panel.current_page < len(self.help_panel.pages) - 1:
                        self.help_panel.next_page()
                        return True
                    else:
                        # 最后一页点击右侧关闭
                        self.show_help = False
                        return True
                
                return True  # 消费面板区域内的点击
        
        if event.type == pygame.KEYDOWN:
            if self.show_help:
                # 帮助面板打开时的按键处理
                if event.key in (pygame.K_h, pygame.K_ESCAPE):
                    self.show_help = False
                    return True
                # 左右键翻页
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self.help_panel.prev_page()
                    return True
                if event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.help_panel.next_page()
                    return True
            else:
                # 按H键打开帮助
                if event.key == pygame.K_h:
                    self.show_help = True
                    self.help_panel.current_page = 0
                    return True
        
        return False
    
    def render(self, screen: pygame.Surface) -> None:
        """
        渲染HUD
        
        Args:
            screen: 渲染目标
        """
        # 半透明背景条
        hud_bg = pygame.Surface((SCREEN_WIDTH, 40), pygame.SRCALPHA)
        hud_bg.fill((0, 0, 0, 128))
        screen.blit(hud_bg, (0, 0))
        
        # 分数
        self._render_score(screen)
        
        # 金币
        self._render_coins(screen)
        
        # 生命
        self._render_lives(screen)
        
        # 帮助按钮
        self._render_help_button(screen)
        
        # 难度显示
        self._render_difficulty(screen)
        
        # 帮助面板（如果打开）
        if self.show_help:
            self.help_panel.render(screen)
    
    def _render_score(self, screen: pygame.Surface) -> None:
        """渲染分数"""
        if not self.font:
            return
        
        score_text = f"分数: {self.game.score:06d}"
        text_surface = self.font.render(score_text, True, Colors.UI_TEXT)
        screen.blit(text_surface, (20, 5))
    
    def _render_coins(self, screen: pygame.Surface) -> None:
        """渲染金币数"""
        if not self.font:
            return
        
        # 金币图标
        if self.coin_icon:
            screen.blit(self.coin_icon, (200, 10))
        
        coin_text = f"x {self.game.coins:02d}"
        text_surface = self.font.render(coin_text, True, Colors.YELLOW)
        screen.blit(text_surface, (225, 5))
    
    def _render_lives(self, screen: pygame.Surface) -> None:
        """渲染生命数"""
        if not self.font:
            return
        
        # 生命图标
        if self.life_icon:
            screen.blit(self.life_icon, (350, 8))
        
        lives_text = f"x {self.game.lives}"
        text_surface = self.font.render(lives_text, True, Colors.UI_TEXT)
        screen.blit(text_surface, (380, 5))
    
    def _render_difficulty(self, screen: pygame.Surface) -> None:
        """渲染当前难度"""
        if not self.small_font:
            return
        
        difficulty_name = self.game.difficulty.get('name', '简单模式')
        if difficulty_name == '简单模式':
            color = Colors.GREEN
        elif difficulty_name == '变态模式':
            color = (200, 80, 200)  # 紫色
        else:
            color = Colors.RED
        
        text_surface = self.small_font.render(difficulty_name, True, color)
        text_rect = text_surface.get_rect(right=SCREEN_WIDTH - 90, centery=20)
        screen.blit(text_surface, text_rect)
    
    def _render_help_button(self, screen: pygame.Surface) -> None:
        """渲染帮助按钮"""
        # 按钮背景
        button_color = (80, 150, 220) if self.show_help else (60, 120, 180)
        pygame.draw.rect(screen, button_color, self.help_button_rect, border_radius=12)
        pygame.draw.rect(screen, (255, 255, 255), self.help_button_rect, width=2, border_radius=12)
        
        # 问号
        if self.font:
            question = self.font.render("?", True, (255, 255, 255))
            q_rect = question.get_rect(center=self.help_button_rect.center)
            screen.blit(question, q_rect)


class HelpPanel:
    """
    帮助面板类
    
    显示游戏帮助信息，包括操作说明、敌人介绍等。
    """
    
    def __init__(self):
        """初始化帮助面板"""
        # 字体
        try:
            self.title_font = pygame.font.SysFont('microsoftyahei', 24)
            self.content_font = pygame.font.SysFont('microsoftyahei', 16)
            self.small_font = pygame.font.SysFont('microsoftyahei', 14)
        except:
            self.title_font = pygame.font.Font(None, 28)
            self.content_font = pygame.font.Font(None, 18)
            self.small_font = pygame.font.Font(None, 16)
        
        # 当前页面
        self.current_page = 0
        self.pages = self._create_pages()
    
    def _create_pages(self) -> list:
        """创建帮助页面内容"""
        return [
            {
                'title': '操作说明',
                'content': [
                    ('← → 或 A D', '左右移动'),
                    ('空格 或 W', '跳跃'),
                    ('长按跳跃键', '跳得更高'),
                    ('↓ 或 S', '下砸（需解锁）'),
                    ('Shift', '冲刺（需解锁）'),
                    ('贴墙+跳跃', '踢墙跳（需解锁）'),
                    ('H', '打开/关闭帮助'),
                    ('ESC', '暂停游戏'),
                    ('F11', '全屏切换'),
                ]
            },
            {
                'title': '敌人介绍',
                'content': [
                    ('🍄 蘑菇怪', '最基础的敌人，来回巡逻'),
                    ('', '踩一下即可消灭'),
                    ('🐢 乌龟', '踩一下变成龟壳'),
                    ('', '再踩或碰触可踢出龟壳'),
                    ('', '滚动的龟壳可消灭敌人'),
                    ('🦇 飞行怪', '在空中上下飞行'),
                    ('', '踩一下即可消灭'),
                    ('⚠️ 尖刺', '碰到会受伤（困难模式）'),
                ]
            },
            {
                'title': '道具介绍',
                'content': [
                    ('🪙 金币', '收集金币，100个+1命'),
                    ('', '通关后金币可在商店使用'),
                    ('🍄 蘑菇', '变大，可多挡一次伤害'),
                    ('⭐ 星星', '无敌状态，碰敌人直接消灭'),
                    ('❓ 问号块', '顶撞可获得金币或道具'),
                    ('🧱 砖块', '大状态下可顶碎'),
                ]
            },
            {
                'title': '升级系统（商店）',
                'content': [
                    ('生命强化', '增加初始生命数'),
                    ('疾风步', '提升移动速度'),
                    ('弹跳力', '提升跳跃高度'),
                    ('金币磁铁', '自动吸引附近金币'),
                    ('护盾延长', '受伤后无敌时间更长'),
                ]
            },
            {
                'title': '特殊能力（商店）',
                'content': [
                    ('二段跳', '空中可再跳一次'),
                    ('冲刺', 'Shift键快速冲刺'),
                    ('踢墙跳', '贴墙滑落时可蹬墙跳'),
                    ('下砸', '空中按↓快速下落'),
                ]
            },
            {
                'title': '装备系统（商店）',
                'content': [
                    ('【帽子】', ''),
                    ('幸运帽', '概率双倍金币'),
                    ('安全帽', '概率抵挡伤害'),
                    ('【靴子】', ''),
                    ('疾风靴/弹簧靴', '速度/跳跃加成'),
                    ('【饰品】', ''),
                    ('护符系列', '各种属性加成'),
                ]
            },
        ]
    
    def render(self, screen: pygame.Surface) -> None:
        """渲染帮助面板"""
        # 半透明背景遮罩
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # 面板
        panel_width = 500
        panel_height = 380
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2
        
        # 面板背景
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(screen, (40, 50, 70), panel_rect, border_radius=15)
        pygame.draw.rect(screen, (100, 150, 200), panel_rect, width=3, border_radius=15)
        
        # 当前页面内容
        page = self.pages[self.current_page]
        
        # 标题
        title = self.title_font.render(page['title'], True, (255, 220, 100))
        title_rect = title.get_rect(centerx=SCREEN_WIDTH // 2, top=panel_y + 15)
        screen.blit(title, title_rect)
        
        # 内容
        y_offset = panel_y + 55
        for item in page['content']:
            if len(item) == 2:
                key, desc = item
                if key:
                    # 键/名称
                    key_surface = self.content_font.render(key, True, (150, 220, 255))
                    screen.blit(key_surface, (panel_x + 30, y_offset))
                    
                    # 描述
                    desc_surface = self.content_font.render(desc, True, (220, 220, 220))
                    screen.blit(desc_surface, (panel_x + 180, y_offset))
                else:
                    # 续行描述（无键名）
                    desc_surface = self.small_font.render(f"    {desc}", True, (180, 180, 180))
                    screen.blit(desc_surface, (panel_x + 180, y_offset))
                    y_offset -= 5  # 续行减少间距
            
            y_offset += 28
        
        # 页面指示器和导航提示
        page_info = f"第 {self.current_page + 1}/{len(self.pages)} 页"
        page_surface = self.small_font.render(page_info, True, (150, 150, 150))
        page_rect = page_surface.get_rect(centerx=SCREEN_WIDTH // 2, bottom=panel_y + panel_height - 40)
        screen.blit(page_surface, page_rect)
        
        # 导航按钮
        nav_y = panel_y + panel_height - 35
        
        # 上一页
        if self.current_page > 0:
            prev_text = "◀ 上一页"
            prev_surface = self.content_font.render(prev_text, True, (100, 200, 255))
            prev_rect = prev_surface.get_rect(left=panel_x + 30, centery=nav_y)
            screen.blit(prev_surface, prev_rect)
        
        # 下一页
        if self.current_page < len(self.pages) - 1:
            next_text = "下一页 ▶"
            next_surface = self.content_font.render(next_text, True, (100, 200, 255))
            next_rect = next_surface.get_rect(right=panel_x + panel_width - 30, centery=nav_y)
            screen.blit(next_surface, next_rect)
        
        # 关闭提示
        close_text = "点击任意位置或按 H/ESC 关闭"
        close_surface = self.small_font.render(close_text, True, (120, 120, 120))
        close_rect = close_surface.get_rect(centerx=SCREEN_WIDTH // 2, bottom=panel_y + panel_height - 10)
        screen.blit(close_surface, close_rect)
    
    def next_page(self) -> None:
        """下一页"""
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
    
    def prev_page(self) -> None:
        """上一页"""
        if self.current_page > 0:
            self.current_page -= 1