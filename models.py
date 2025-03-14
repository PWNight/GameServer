from datetime import datetime,timedelta,timezone
import jwt

class User:
    """Класс создания пользователя"""
    def __init__(self,login, password,token=None):
        """Метод Создания пользователя"""
        self.login = login
        self.password = password
        self.token = token

    def generate_token(self,secret_key,expires_in=3600):
        payload = {
            'user_name': self.login,
            'exp': datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        }
        return jwt.encode(payload,secret_key,algorithm='HS256')

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

class DataBase:
    def __init__(self):
        self.users = {}
        self.characters = {}

    def character_add(self,login,name):
        if login in self.users:
            if name in self.characters:
                return False
            else:
                self.characters[name] = Character(login, name)
                return True
        else:
            return False

    def user_add(self,login, password):
        if login in self.users:
            return False
        else:
            self.users[login] = User(login, password)
            return True

    def token(self,login):
        user = self.users[login]
        self.users[login].token = user.generate_token(user.password)
        self.users[login] = user
        return user.token

    def auth(self,login, password):
        return self.users[login].password == password

    def out(self,login):
        user = self.users[login]
        user.token = None
        self.users[login] = user
        return True

    def password_edit(self,login,password_new):
        user = self.users[login]
        if user.token is not None:
            user.password = password_new
            return True
        else:
            return False

    def level_up(self,name):
        character = self.characters[name]
        character.level_up()
        self.characters[name] = character

    def level_down(self, name):
        character = self.characters[name]
        character.level_down()
        self.characters[name] = character

#print(User.__doc__)
# db = DataBase()
# print(db.user_add("test","1234qqwer"))
# print(db.user_add("test","1234qqw234"))
# print(db.users)