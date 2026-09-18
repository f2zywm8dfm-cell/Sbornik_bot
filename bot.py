import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, ADMIN_ID
from database import (
    init_db, get_user, create_user, update_balance,
    get_equipment, buy_equipment, collect_application, get_top_players,
    get_user_rank
)
from keyboards import (
    main_keyboard, shop_keyboard, businesses_keyboard,
    investments_keyboard, admin_keyboard
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


class AdminStates(StatesGroup):
    waiting_for_amount = State()


@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Без ника"
    full_name = message.from_user.full_name or "Игрок"
    
    await create_user(user_id, username, full_name)
    
    text = (
        f"👋 Привет, <b>{full_name}</b>!\n\n"
        f"Ты устроился сборщиком на холодный склад.\n"
        f"Собирай заявки, прокачивайся, покупай бизнесы и становись лучшим.\n\n"
        f"📦 Собирай заявки каждые 2 минуты\n"
        f"📈 Максимум 40 заявок в день\n"
        f"🛒 Покупай экипировку и бизнесы\n"
        f"🏆 Соревнуйся в рейтинге\n\n"
        f"Удачи, сборщик!"
    )
    
    await message.answer(text, reply_markup=main_keyboard(user_id), parse_mode="HTML")


@dp.message(F.text == "📦 Собрать заявку")
async def collect_handler(message: Message):
    result = await collect_application(message.from_user.id)
    
    if not result["success"]:
        await message.answer(result["message"])
        return
    
    text = (
        f"✅ <b>Заявка собрана!</b>\n\n"
        f"💰 Получено: <b>{result['price']:,} ₽</b>\n"
        f"✨ Опыт: +{result['xp']}\n"
        f"📊 Сегодня собрано: {result['applications_today']}/40"
    )
    
    if result.get("new_level"):
        text += f"\n\n🎉 <b>Новый уровень: {result['new_level']}!</b>"
    
    await message.answer(text, parse_mode="HTML")


@dp.message(F.text == "👤 Профиль")
async def profile_handler(message: Message):
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("Сначала нажми /start")
        return
    
    eq = await get_equipment(message.from_user.id)
    rank = await get_user_rank(message.from_user.id)
    
    equipment_list = []
    if eq:
        if eq["gloves"]: equipment_list.append("🧤 Перчатки")
        if eq["clothes"]: equipment_list.append("🧥 Тёплая одежда")
        if eq["tablet"]: equipment_list.append("📱 Планшет")
        if eq["marker_basic"]: equipment_list.append("🖊 Маркер Базовый")
        if eq["marker_pro"]: equipment_list.append("🖊 Маркер Профи")
        if eq["marker_legend"]: equipment_list.append("🖊 Маркер Легенда")
        if eq["costume"]: equipment_list.append("👑 Костюм «Саша Светлый»")
    
    eq_text = ", ".join(equipment_list) if equipment_list else "Нет"
    
    text = (
        f"👤 <b>Профиль</b>\n\n"
        f"Имя: {user['full_name']}\n"
        f"Уровень: <b>{user['level']}</b>\n"
        f"Опыт: {user['xp']}\n"
        f"Баланс: <b>{user['balance']:,} ₽</b>\n"
        f"Собрано заявок всего: {user['total_collected']}\n"
        f"Сегодня: {user['applications_today']}/40\n"
        f"Место в рейтинге: <b>#{rank}</b>\n\n"
        f"🎒 Экипировка: {eq_text}"
    )
    
    await message.answer(text, parse_mode="HTML")


@dp.message(F.text == "🏆 Рейтинг")
async def rating_handler(message: Message):
    top = await get_top_players(10)
    
    if not top:
        await message.answer("Пока никого нет в рейтинге.")
        return
    
    text = "🏆 <b>Топ-10 сборщиков</b>\n\n"
    medals = ["🥇", "🥈", "🥉"]
    
    for i, player in enumerate(top, 1):
        medal = medals[i-1] if i <= 3 else f"{i}."
        name = player['full_name'] or player['username'] or "Игрок"
        text += f"{medal} <b>{name}</b>\n"
        text += f"    💰 {player['balance']:,} ₽ | Ур. {player['level']} | Заявок: {player['total_collected']}\n\n"
    
    rank = await get_user_rank(message.from_user.id)
    user = await get_user(message.from_user.id)
    text += f"————————————\nТвоё место: <b>#{rank}</b> | {user['balance']:,} ₽"
    
    await message.answer(text, parse_mode="HTML")


@dp.message(F.text == "🛒 Магазин")
async def shop_handler(message: Message):
    await message.answer(
        "🛒 <b>Магазин экипировки</b>\n\nВыбери, что хочешь купить:",
        reply_markup=shop_keyboard(),
        parse_mode="HTML"
    )


@dp.message(F.text == "💼 Бизнесы")
async def businesses_handler(message: Message):
    await message.answer(
        "💼 <b>Бизнесы</b>\n\nПокупай бизнесы и получай пассивный доход:",
        reply_markup=businesses_keyboard(),
        parse_mode="HTML"
    )


@dp.message(F.text == "📈 Инвестиции")
async def investments_handler(message: Message):
    await message.answer(
        "📈 <b>Инвестиции</b>\n\nВкладывай от 1000 ₽ и получай дивиденды.\nВыбери куда инвестировать:",
        reply_markup=investments_keyboard(),
        parse_mode="HTML"
    )


@dp.message(F.text == "🛠 Админ-панель")
async def admin_handler(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔️ Нет доступа")
        return
    
    await message.answer(
        "🛠 <b>Админ-панель</b>\n\nВыбери действие:",
        reply_markup=admin_keyboard(),
        parse_mode="HTML"
    )


@dp.callback_query(F.data.startswith("buy_"))
async def buy_callback(callback: CallbackQuery):
    data = callback.data
    user_id = callback.from_user.id
    
    prices = {
        "buy_gloves": ("gloves", 15000, "Перчатки"),
        "buy_clothes": ("clothes", 25000, "Тёплая одежда"),
        "buy_tablet": ("tablet", 40000, "Планшет"),
        "buy_marker_basic": ("marker_basic", 12000, "Маркер Базовый"),
        "buy_marker_pro": ("marker_pro", 35000, "Маркер Профи"),
        "buy_marker_legend": ("marker_legend", 80000, "Маркер Легенда"),
        "buy_costume": ("costume", 5000000, "Костюм «Саша Светлый»"),
    }
    
    if data in prices:
        item, price, name = prices[data]
        eq = await get_equipment(user_id)
        
        if eq and eq.get(item):
            await callback.answer("У тебя уже есть этот предмет!", show_alert=True)
            return
        
        success = await buy_equipment(user_id, item, price)
        if success:
            await callback.message.answer(f"✅ Ты купил: <b>{name}</b>!", parse_mode="HTML")
        else:
            await callback.answer("Недостаточно денег!", show_alert=True)
    
    await callback.answer()


@dp.callback_query(F.data == "admin_give_money")
async def admin_give_money(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа", show_alert=True)
        return
    
    await callback.message.answer("Введи сумму, которую хочешь себе выдать:")
    await state.set_state(AdminStates.waiting_for_amount)
    await callback.answer()


@dp.message(AdminStates.waiting_for_amount)
async def process_admin_amount(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        amount = int(message.text.replace(" ", "").replace(",", ""))
        await update_balance(message.from_user.id, amount)
        user = await get_user(message.from_user.id)
        await message.answer(
            f"✅ Тебе начислено <b>{amount:,} ₽</b>\n"
            f"Текущий баланс: <b>{user['balance']:,} ₽</b>",
            parse_mode="HTML"
        )
    except ValueError:
        await message.answer("Введи число, например: 100000")
        return
    
    await state.clear()


@dp.callback_query(F.data == "back_main")
async def back_main(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer()


async def main():
    await init_db()
    logger.info("База данных инициализирована")
    logger.info("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
