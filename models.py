from datetime import datetime, timedelta, timezone
import jwt

class DataBase:
    def __init__(self):
        self.users = {}
        self.characters = {}
        self.trade_system = Trade(self)  # Инициализируем Trade внутри DataBase

    """Добавление персонажа"""
    def character_add(self, login, name):
        if login in self.users:
            if name in self.characters:
                return False
            else:
                self.characters[name] = Character(login, name)
                return True
        return False

    """Добавление пользователя"""
    def user_add(self, login, password):
        if login in self.users:
            return False
        self.users[login] = User(login, password)
        return True

    """Получение токена пользователя"""
    def token(self, login):
        if login in self.users:
            user = self.users[login]
            user.token = user.generate_token(user.password)
            self.users[login] = user
            return user.token
        return None

    """Проверка пароля по логину"""
    def auth(self, login, password):
        return login in self.users and self.users[login].password == password

    """Выход из аккаунта"""
    def out(self, login):
        if login in self.users:
            user = self.users[login]
            user.token = None
            self.users[login] = user
            return True
        return False

    """Редактирование пароля"""
    def password_edit(self, login, password_new):
        if login in self.users:
            user = self.users[login]
            if user.token is not None:
                user.password = password_new
                return True
        return False

    """Повышение уровня"""
    def level_up(self, name):
        if name in self.characters:
            character = self.characters[name]
            character.level_up()
            self.characters[name] = character
            return True
        return False

    """Понижение уровня"""
    def level_down(self, name):
        if name in self.characters:
            character = self.characters[name]
            character.level_down()
            self.characters[name] = character
            return True
        return False

class User:
    def __init__(self, login, password, token=None):
        self.login = login
        self.password = password
        self.token = token

    """Генерация токена"""
    def generate_token(self, secret_key, expires_in=3600):
        payload = {
            'user_name': self.login,
            'exp': datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        }
        return jwt.encode(payload, secret_key, algorithm='HS256')

class Character:
    def __init__(
        self, login, name,
        heals=10, streng=1, intel=1,
        dexterity=1, spirit=1, endurance=1,
        head=None, armour=None, shoulders=None,
        gloves=None, legs=None, boots=None,
        exp=0, level=1
    ):
        self.account = login
        self.name = name
        self.heals = heals
        self.char = {
            'strength': streng,
            'intelligence': intel,
            'dexterity': dexterity,
            'spirit': spirit,
            'endurance': endurance
        }
        self.equipment = {
            'head': head,
            'armour': armour,
            'shoulders': shoulders,
            'gloves': gloves,
            'legs': legs,
            'boots': boots
        }
        self.inventory = Inventory()
        self.exp = exp
        self.level = level

    def level_up(self):
        self.level += 1
        self.exp = 0

    def level_down(self):
        self.level -= 1
        self.exp = 100

class Item:
    def __init__(self, name, item_type, value, weight, bonus=None):
        self.name = name
        self.type = item_type
        self.value = value
        self.weight = weight
        self.bonus = bonus

class Inventory:
    def __init__(self):
        self.items = {}
        self.max_weight = 100
        self.current_weight = 0

    """Добавление предмета в инвентарь"""
    def add_item(self, item):
        if self.current_weight + item.weight <= self.max_weight:
            if item.name in self.items:
                return False
            self.items[item.name] = item
            self.current_weight += item.weight
            return True
        return False

    """Удаление предмета из инвентаря"""
    def remove_item(self, item_name):
        if item_name in self.items:
            self.current_weight -= self.items[item_name].weight
            del self.items[item_name]
            return True
        return False

    """Подсчет общей стоимости предметов"""
    def get_total_value(self):
        return sum(item.value for item in self.items.values())

class Trade:
    def __init__(self, db: DataBase):
        self.db = db
        self.offers = {}

    """Создание предложения сделки"""
    def create_offer(self, initiator_name, target_name, items_offered, items_requested):
        if initiator_name not in self.db.characters or target_name not in self.db.characters:
            return False

        initiator = self.db.characters[initiator_name]
        for item_name in items_offered:
            if item_name not in initiator.inventory.items:
                return False

        self.offers[initiator_name] = {
            'target': target_name,
            'offered': items_offered,
            'requested': items_requested,
            'status': 'pending'
        }
        return True

    """Принятие сделки"""
    def accept_trade(self, target_name, initiator_name):
        if initiator_name not in self.offers or self.offers[initiator_name]['target'] != target_name:
            return False

        trade = self.offers[initiator_name]
        if trade['status'] != 'pending':
            return False

        initiator = self.db.characters[initiator_name]
        target = self.db.characters[target_name]

        # Проверка наличия запрашиваемых предметов у цели
        for item_name in trade['requested']:
            if item_name not in target.inventory.items:
                return False

        # Обмен предметами
        for item_name in trade['offered']:
            item = initiator.inventory.items[item_name]
            initiator.inventory.remove_item(item_name)
            target.inventory.add_item(item)

        for item_name in trade['requested']:
            item = target.inventory.items[item_name]
            target.inventory.remove_item(item_name)
            initiator.inventory.add_item(item)

        trade['status'] = 'completed'
        return True

    """Отклонение сделки"""
    def decline_trade(self, target_name, initiator_name):
        if initiator_name in self.offers and self.offers[initiator_name]['target'] == target_name:
            self.offers[initiator_name]['status'] = 'declined'
            return True
        return False

    """Отмена сделки инициатором"""
    def cancel_trade(self, initiator_name):
        if initiator_name in self.offers:
            del self.offers[initiator_name]
            return True
        return False