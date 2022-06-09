import sqlite3 as sq
from datetime import datetime


class BotDB:

    def __init__(self, db_file):
        # Соединение с БД
        self.conn = sq.connect(db_file)
        self.cursor = self.conn.cursor()
        self.upgrade_names = ['first', 'second', 'third', 'fourth', 'fifth']

    def user_exists(self, user_id):
        # Проверка на наличие пользователя в БД
        result = self.cursor.execute("SELECT user_id FROM user WHERE user_id = ?", [user_id])
        return bool(len(result.fetchall()))

    def is_selling(self, user_id):
        result = self.cursor.execute("SELECT user_id FROM market WHERE user_id = ?", [user_id])
        return bool(len(result.fetchall()))

    def get_purse(self, user_id):
        return self.cursor.execute("SELECT purse FROM user WHERE user_id = ?;", [user_id]).fetchall()[0][0]

    def create_sell(self, user_id, amount, price):
        self.cursor.execute("INSERT INTO market (user_id, amount, price) VALUES(?, ?, ?);", [user_id, amount, price])
        self.cursor.execute(f"UPDATE user SET purse = purse - {amount} WHERE user_id = ?", [user_id])
        self.conn.commit()

    def delete_sell(self, user_id):
        result = self.cursor.execute("SELECT amount, price FROM market WHERE user_id = ?", [user_id]).fetchall()[0]
        amount = result[0]
        self.cursor.execute(f"UPDATE user SET purse = purse + {amount} WHERE user_id = ?", [user_id])
        self.cursor.execute("DELETE FROM market WHERE user_id = ?;", [user_id])
        self.conn.commit()

    def get_sell(self, user_id):
        result = self.cursor.execute("SELECT amount, price FROM market WHERE user_id = ?", [user_id])
        return result.fetchall()[0]

    def add_user(self, user_id, username, inviter):
        # Добавление пользователя
        self.cursor.execute("INSERT INTO user (user_id, username, inviter) VALUES(?, ?, ?);", [user_id, username, inviter])
        self.conn.commit()

    def get_user(self, user_id):
        # Получить данные о пользователе
        result = self.cursor.execute("SELECT * FROM user WHERE (user_id = ?);", [user_id])
        return result.fetchall()[0]

    def click(self, user_id, purse, excavation, clicks):
        # Обработка клика
        self.cursor.execute("UPDATE user SET purse = purse + excavation, clicks = clicks + 1 "
                            "WHERE user_id = ?;", [user_id])
        self.conn.commit()
        return purse + excavation

    def buy_upgrade(self, user_id, excavation, excavation_upgrade, purse, upgrade_number, upgrade_price):
        # Покупка улучшения
        excavation += excavation_upgrade
        purse -= upgrade_price
        self.cursor.execute(f"UPDATE user SET purse = ?, excavation = ?, "
                            f"{self.upgrade_names[upgrade_number]}UpgradeAmount = {self.upgrade_names[upgrade_number]}UpgradeAmount + 1 "
                            f"WHERE user_id = ?;", [purse, excavation, user_id])
        self.conn.commit()
        return purse

    def buy_p_upgrade(self, user_id, passive_income, income_upgrade, purse, upgrade_number, upgrade_price):
        self.update_warehouse(user_id=user_id)
        passive_income += income_upgrade
        purse -= upgrade_price
        self.cursor.execute(f"UPDATE user SET purse = ?, passiveIncome = ?, "
                            f"{self.upgrade_names[upgrade_number]}PUpgradeAmount = {self.upgrade_names[upgrade_number]}PUpgradeAmount + 1 "
                            f"WHERE user_id = ?;", [purse, passive_income, user_id])
        self.conn.commit()
        return purse

    def collect_warehouse(self, user_id):
        # Сбор накопленного на складе
        self.cursor.execute(f"UPDATE user SET purse = purse + warehouse + ({int(datetime.now().timestamp())} - "
                            f"lastWarehouseUpdate) * passiveIncome, warehouse = 0, "
                            f"lastWarehouseUpdate = {int(datetime.now().timestamp())} WHERE user_id = ?;", [user_id])
        self.conn.commit()

    def update_warehouse(self, user_id):
        self.cursor.execute(f"UPDATE user SET warehouse = warehouse + "
                            f"({int(datetime.now().timestamp())} - lastWarehouseUpdate) * passiveIncome, "
                            f"lastWarehouseUpdate = {int(datetime.now().timestamp())} WHERE user_id = ?", [user_id])
        self.conn.commit()
        return self.cursor.execute("SELECT warehouse FROM user WHERE (user_id = ?);", [user_id]).fetchall()[0][0]

    def deposit(self, user_id, money):
        self.payment_log(user_id=user_id, summ=money)
        self.cursor.execute("UPDATE user SET money = money + ? WHERE user_id = ?", [money, user_id])
        self.conn.commit()

    def payment_log(self, user_id, summ, operation="ПОПОЛНЕНИЕ"):
        self.cursor.execute("INSERT INTO operations (user_id, operation, sum) VALUES(?, ?, ?)",
                            [user_id, operation, summ])
        self.conn.commit()
