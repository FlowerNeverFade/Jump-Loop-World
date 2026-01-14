"""
商店状态模块
AI辅助生成: 实现Roguelike商店界面

允许玩家使用金币购买升级、能力和装备。
"""

import pygame
from typing import TYPE_CHECKING, List, Optional

from .game_state import GameState
from ..ui.button import Button
from ..core.save_manager import SaveManager
from ..core.roguelike_data import (
    RoguelikeData, ShopCategory, ShopItem,
    UpgradeDefinition, AbilityDefinition, EquipmentDefinition
)
from ..settings import Colors, SCREEN_WIDTH, SCREEN_HEIGHT, DifficultySettings

if TYPE_CHECKING:
    from ..game import Game
    from ..core.state_machine import StateMachine


class ShopState(GameState):
    """
    商店状态
    
    显示可购买的升级、能力和装备列表。
    """
    
    def __init__(self, game: 'Game', state_machine: 'StateMachine'):
        super().__init__(game, state_machine)
        
        self.save_manager = SaveManager()
        
        # 当前选中的分类
        self.current_category = ShopCategory.UPGRADES
        
        # 商店物品列表
        self.shop_items: List[ShopItem] = []
        
        # 分类按钮
        self.category_buttons: List[Button] = []
        
        # 操作按钮（开始游戏、返回）
        self.action_buttons: List[Button] = []
        
        # 当前选中的物品索引
        self.selected_index = 0
        
        # 滚动偏移
        self.scroll_offset = 0
        self.max_visible_items = 4  # 减少可见数量避免重叠
        
        # 冒险模式难度选择
        self.selected_difficulty = 'easy'
        
        # 字体
        try:
            self.title_font = pygame.font.SysFont('microsoftyahei', 32)
            self.item_font = pygame.font.SysFont('microsoftyahei', 22)
            self.desc_font = pygame.font.SysFont('microsoftyahei', 16)
            self.coin_font = pygame.font.SysFont('microsoftyahei', 24)
        except:
            self.title_font = pygame.font.Font(None, 36)
            self.item_font = pygame.font.Font(None, 26)
            self.desc_font = pygame.font.Font(None, 18)
            self.coin_font = pygame.font.Font(None, 28)
    
    def enter(self, **kwargs) -> None:
        """进入商店状态"""
        # 商店界面使用菜单音乐
        try:
            self.game.audio_manager.play_music('menu')
        except Exception:
            pass
        # 同步当前游戏难度到商店选择（避免每次进入都默认“简单”）
        if self.game.difficulty == DifficultySettings.HARD:
            self.selected_difficulty = 'hard'
        elif self.game.difficulty == DifficultySettings.HARDCORE:
            self.selected_difficulty = 'hardcore'
        else:
            self.selected_difficulty = 'easy'
        
        self._create_category_buttons()
        self._load_shop_items()
    
    def exit(self) -> None:
        """退出商店状态"""
        # 保存存档
        self.save_manager.save_current()
        self.category_buttons.clear()
        self.action_buttons.clear()
        self.shop_items.clear()
    
    def _create_category_buttons(self) -> None:
        """创建分类切换按钮和操作按钮"""
        self.category_buttons.clear()
        
        button_width = 100
        button_height = 35
        spacing = 10
        start_x = (SCREEN_WIDTH - (button_width * 3 + spacing * 2)) // 2
        y = 60
        
        categories = [
            (ShopCategory.UPGRADES, "升级"),
            (ShopCategory.ABILITIES, "能力"),
            (ShopCategory.EQUIPMENT, "装备"),
        ]
        
        for i, (cat, name) in enumerate(categories):
            btn = Button(
                x=start_x + i * (button_width + spacing),
                y=y,
                width=button_width,
                height=button_height,
                text=name,
                callback=lambda c=cat: self._switch_category(c)
            )
            self.category_buttons.append(btn)
        
        # 底部操作按钮
        self.action_buttons: List[Button] = []
        action_y = SCREEN_HEIGHT - 65  # 上移避免与提示重叠
        
        # 按钮尺寸和布局（紧凑排列）
        diff_btn_w = 60  # 难度按钮宽度
        start_btn_w = 90  # 开始按钮宽度
        back_btn_w = 60  # 返回按钮宽度
        btn_h = 36
        btn_spacing = 8
        
        # 计算总宽度并居中
        total_w = diff_btn_w * 3 + start_btn_w + back_btn_w + btn_spacing * 4
        start_x = (SCREEN_WIDTH - total_w) // 2
        
        # 难度选择按钮
        easy_btn = Button(
            x=start_x,
            y=action_y,
            width=diff_btn_w,
            height=btn_h,
            text="简单",
            callback=self._select_easy
        )
        self.action_buttons.append(easy_btn)
        
        hard_btn = Button(
            x=start_x + diff_btn_w + btn_spacing,
            y=action_y,
            width=diff_btn_w,
            height=btn_h,
            text="困难",
            callback=self._select_hard
        )
        self.action_buttons.append(hard_btn)
        
        hardcore_btn = Button(
            x=start_x + (diff_btn_w + btn_spacing) * 2,
            y=action_y,
            width=diff_btn_w,
            height=btn_h,
            text="变态",
            callback=self._select_hardcore
        )
        self.action_buttons.append(hardcore_btn)
        
        # 开始冒险按钮
        start_btn = Button(
            x=start_x + (diff_btn_w + btn_spacing) * 3,
            y=action_y,
            width=start_btn_w,
            height=btn_h,
            text="开始",
            callback=self._start_adventure
        )
        self.action_buttons.append(start_btn)
        
        # 返回按钮
        back_btn = Button(
            x=start_x + (diff_btn_w + btn_spacing) * 3 + start_btn_w + btn_spacing,
            y=action_y,
            width=back_btn_w,
            height=btn_h,
            text="返回",
            callback=self._go_back
        )
        self.action_buttons.append(back_btn)
    
    def _switch_category(self, category: ShopCategory) -> None:
        """切换商品分类"""
        self.current_category = category
        self.selected_index = 0
        self.scroll_offset = 0
        self._load_shop_items()
    
    def _load_shop_items(self) -> None:
        """加载当前分类的商品"""
        self.shop_items.clear()
        
        save_data = self.save_manager.get_current_save()
        if not save_data:
            return
        
        upgrades = save_data.get('upgrades', {})
        abilities = save_data.get('abilities', {})
        purchased = save_data.get('purchased_items', [])
        
        if self.current_category == ShopCategory.UPGRADES:
            for upgrade in RoguelikeData.get_all_upgrades():
                current_level = upgrades.get(upgrade.id, 0)
                cost = upgrade.get_cost(current_level)
                item = ShopItem(
                    item_id=upgrade.id,
                    name=upgrade.name,
                    description=upgrade.description,
                    cost=cost if cost > 0 else 0,
                    category=ShopCategory.UPGRADES,
                    current_level=current_level,
                    max_level=upgrade.max_level,
                    is_purchased=(current_level >= upgrade.max_level)
                )
                self.shop_items.append(item)
        
        elif self.current_category == ShopCategory.ABILITIES:
            for ability in RoguelikeData.get_all_abilities():
                is_unlocked = abilities.get(ability.id, False)
                item = ShopItem(
                    item_id=ability.id,
                    name=ability.name,
                    description=ability.description,
                    cost=ability.cost,
                    category=ShopCategory.ABILITIES,
                    is_purchased=is_unlocked
                )
                self.shop_items.append(item)
        
        elif self.current_category == ShopCategory.EQUIPMENT:
            # 获取当前装备的物品
            equipped = save_data.get('equipment', {})
            equipped_items = [v for v in equipped.values() if v]
            
            for equipment in RoguelikeData.get_all_equipment():
                is_owned = equipment.id in purchased
                is_equipped = equipment.id in equipped_items
                item = ShopItem(
                    item_id=equipment.id,
                    name=equipment.name,
                    description=equipment.description,
                    cost=equipment.cost,
                    category=ShopCategory.EQUIPMENT,
                    is_purchased=is_owned
                )
                # 标记是否已装备
                item.is_equipped = is_equipped
                item.slot = equipment.slot.name.lower()  # hat, boots, accessory
                self.shop_items.append(item)
    
    def _purchase_item(self) -> None:
        """购买或装备当前选中的物品"""
        if not self.shop_items or self.selected_index >= len(self.shop_items):
            return
        
        item = self.shop_items[self.selected_index]
        save_data = self.save_manager.get_current_save()
        if not save_data:
            return
        
        # 装备类物品特殊处理：已拥有的可以装备/卸下
        if item.category == ShopCategory.EQUIPMENT and item.is_purchased:
            self._toggle_equipment(item, save_data)
            return
        
        if not item.can_purchase:
            return
        
        # 检查金币
        current_coins = self.save_manager.get_coins()
        if current_coins < item.cost:
            return  # 金币不足
        
        # 扣除金币
        if not self.save_manager.spend_coins(item.cost):
            return
        
        if item.category == ShopCategory.UPGRADES:
            save_data['upgrades'][item.item_id] = item.current_level + 1
        
        elif item.category == ShopCategory.ABILITIES:
            save_data['abilities'][item.item_id] = True
        
        elif item.category == ShopCategory.EQUIPMENT:
            if 'purchased_items' not in save_data:
                save_data['purchased_items'] = []
            save_data['purchased_items'].append(item.item_id)
            # 购买后自动装备
            self._equip_item(item, save_data)
        
        # 刷新列表
        self._load_shop_items()
    
    def _toggle_equipment(self, item: ShopItem, save_data: dict) -> None:
        """切换装备状态"""
        slot = getattr(item, 'slot', None)
        if not slot:
            return
        
        if 'equipment' not in save_data:
            save_data['equipment'] = {'hat': None, 'boots': None, 'accessory': None}
        
        is_equipped = getattr(item, 'is_equipped', False)
        
        if is_equipped:
            # 卸下装备
            save_data['equipment'][slot] = None
        else:
            # 装备物品
            save_data['equipment'][slot] = item.item_id
        
        # 刷新列表
        self._load_shop_items()
    
    def _equip_item(self, item: ShopItem, save_data: dict) -> None:
        """装备物品"""
        slot = getattr(item, 'slot', None)
        if not slot:
            return
        
        if 'equipment' not in save_data:
            save_data['equipment'] = {'hat': None, 'boots': None, 'accessory': None}
        
        save_data['equipment'][slot] = item.item_id
    
    def _select_easy(self) -> None:
        """选择简单难度"""
        self.selected_difficulty = 'easy'
    
    def _select_hard(self) -> None:
        """选择困难难度"""
        self.selected_difficulty = 'hard'
    
    def _select_hardcore(self) -> None:
        """选择变态难度"""
        self.selected_difficulty = 'hardcore'
    
    def _start_adventure(self) -> None:
        """开始冒险（进入游戏）"""
        self.game.set_difficulty(self.selected_difficulty)
        self.game.reset_game_data()
        # 变态模式使用特殊关卡
        if self.selected_difficulty == 'hardcore':
            self.state_machine.change_state('play', hardcore=True)
        else:
            self.state_machine.change_state('play')
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """处理事件"""
        # 分类按钮
        for btn in self.category_buttons:
            btn.handle_event(event)
        
        # 操作按钮
        for btn in self.action_buttons:
            btn.handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._go_back()
            elif event.key == pygame.K_UP:
                self._navigate(-1)
            elif event.key == pygame.K_DOWN:
                self._navigate(1)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._purchase_item()
            elif event.key == pygame.K_LEFT:
                self._switch_category_by_direction(-1)
            elif event.key == pygame.K_RIGHT:
                self._switch_category_by_direction(1)
            elif event.key == pygame.K_s:
                self._start_adventure()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self._handle_click(event.pos)
    
    def _navigate(self, direction: int) -> None:
        """导航商品列表"""
        if not self.shop_items:
            return
        
        self.selected_index = (self.selected_index + direction) % len(self.shop_items)
        
        # 调整滚动
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.max_visible_items:
            self.scroll_offset = self.selected_index - self.max_visible_items + 1
    
    def _switch_category_by_direction(self, direction: int) -> None:
        """通过方向键切换分类"""
        categories = [ShopCategory.UPGRADES, ShopCategory.ABILITIES, ShopCategory.EQUIPMENT]
        current_idx = categories.index(self.current_category)
        new_idx = (current_idx + direction) % len(categories)
        self._switch_category(categories[new_idx])
    
    def _handle_click(self, pos: tuple) -> None:
        """处理点击事件"""
        # 检查是否点击了商品
        item_start_y = 120
        item_height = 60
        
        for i, item in enumerate(self.shop_items[self.scroll_offset:self.scroll_offset + self.max_visible_items]):
            item_y = item_start_y + i * item_height
            item_rect = pygame.Rect(50, item_y, SCREEN_WIDTH - 100, item_height - 5)
            
            if item_rect.collidepoint(pos):
                self.selected_index = self.scroll_offset + i
                self._purchase_item()
                return
    
    def _go_back(self) -> None:
        """返回主菜单"""
        self.state_machine.change_state('menu')
    
    def update(self, dt: float) -> None:
        """更新状态"""
        for btn in self.category_buttons:
            btn.update(dt)
        for btn in self.action_buttons:
            btn.update(dt)
    
    def render(self, screen: pygame.Surface) -> None:
        """渲染商店界面"""
        screen.fill(Colors.UI_BACKGROUND)
        
        # 标题
        title = self.title_font.render("商店", True, Colors.UI_HIGHLIGHT)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 15))
        
        # 金币显示
        coins = self.save_manager.get_coins()
        coin_text = self.coin_font.render(f"金币: {coins}", True, (255, 215, 0))
        screen.blit(coin_text, (SCREEN_WIDTH - coin_text.get_width() - 20, 20))
        
        # 显示当前选择的难度
        self._render_difficulty_indicator(screen)
        
        # 分类按钮
        for i, btn in enumerate(self.category_buttons):
            # 高亮当前分类
            categories = [ShopCategory.UPGRADES, ShopCategory.ABILITIES, ShopCategory.EQUIPMENT]
            if categories[i] == self.current_category:
                btn.bg_color = (100, 150, 200)
            else:
                btn.bg_color = Colors.UI_BUTTON
            btn.render(screen)
        
        # 商品列表
        self._render_items(screen)
        
        # 操作按钮（高亮当前选中的难度）
        for i, btn in enumerate(self.action_buttons):
            # 前三个按钮是难度选择按钮
            if i == 0:  # 简单
                if self.selected_difficulty == 'easy':
                    btn.bg_color = (80, 180, 80)  # 绿色高亮
                else:
                    btn.bg_color = Colors.UI_BUTTON
            elif i == 1:  # 困难
                if self.selected_difficulty == 'hard':
                    btn.bg_color = (200, 80, 80)  # 红色高亮
                else:
                    btn.bg_color = Colors.UI_BUTTON
            elif i == 2:  # 变态
                if self.selected_difficulty == 'hardcore':
                    btn.bg_color = (180, 50, 180)  # 紫色高亮
                else:
                    btn.bg_color = Colors.UI_BUTTON
            btn.render(screen)
        
        # 操作提示
        self._render_hints(screen)
    
    def _truncate_text(self, text: str, font: pygame.font.Font, max_width: int) -> str:
        """截断文字以适应最大宽度"""
        if font.size(text)[0] <= max_width:
            return text
        
        # 逐字减少直到适合
        while len(text) > 0 and font.size(text + "...")[0] > max_width:
            text = text[:-1]
        
        return text + "..." if text else "..."
    
    def _render_items(self, screen: pygame.Surface) -> None:
        """渲染商品列表"""
        if not self.shop_items:
            no_items = self.item_font.render("暂无商品", True, (150, 150, 150))
            screen.blit(no_items, (SCREEN_WIDTH // 2 - no_items.get_width() // 2, 200))
            return
        
        item_start_y = 115
        item_height = 55  # 缩小高度
        item_width = SCREEN_WIDTH - 100
        
        visible_items = self.shop_items[self.scroll_offset:self.scroll_offset + self.max_visible_items]
        
        for i, item in enumerate(visible_items):
            actual_index = self.scroll_offset + i
            item_y = item_start_y + i * item_height
            item_rect = pygame.Rect(50, item_y, item_width, item_height - 5)
            
            # 背景
            if actual_index == self.selected_index:
                bg_color = (80, 100, 140)
            else:
                bg_color = (50, 55, 70)
            
            pygame.draw.rect(screen, bg_color, item_rect, border_radius=8)
            pygame.draw.rect(screen, (100, 100, 120), item_rect, width=1, border_radius=8)
            
            # 先渲染价格/状态（需要知道其宽度来计算文字可用空间）
            if item.can_purchase:
                cost_color = (255, 215, 0)
                cost_text = f"{item.cost}"
            elif item.category == ShopCategory.EQUIPMENT:
                # 装备类显示装备状态
                is_equipped = getattr(item, 'is_equipped', False)
                if is_equipped:
                    cost_color = (100, 255, 100)
                    cost_text = "装备中"
                else:
                    cost_color = (180, 180, 100)
                    cost_text = "装备"
            else:
                cost_color = (100, 180, 100)
                cost_text = "已购买" if item.is_purchased else "已满级"
            
            cost_surface = self.item_font.render(cost_text, True, cost_color)
            cost_width = cost_surface.get_width()
            
            # 计算文字可用宽度（左边距15 + 右边距15 + 价格宽度 + 间隔20）
            text_max_width = item_rect.width - 15 - 15 - cost_width - 20
            
            # 名称
            name_color = (200, 200, 200) if item.can_purchase else (120, 120, 120)
            name_text = item.name
            if item.category == ShopCategory.UPGRADES and item.max_level > 1:
                name_text += f" (Lv.{item.current_level}/{item.max_level})"
            
            # 截断名称以适应宽度
            name_text = self._truncate_text(name_text, self.item_font, text_max_width)
            name_surface = self.item_font.render(name_text, True, name_color)
            screen.blit(name_surface, (item_rect.x + 15, item_rect.y + 5))
            
            # 描述（截断以适应宽度）
            desc_text = self._truncate_text(item.description, self.desc_font, text_max_width)
            desc_surface = self.desc_font.render(desc_text, True, (140, 140, 160))
            screen.blit(desc_surface, (item_rect.x + 15, item_rect.y + 28))
            
            # 渲染价格/状态
            screen.blit(cost_surface, (item_rect.right - cost_width - 15, item_rect.y + 15))
        
        # 滚动指示器
        if len(self.shop_items) > self.max_visible_items:
            if self.scroll_offset > 0:
                arrow_up = self.item_font.render("▲", True, (200, 200, 200))
                screen.blit(arrow_up, (SCREEN_WIDTH // 2 - 10, item_start_y - 20))
            
            if self.scroll_offset + self.max_visible_items < len(self.shop_items):
                arrow_down = self.item_font.render("▼", True, (200, 200, 200))
                screen.blit(arrow_down, (SCREEN_WIDTH // 2 - 10, item_start_y + self.max_visible_items * item_height))
    
    def _render_difficulty_indicator(self, screen: pygame.Surface) -> None:
        """渲染当前难度指示器"""
        # 难度文字
        if self.selected_difficulty == 'easy':
            diff_text = "简单"
            diff_color = (80, 200, 80)  # 绿色
            desc = "敌人较少，无陷阱"
        elif self.selected_difficulty == 'hard':
            diff_text = "困难"
            diff_color = (220, 80, 80)  # 红色
            desc = "敌人更多更快，有尖刺"
        else:  # hardcore
            diff_text = "变态"
            diff_color = (200, 80, 200)  # 紫色
            desc = "复式关卡，新敌人，危险障碍"
        
        # 渲染难度指示（放在左上角，一行显示）
        label_surface = self.desc_font.render("难度:", True, (150, 150, 170))
        diff_surface = self.desc_font.render(diff_text, True, diff_color)
        desc_surface = self.desc_font.render(f"({desc})", True, (120, 120, 140))
        
        screen.blit(label_surface, (20, 22))
        screen.blit(diff_surface, (20 + label_surface.get_width() + 5, 22))
        screen.blit(desc_surface, (20 + label_surface.get_width() + 5 + diff_surface.get_width() + 8, 22))
    
    def _render_hints(self, screen: pygame.Surface) -> None:
        """渲染操作提示"""
        if self.current_category == ShopCategory.EQUIPMENT:
            hints = "↑↓选择 | ←→分类 | Enter购买/装备 | S开始 | ESC返回"
        else:
            hints = "↑↓选择 | ←→分类 | Enter购买 | S开始 | ESC返回"
        hint_surface = self.desc_font.render(hints, True, (100, 100, 130))
        screen.blit(hint_surface, (SCREEN_WIDTH // 2 - hint_surface.get_width() // 2, SCREEN_HEIGHT - 25))
