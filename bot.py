from config import TOKEN, YMTOKEN
from db import BotDB

from aiogram.utils.markdown import escape_md
from keyboards.mainMenu import main_menu_kb, cancel_kb, invite_kb
from keyboards.tradingHall import trading_hall_kb
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
boost = [0.0001, 0.0005, 0.004, 0.01, 0.04]
basic_prices = [0.015, 0.1, 5, 30, 100]
basic_p_prices = [0.15, 1, 50, 300, 1000]
deposit = [150, 300, 500, 1000]
BotDB = BotDB('database.db')

WEBHOOK_HOST = 'localhost'
WEBHOOK_PATH = ""


class SellCoins(StatesGroup):
    amount = State()
    price = State()


class Registration(StatesGroup):
    username = State()
    inviter = State()


def is_int(a):
    try:
        return type(int(a)) == int
    except Exception:
        return False


@dp.message_handler(commands=['start'], state=None)
async def start(message: types.message):
    user_id = message.from_user.id
    if not BotDB.user_exists(user_id):
        await message.answer('Добро пожаловать! Введите имя пользователя перед тем, как начать пользоваться ботом')
        await Registration.username.set()
    else:
        await message.answer('Добро пожаловать!', reply_markup=main_menu_kb)


@dp.message_handler(state=Registration.username)
async def set_username(message: types.message, state: FSMContext):
    if len(message.text) > 20:
        await message.answer("🛑 Длина имени должная быть меньше 20 символов!")
    else:
        await Registration.next()
        async with state.proxy() as data:
            data['username'] = str(message.text)
        await message.answer("Введите ID пользователя, пригласившего вас", reply_markup=invite_kb)


@dp.message_handler(lambda m: m.text == 'Меня никто не приглашал', state=Registration.inviter)
async def set_me(message: types.message, state: FSMContext):
    async with state.proxy() as data:
        data['inviter'] = '566949209'
        BotDB.add_user(message.from_user.id, data['username'], data['inviter'])
    await message.answer("✅ Регистрация прошла успешно! Приятной игры!", reply_markup=main_menu_kb)
    await state.finish()


@dp.message_handler(state=Registration.inviter)
async def set_inviter(message: types.message, state: FSMContext):
    if not BotDB.user_exists(message.text):
        await message.answer("Пользователя с таким ID не существует")
    else:
        async with state.proxy() as data:
            data['inviter'] = message.text
            BotDB.add_user(message.from_user.id, data['username'], data['inviter'])
        await message.answer("✅ Регистрация прошла успешно! Приятной игры!", reply_markup=main_menu_kb)
        await state.finish()


@dp.message_handler(state=None)
async def handler(message: types.message):
    if message.chat.type == 'private':
        user_data = BotDB.get_user(message.from_user.id)
        user_id = user_data[0]
        username = user_data[1]
        purse = user_data[2]
        excavation = user_data[3]
        passive_income = user_data[4]
        clicks = user_data[6]
        last_c = user_data[7]
        upgrades = [user_data[8], user_data[9], user_data[10], user_data[11], user_data[12]]
        p_upgrades = [user_data[13], user_data[14], user_data[15], user_data[16], user_data[17]]
        warehouse = user_data[18]
        money = user_data[19]
        text = message.text.lower()

        if text == '🎮 клик':
            print(user_id, 'click')
            purse = BotDB.click(user_id=user_id, purse=purse, excavation=excavation, clicks=clicks)
            await message.answer(f'Выполнен клик\nБаланс: {round(purse, 4)}', reply_markup=main_menu_kb)

        elif text == '👤 профиль':
            print(user_id, 'profile')
            text = f'*📌 Профиль пользователя {escape_md(username)}*\n' \
                   f'\n' \
                   f'👤 ID пользователя: ||{user_id}|| \n\n' \
                   f'🎮 Кликов сделано: *{clicks}*\n\n' \
                   f'⛏ Добыча с клика: *{escape_md(str(round(excavation, 4)))}*\n\n' \
                   f'💤 Пассивная добыча: *{escape_md(str(round(passive_income, 4)))}*\n\n' \
                   f'💰 Всего монет: *{escape_md(str(round(purse, 4)))}*\n\n' \
                   f'💵 Денег на счету: *{escape_md(str(round(money, 4)))}₽*'
            await message.answer(text, parse_mode='Markdownv2')

        elif text == '⛏ активные улучшения':
            for i in range(5):
                await bot.send_message(message.chat.id, f"⬆ *Улучшение {i + 1}*\n\n"
                                                        f"Повышает добычу на *{boost[i]}*\n"
                                                        f"Кол-во: *{upgrades[i]}*\n"
                                                        f"Цена: *{round(basic_prices[i] * (1.2 ** upgrades[i]), 4)}*",
                                       reply_markup=InlineKeyboardMarkup().add(
                                           InlineKeyboardButton('Купить', callback_data=i)),
                                       parse_mode='Markdown'
                                       )

        elif text == '💤 пассивные улучшения':
            for i in range(5):
                await bot.send_message(message.chat.id, f"⬆ *Пассивное улучшение {i + 1}*\n\n"
                                                        f"Повышает пассивную добычу на *{boost[i]} монет/сек*\n"
                                                        f"Кол-во: *{p_upgrades[i]}*\n"
                                                        f"Цена: *{round(basic_p_prices[i] * (1.2 ** p_upgrades[i]), 4)}*",
                                       reply_markup=InlineKeyboardMarkup().add(
                                           InlineKeyboardButton('Купить', callback_data=i + 5)),
                                       parse_mode='Markdown'
                                       )

        elif text == '📦 склад':
            warehouse = BotDB.update_warehouse(user_id)
            await message.answer(f"Здесь хранятся монеты, добытые пассивными улучшениями.\n\n"
                                 f"Сейчас складе имеется *{round(warehouse, 4)}* монет",
                                 reply_markup=InlineKeyboardMarkup().add(
                                     InlineKeyboardButton('Забрать', callback_data=-1)),
                                 parse_mode='Markdown')

        elif text == '🏛 торговая площадка':
            await message.answer("*Добро пожаловать на торговую площадку!*\n\n"
                                 "Здесь вы можете продать/купить монеты за настоящие деньги.",
                                 reply_markup=trading_hall_kb, parse_mode='Markdown')

        elif text == '🔙 назад':
            await message.answer("🔙 Назад", reply_markup=main_menu_kb)

        elif text == '💳 пополнить счет':
            deposit_kb = InlineKeyboardMarkup()
            for i in deposit:
                deposit_kb = deposit_kb.add(InlineKeyboardButton(f'{i}₽', callback_data=i))
            await message.answer("Выберите необходимую сумму для пополнения", reply_markup=deposit_kb)

        elif text == '🚚 продать монеты':
            is_selling = BotDB.is_selling(user_id=user_id)
            if not is_selling:
                await message.answer("На данный момент вы не продаете монет", reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton("➕ Создать лот", callback_data="sell_coins")
                ))
            else:
                sell_data = BotDB.get_sell(message.from_user.id)
                amount = sell_data[0]
                price = sell_data[1]
                await message.answer(f"*Ваш лот*\n"
                                     f"Кол-во монет: *{round(amount, 4)}*\n"
                                     f"Цена за монету: *{round(price, 4)}*\n"
                                     f"Цена за все: *{round(amount * price, 4)}*\n",
                                     reply_markup=InlineKeyboardMarkup().add(
                                         InlineKeyboardButton("➖ Удалить лот", callback_data="delete_sell")),
                                     parse_mode='Markdown'
                                     )

        else:
            await message.answer("🛑 Неизвестная команда", reply_markup=main_menu_kb)


@dp.callback_query_handler(lambda x: x.data == 'sell_coins', state=None)
async def sell_coins(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    await SellCoins.amount.set()
    await bot.send_message(callback_query.from_user.id, "Введите кол-во монет, которое хотите продать (минимум 1):",
                           reply_markup=cancel_kb)


@dp.callback_query_handler(lambda x: x.data == 'delete_sell', state=None)
async def delete_sell(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    BotDB.delete_sell(callback_query.from_user.id)


@dp.message_handler(lambda m: m.text == 'Отмена', state=SellCoins)
async def cancel(message: types.message, state: FSMContext):
    await state.finish()
    await message.answer("Отмена", reply_markup=trading_hall_kb)


@dp.message_handler(state=SellCoins.amount)
async def set_amount(message: types.message, state: FSMContext):
    try:
        if float(message.text) <= BotDB.get_purse(message.from_user.id):
            if float(message.text) > 1:
                async with state.proxy() as data:
                    data['amount'] = float(message.text)
                    await SellCoins.next()
                    await message.answer("Введите цену за 1 монету", reply_markup=cancel_kb)
            else:
                await message.answer("🛑 Минимальная сумма для продажи - 1 монета")
        else:
            await message.answer("🛑 Недостаточно средств")
    except Exception:
        await message.answer("🛑 Неправильный ввод")


@dp.message_handler(state=SellCoins.price)
async def set_price(message: types.message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['price'] = float(message.text)
        async with state.proxy() as data:
            print(data)
            BotDB.create_sell(message.from_user.id, data['amount'], data['price'])
        await state.finish()
        await message.answer("✅ Лот был успешно создан!", reply_markup=trading_hall_kb)
    except Exception:
        await message.answer("🛑 Неправильный ввод 🛑")


@dp.callback_query_handler(lambda x: is_int(x.data) and int(x.data) == -1, state=None)
async def collect_warehouse(callback_query: types.CallbackQuery):
    BotDB.update_warehouse(user_id=BotDB.get_user(callback_query.from_user.id)[0])
    user_data = BotDB.get_user(callback_query.from_user.id)
    user_id = user_data[0]
    purse = user_data[2]
    warehouse = user_data[18]
    BotDB.collect_warehouse(user_id=user_id)
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    await bot.send_message(callback_query.from_user.id, f"✅ Успешно собрано содержимое склада\n \n"
                                                        f"💰 Баланс: {round(purse + warehouse, 4)}")


@dp.callback_query_handler(lambda x: is_int(x.data) and 0 <= int(x.data) <= 4, state=None)
async def buy_active_upgrade(callback_query: types.CallbackQuery):
    user_data = BotDB.get_user(callback_query.from_user.id)
    user_id = user_data[0]
    excavation = user_data[3]
    upgrades = [user_data[8], user_data[9], user_data[10], user_data[11], user_data[12]]
    purse = user_data[2]
    i = int(callback_query.data)
    price = basic_prices[i] * (1.2 ** upgrades[i])
    if purse >= price:

        text = f"⬆ *Улучшение {i + 1}*\n\n" \
               f"Повышает добычу на *{boost[i]}*\n" \
               f"Кол-во: *{upgrades[i] + 1}*\n" \
               f"Цена: *{round(basic_prices[i] * (1.2 ** (upgrades[i] + 1)), 4)}*"

        chat_id = callback_query.message.chat.id
        message_id = callback_query.message.message_id
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, parse_mode='Markdown',
                                    reply_markup=InlineKeyboardMarkup().add(
                                        InlineKeyboardButton('Купить', callback_data=i)),
                                    )
        purse = BotDB.buy_upgrade(user_id=user_id, excavation=excavation, excavation_upgrade=boost[i], purse=purse,
                                  upgrade_number=i,
                                  upgrade_price=price)
        await bot.send_message(callback_query.from_user.id, f'✅ *Куплено улучшение {int(callback_query.data) + 1}*\n\n'
                                                            f'💰 Баланс: {round(purse, 4)}',
                               parse_mode='Markdown')
    else:
        await bot.send_message(callback_query.from_user.id, f'❌ Недостаточно средств')


@dp.callback_query_handler(lambda x: is_int(x.data) and 5 <= int(x.data) <= 9)
async def buy_passive_upgrade(callback_query: types.CallbackQuery):
    user_data = BotDB.get_user(callback_query.from_user.id)
    user_id = user_data[0]
    passive_income = user_data[4]
    p_upgrades = [user_data[13], user_data[14], user_data[15], user_data[16], user_data[17]]
    purse = user_data[2]
    i = int(callback_query.data) - 5
    price = basic_p_prices[i] * (1.2 ** p_upgrades[i])
    if purse >= price:

        text = f"⬆ *Пассивное Улучшение {i}*\n\n" \
               f"Повышает пассивную добычу на *{boost[i]}*\n" \
               f"Кол-во: *{p_upgrades[i] + 1}*\n" \
               f"Цена: *{round(basic_p_prices[i] * (1.2 ** (p_upgrades[i] + 1)), 4)}*"

        chat_id = callback_query.message.chat.id
        message_id = callback_query.message.message_id
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, parse_mode='Markdown',
                                    reply_markup=InlineKeyboardMarkup().add(
                                        InlineKeyboardButton('Купить', callback_data=i + 5)),
                                    )
        purse = BotDB.buy_p_upgrade(user_id=user_id, passive_income=passive_income, income_upgrade=boost[i],
                                    purse=purse,
                                    upgrade_number=i,
                                    upgrade_price=price)
        await bot.send_message(callback_query.from_user.id,
                               f'✅ *Куплено пассивное улучшение {int(callback_query.data) - 4}*\n\n'
                               f'💰 Баланс: {round(purse, 4)}',
                               parse_mode='Markdown')
    else:
        await bot.send_message(callback_query.from_user.id, f'❌ Недостаточно средств')


@dp.callback_query_handler(lambda x: is_int(x.data) and x.data in deposit)
async def deposit_money(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    await bot.send_invoice(chat_id=callback_query.from_user.id,
                           title="Пополнение счета FunCoin",
                           description=str(callback_query.from_user.id),
                           payload=str(callback_query.data),
                           provider_token=YMTOKEN,
                           currency="RUB",
                           start_parameter="test",
                           prices=[{"label": "Руб", "amount": int(callback_query.data) * 110}]
                           )


@dp.pre_checkout_query_handler()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=types.ContentTypes.SUCCESSFUL_PAYMENT)
async def process_pay(message: types.Message):
    BotDB.deposit(user_id=message.from_user.id, money=message.successful_payment.invoice_payload)
    await message.answer(f"Вы успешно пополнили счет на {message.successful_payment.invoice_payload}₽")


executor.start_polling(dp, skip_updates=True)

if __name__ == '__main__':
    executor.start_webhook(dp)
