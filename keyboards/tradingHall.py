from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton


back = KeyboardButton('🔙 Назад')
buy = KeyboardButton('🛒 Купить монеты')
sell = KeyboardButton('🚚 Продать монеты')
top_up = KeyboardButton('💳 Пополнить счет')
withdraw = KeyboardButton('💸 Вывести деньги со счета')
trading_hall_kb = ReplyKeyboardMarkup(resize_keyboard=True)
trading_hall_kb.row(buy, sell).row(top_up, withdraw).add(back)
