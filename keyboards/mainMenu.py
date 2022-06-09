from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton


button_click = KeyboardButton('🎮 Клик')
warehouse = KeyboardButton('📦 Склад')
active_upgrades = KeyboardButton('⛏ Активные улучшения')
passive_upgrades = KeyboardButton('💤 Пассивные улучшения')
profile = KeyboardButton('👤 Профиль')
shop = KeyboardButton('🏛 Торговая площадка')

main_menu_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu_kb.add(button_click).add(warehouse).row(active_upgrades, passive_upgrades).row(profile, shop)

cancel = KeyboardButton('Отмена')

cancel_kb = ReplyKeyboardMarkup(resize_keyboard=True)
cancel_kb.add(cancel)

nobody_invited = KeyboardButton('Меня никто не приглашал')

invite_kb = ReplyKeyboardMarkup(resize_keyboard=True)
invite_kb.add(nobody_invited)
