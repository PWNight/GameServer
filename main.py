from flask import Flask,request,jsonify,render_template
import logging
import markdown
from models import DataBase, User, Item

app = Flask(__name__)
db = DataBase()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('main.log'),
        logging.StreamHandler()
    ]
)

# Ф-ия записи логов с указанием айпи
def log_with_ip(message,level=logging.INFO):
    ip_address = request.remote_addr
    log_message = f"{message} [IP: {ip_address}]"
    logging.log(level,log_message)

# Главная страница с контентом из readme.md
@app.route('/')
def home():
    with open('README.md','r',encoding='utf-8')as f:
        content = f.read()
        content_html=markdown.markdown(content)
        return render_template("readme.html",content=content_html)

# POST метод для регистрации аккаунта
@app.route('/reg',methods=['POST'])
def reg():
    data = request.json
    user_login = data.get('login')
    user_password = data.get('password')

    if not user_login or not user_password:
        log_with_ip("Registration attempt without login/password", logging.WARNING)
        return jsonify({ 'error': 'Login or Password required' }), 400
    if db.user_add(user_login, user_password):
        log_with_ip(f"User {user_login} registered")
        return jsonify({ 'message': 'User created' }), 201
    else:
        log_with_ip(f"Registration failed for {user_login}", logging.ERROR)
        return jsonify({ 'error': 'Username exists' }), 400

# POST метод для авторизации
@app.route('/login',methods=['POST'])
def login():
    data = request.json
    user_login = data.get('login')
    user_password = data.get('password')

    if not user_login or not user_password:
        log_with_ip("Registration attempt without login/password", logging.WARNING)
        return jsonify({ 'error': 'Login or Password required' }), 400
    if db.auth(user_login, user_password):
        log_with_ip(f"User {user_login} logged in")
        db.token(user_login)
        return jsonify({ 'token': db.token(user_login) }), 200

# POST метод для выхода из аккаунта
@app.route('/out',methods=['POST'])
def out():
    data = request.json
    user_login = data.get('login')

    if not user_login :
        log_with_ip("Registration attempt without login", logging.WARNING)
        return jsonify({ 'error': 'Login required' }), 400
    if db.out(user_login):
        log_with_ip("User out of system")
        return jsonify({ 'message': 'User out of system' })
    else:
        log_with_ip("User out of system error", logging.ERROR)
        return jsonify({ 'error': 'User out of system Error' })

# POST метод для изменения пароля
@app.route('/password',methods=['POST'])
def password():
    data = request.json
    user_login = data.get('login')
    new_password = data.get('password')

    if not user_login or not new_password:
        log_with_ip("Registration attempt without login", logging.WARNING)
        return jsonify({ 'error': 'Login required' }), 400
    if db.password_edit(user_login, new_password):
        log_with_ip("User edit password")
        return jsonify({ 'message': 'User edit password' })
    else:
        log_with_ip("User edit password error",logging.ERROR)
        return jsonify({'error':'edit password Error'})

# POST метод для создания персонажа
@app.route('/character',methods=['POST'])
def character_add():
    data = request.json
    user_login = data.get('login')
    character_name = data.get('name')

    if not user_login or not character_name:
        log_with_ip("Registration attempt without login/name", logging.WARNING)
        return jsonify({ 'error': 'Login or name required' }), 400
    if db.character_add(user_login, character_name):
        log_with_ip(f"User {user_login} created character {character_name}")
        db.token(user_login)
        return jsonify({ 'message': f'User {user_login} created character {character_name}' })
    else:
        log_with_ip(f"Error when user {user_login} creating character {character_name}", logging.ERROR)
        db.token(user_login)
        return jsonify({ 'error': f'Error when user {user_login} creating character {character_name}' }), 401

# POST метод повышения уровня персонажа
@app.route('level_up',methods=['POST'])
def level_up():
    data = request.json
    character_name = data.get('name')

    if not character_name:
        log_with_ip("Name empty", logging.WARNING)
        return jsonify({ 'error': 'Name empty' }), 400
    if db.level_up(character_name):
        log_with_ip(f"{character_name} level up")
        db.token(login)
        return jsonify({ 'message': f'{character_name} level up' })
    else:
        log_with_ip(f"Error when {character_name} level up", logging.ERROR)
        db.token(login)
        return jsonify({ 'error': f'Error when {character_name} level up' }), 401

# POST метод для понижения уровня персонажа
@app.route('level_down',methods=['POST'])
def level_down():
    data = request.json
    character_name = data.get('name')

    if not character_name:
        log_with_ip("Name empty", logging.WARNING)
        return jsonify({ 'error': 'Name empty' }), 400
    if db.level_down(character_name):
        log_with_ip(f"{character_name} level up")
        db.token(login)
        return jsonify({ 'message': f'{character_name} level down' })
    else:
        log_with_ip(f"Error when {character_name} level down", logging.ERROR)
        db.token(login)
        return jsonify({ 'error': f'Error when {character_name} level down' }), 401


# POST метод для добавления предмета в инвентарь
@app.route('/inventory/add', methods=['POST'])
def add_item_to_inventory():
    data = request.json
    character_name = data.get('character_name')
    item_data = data.get('item', {})

    if not character_name or not item_data:
        log_with_ip("Attempt to add item without character name or item data", logging.WARNING)
        return jsonify({'error': 'Character name and item data required'}), 400

    if character_name not in db.characters:
        log_with_ip(f"Character {character_name} not found", logging.ERROR)
        return jsonify({'error': 'Character not found'}), 404

    item = Item(
        name=item_data.get('name'),
        item_type=item_data.get('type'),
        value=item_data.get('value', 0),
        weight=item_data.get('weight', 0),
        bonus=item_data.get('bonus')
    )

    if db.characters[character_name].inventory.add_item(item):
        log_with_ip(f"Item {item.name} added to {character_name}'s inventory")
        return jsonify({'message': f'Item {item.name} added to {character_name}'}), 200
    else:
        log_with_ip(f"Failed to add item {item.name} to {character_name}'s inventory", logging.ERROR)
        return jsonify({'error': 'Failed to add item (weight limit or duplicate)'}), 400


# POST метод для удаления предмета из инвентаря
@app.route('/inventory/remove', methods=['POST'])
def remove_item_from_inventory():
    data = request.json
    character_name = data.get('character_name')
    item_name = data.get('item_name')

    if not character_name or not item_name:
        log_with_ip("Attempt to remove item without character name or item name", logging.WARNING)
        return jsonify({'error': 'Character name and item name required'}), 400

    if character_name not in db.characters:
        log_with_ip(f"Character {character_name} not found", logging.ERROR)
        return jsonify({'error': 'Character not found'}), 404

    if db.characters[character_name].inventory.remove_item(item_name):
        log_with_ip(f"Item {item_name} removed from {character_name}'s inventory")
        return jsonify({'message': f'Item {item_name} removed from {character_name}'}), 200
    else:
        log_with_ip(f"Item {item_name} not found in {character_name}'s inventory", logging.ERROR)
        return jsonify({'error': 'Item not found'}), 404

if __name__=='__main__':
    logging.info("Auth_server Start")
    app.run(host='0.0.0.0',port=5005,debug=True)