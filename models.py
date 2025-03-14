from datetime import datetime,timedelta,timezone
import jwt

class User:
    def __init__(self,login, password,token=None):
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
    """Класс персонажа"""
    def __init__(
        self,login,name,
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
            'strength':streng, # Сила
            'intelligence':intel, # Интеллект
            'dexterity':dexterity, # Ловкость
            'spirit':spirit, # Дух
            'endurance':endurance # Выносливость
        }
        self.equipment = {
            'head': head, # Шлем
            'armour': armour, # Тело
            'shoulders': shoulders, # Наплечники
            'gloves': gloves, # Перчатки
            'legs': legs, # Поножи
            'boots': boots # Сапоги
        }
        self.exp = exp
        self.level = level

    def level_up(self):
        self.level += 1
        self.exp = 0

    def level_down(self):
        self.level -= 1
        self.exp = 100

class Item:
    """Класс предмета"""
    def __init__(
        self, name, item_type,
        value, weight, bonus = None
    ):
        self.name = name # название
        self.type = item_type # тип
        self.value = value # стоимость
        self.weight = weight # вес
        self.bonus = bonus # эффект/бонус от предмета

class Inventory:
    def __init__(
        self
    ):
        self.items = {} # объект со всеми предметами
        self.max_weight = 100 # максимальный вес инвентаря
        self.current_weight = 0 # текущий вес инвентаря

    """Добавление предмета в инвентарь"""
    def add_item(self, item):
        if self.current_weight + item.weight <= self.max_weight:
            if item.name in self.items:
                return False  # предмет с таким именем уже есть
            self.items[item.name] = item
            self.current_weight += item.weight
            return True
        return False  # превышен лимит веса

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

class DataBase:
    def __init__(self):
        self.users = {}
        self.characters = {}

    """Добавление персонажа"""
    def character_add(self,login,name):
        if login in self.users:
            if name in self.characters:
                return False
            else:
                self.characters[name] = Character(login, name)
                return True
        else:
            return False

    """Добавление пользователя"""
    def user_add(self,login, password):
        if login in self.users:
            return False
        else:
            self.users[login] = User(login, password)
            return True

    """Получение токена пользователя"""
    def token(self,login):
        user = self.users[login]
        self.users[login].token = user.generate_token(user.password)
        self.users[login] = user
        return user.token

    """Проверка пароля по логину"""
    def auth(self,login, password):
        return self.users[login].password == password

    """Выход из аккаунта"""
    def out(self,login):
        user = self.users[login]
        user.token = None
        self.users[login] = user
        return True

    """Редактирование пароля"""
    def password_edit(self,login,password_new):
        user = self.users[login]
        if user.token is not None:
            user.password = password_new
            return True
        else:
            return False

    """Повышение уровня"""
    def level_up(self,name):
        character = self.characters[name]
        character.level_up()
        self.characters[name] = character

    """Понижение уровня"""
    def level_down(self, name):
        character = self.characters[name]
        character.level_down()
        self.characters[name] = character

#print(User.__doc__)
# db = DataBase()
# print(db.user_add("test","1234qqwer"))
# print(db.user_add("test","1234qqw234"))
# print(db.users)