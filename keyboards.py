from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_ID

def main_keyboard(user_id: int = None):
    buttons = [
        [KeyboardButton(text="📦 Собрать заявку")],
        [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="🏆 Рейтинг")],
        [KeyboardButton(text="🛒 Магазин"), KeyboardButton(text="💼 Бизнесы")],
        [KeyboardButton(text="📈 Инвестиции")],
    ]
    
    if user_id == ADMIN_ID:
        buttons.append([KeyboardButton(text="🛠 Админ-панель")])
    
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def shop_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧤 Перчатки — 15.000₽ (+6% скорость)", callback_data="buy_gloves")],
        [InlineKeyboardButton(text="🧥 Тёплая одежда — 25.000₽ (+7% к цене)", callback_data="buy_clothes")],
        [InlineKeyboardButton(text="📱 Планшет — 40.000₽ (+8% к опыту)", callback_data="buy_tablet")],
        [InlineKeyboardButton(text="🖊 Маркер Базовый — 12.000₽ (+5%)", callback_data="buy_marker_basic")],
        [InlineKeyboardButton(text="🖊 Маркер Профи — 35.000₽ (+9%)", callback_data="buy_marker_pro")],
        [InlineKeyboardButton(text="🖊 Маркер Легенда — 80.000₽ (+10%)", callback_data="buy_marker_legend")],
        [InlineKeyboardButton(text="👑 Костюм «Саша Светлый» — 5.000.000₽ (+50%)", callback_data="buy_costume")],
        [InlineKeyboardButton(text="« Назад", callback_data="back_main")],
    ])


def businesses_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏪 Ларёк у дома — 25.000₽ (180₽/час)", callback_data="buy_biz_1")],
        [InlineKeyboardButton(text="🏬 Магазин у дома — 70.000₽ (420₽/час)", callback_data="buy_biz_2")],
        [InlineKeyboardButton(text="📦 Небольшой склад — 180.000₽ (950₽/час)", callback_data="buy_biz_3")],
        [InlineKeyboardButton(text="🏢 Сеть из 3 точек — 450.000₽ (2100₽/час)", callback_data="buy_biz_4")],
        [InlineKeyboardButton(text="🚚 Региональный дистрибьютор — 1.100.000₽ (4800₽/час)", callback_data="buy_biz_5")],
        [InlineKeyboardButton(text="🏭 Крупный логистический центр — 4.500.000₽ (16000₽/час)", callback_data="buy_biz_6")],
        [InlineKeyboardButton(text="« Назад", callback_data="back_main")],
    ])


def investments_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏦 Тинькофф", callback_data="invest_tinkoff")],
        [InlineKeyboardButton(text="🏦 Альфа-Банк", callback_data="invest_alfa")],
        [InlineKeyboardButton(text="🏦 Газпромбанк", callback_data="invest_gazprom")],
        [InlineKeyboardButton(text="🏦 Сбербанк", callback_data="invest_sber")],
        [InlineKeyboardButton(text="🥇 Золото", callback_data="invest_gold")],
        [InlineKeyboardButton(text="🥈 Серебро", callback_data="invest_silver")],
        [InlineKeyboardButton(text="⚪ Платина", callback_data="invest_platinum")],
        [InlineKeyboardButton(text="🔸 Палладий", callback_data="invest_palladium")],
        [InlineKeyboardButton(text="💎 Алмазы", callback_data="invest_diamonds")],
        [InlineKeyboardButton(text="« Назад", callback_data="back_main")],
    ])


def admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Выдать себе деньги", callback_data="admin_give_money")],
        [InlineKeyboardButton(text="« Назад", callback_data="back_main")],
    ])
