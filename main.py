from flask import Flask, request, jsonify, render_template
import logging
import markdown
from flasgger import Swagger
from models import DataBase, Item

app = Flask(__name__)
db = DataBase()

swagger_config = {
    "openapi": "3.0.3",
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api",
    "headers": []
}
swagger = Swagger(app, config=swagger_config, template_file='static/swagger.yaml')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('main.log'),
        logging.StreamHandler()
    ]
)

# Функция записи логов с указанием IP
def log_with_ip(message, level=logging.INFO):
    ip_address = request.remote_addr
    log_message = f"{message} [IP: {ip_address}]"
    logging.log(level, log_message)

# Главная страница с контентом из README.md
@app.route('/')
def home():
    with open('README.md', 'r', encoding='utf-8') as f:
        content = f.read()
        content_html = markdown.markdown(content)
    return render_template("readme.html", content=content_html)

# POST метод для регистрации аккаунта
@app.route('/reg', methods=['POST'])
def reg():
    data = request.json
    user_login = data.get('login')
    user_password = data.get('password')

    if not user_login or not user_password:
        log_with_ip("Registration attempt without login/password", logging.WARNING)
        return jsonify({'error': 'Login or Password required'}), 400

    if db.user_add(user_login, user_password):
        log_with_ip(f"User {user_login} registered")
        return jsonify({'message': 'User created'}), 201
    else:
        log_with_ip(f"Registration failed for {user_login}", logging.ERROR)
        return jsonify({'error': 'Username exists'}), 400

# POST метод для авторизации
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user_login = data.get('login')
    user_password = data.get('password')

    if not user_login or not user_password:
        log_with_ip("Login attempt without login/password", logging.WARNING)
        return jsonify({'error': 'Login or Password required'}), 400

    if db.auth(user_login, user_password):
        token = db.token(user_login)
        log_with_ip(f"User {user_login} logged in")
        return jsonify({'token': token}), 200
    else:
        log_with_ip(f"Login failed for {user_login}", logging.ERROR)
        return jsonify({'error': 'Invalid credentials'}), 401

# POST метод для выхода из аккаунта
@app.route('/out', methods=['POST'])
def out():
    data = request.json
    user_login = data.get('login')

    if not user_login:
        log_with_ip("Logout attempt without login", logging.WARNING)
        return jsonify({'error': 'Login required'}), 400

    if db.out(user_login):
        log_with_ip(f"User {user_login} logged out")
        return jsonify({'message': 'User out of system'}), 200
    else:
        log_with_ip(f"Logout error for {user_login}", logging.ERROR)
        return jsonify({'error': 'User logout error'}), 500

# POST метод для изменения пароля
@app.route('/password', methods=['POST'])
def password():
    data = request.json
    user_login = data.get('login')
    new_password = data.get('password')

    if not user_login or not new_password:
        log_with_ip("Password change attempt without login/password", logging.WARNING)
        return jsonify({'error': 'Login and new password required'}), 400

    if db.password_edit(user_login, new_password):
        log_with_ip(f"User {user_login} changed password")
        return jsonify({'message': 'Password updated'}), 200
    else:
        log_with_ip(f"Password change error for {user_login}", logging.ERROR)
        return jsonify({'error': 'Password change error (not logged in?)'}), 401

# POST метод для создания персонажа
@app.route('/character', methods=['POST'])
def character_add():
    data = request.json
    user_login = data.get('login')
    character_name = data.get('name')

    if not user_login or not character_name:
        log_with_ip("Character creation attempt without login/name", logging.WARNING)
        return jsonify({'error': 'Login or name required'}), 400

    if db.character_add(user_login, character_name):
        log_with_ip(f"User {user_login} created character {character_name}")
        return jsonify({'message': f'User {user_login} created character {character_name}'}), 201
    else:
        log_with_ip(f"Error when user {user_login} creating character {character_name}", logging.ERROR)
        return jsonify({'error': f'Error creating character {character_name}'}), 400

# POST метод повышения уровня персонажа
@app.route('/level_up', methods=['POST'])
def level_up():
    data = request.json
    character_name = data.get('name')

    if not character_name:
        log_with_ip("Level up attempt without name", logging.WARNING)
        return jsonify({'error': 'Character name required'}), 400

    if character_name in db.characters and db.level_up(character_name):
        log_with_ip(f"{character_name} leveled up")
        return jsonify({'message': f'{character_name} leveled up'}), 200
    else:
        log_with_ip(f"Error when {character_name} leveling up", logging.ERROR)
        return jsonify({'error': f'Error leveling up {character_name}'}), 404

# POST метод для понижения уровня персонажа
@app.route('/level_down', methods=['POST'])
def level_down():
    data = request.json
    character_name = data.get('name')

    if not character_name:
        log_with_ip("Level down attempt without name", logging.WARNING)
        return jsonify({'error': 'Character name required'}), 400

    if character_name in db.characters and db.level_down(character_name):
        log_with_ip(f"{character_name} leveled down")
        return jsonify({'message': f'{character_name} leveled down'}), 200
    else:
        log_with_ip(f"Error when {character_name} leveling down", logging.ERROR)
        return jsonify({'error': f'Error leveling down {character_name}'}), 404

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

# POST метод для создания предложения сделки
@app.route('/trade/offer', methods=['POST'])
def create_trade_offer():
    data = request.json
    initiator_name = data.get('initiator_name')
    target_name = data.get('target_name')
    items_offered = data.get('items_offered', [])
    items_requested = data.get('items_requested', [])

    if items_offered is None or not isinstance(items_offered, list):
        items_offered = []
        log_with_ip("items_offered is None or not a list, defaulting to empty list", logging.WARNING)
    if items_requested is None or not isinstance(items_requested, list):
        items_requested = []
        log_with_ip("items_requested is None or not a list, defaulting to empty list", logging.WARNING)

    if not initiator_name or not target_name or not items_offered or not items_requested:
        log_with_ip("Incomplete trade offer data", logging.WARNING)
        return jsonify({'error': 'All trade fields required'}), 400

    if db.trade_system.create_offer(initiator_name, target_name, items_offered, items_requested):
        log_with_ip(f"Trade offer created from {initiator_name} to {target_name}")
        return jsonify({'message': f'Trade offer from {initiator_name} to {target_name} created'}), 200
    else:
        log_with_ip(f"Failed to create trade offer from {initiator_name} to {target_name}", logging.ERROR)
        return jsonify({'error': 'Failed to create trade offer'}), 400

# POST метод для принятия сделки
@app.route('/trade/accept', methods=['POST'])
def accept_trade():
    data = request.json
    target_name = data.get('target_name')
    initiator_name = data.get('initiator_name')

    if not target_name or not initiator_name:
        log_with_ip("Attempt to accept trade without names", logging.WARNING)
        return jsonify({'error': 'Target and initiator names required'}), 400

    if db.trade_system.accept_trade(target_name, initiator_name):
        log_with_ip(f"Trade accepted between {initiator_name} and {target_name}")
        return jsonify({'message': f'Trade between {initiator_name} and {target_name} completed'}), 200
    else:
        log_with_ip(f"Failed to accept trade between {initiator_name} and {target_name}", logging.ERROR)
        return jsonify({'error': 'Failed to accept trade'}), 400

# POST метод для отклонения сделки
@app.route('/trade/decline', methods=['POST'])
def decline_trade():
    data = request.json
    target_name = data.get('target_name')
    initiator_name = data.get('initiator_name')

    if not target_name or not initiator_name:
        log_with_ip("Attempt to decline trade without names", logging.WARNING)
        return jsonify({'error': 'Target and initiator names required'}), 400

    if db.trade_system.decline_trade(target_name, initiator_name):
        log_with_ip(f"Trade declined between {initiator_name} and {target_name}")
        return jsonify({'message': f'Trade between {initiator_name} and {target_name} declined'}), 200
    else:
        log_with_ip(f"Failed to decline trade between {initiator_name} and {target_name}", logging.ERROR)
        return jsonify({'error': 'Failed to decline trade'}), 400

# POST метод для отмены сделки
@app.route('/trade/cancel', methods=['POST'])
def cancel_trade():
    data = request.json
    initiator_name = data.get('initiator_name')

    if not initiator_name:
        log_with_ip("Attempt to cancel trade without initiator name", logging.WARNING)
        return jsonify({'error': 'Initiator name required'}), 400

    if db.trade_system.cancel_trade(initiator_name):
        log_with_ip(f"Trade offer from {initiator_name} canceled")
        return jsonify({'message': f'Trade offer from {initiator_name} canceled'}), 200
    else:
        log_with_ip(f"Failed to cancel trade offer from {initiator_name}", logging.ERROR)
        return jsonify({'error': 'Failed to cancel trade offer'}), 400

if __name__ == '__main__':
    logging.info("Auth_server Start")
    app.run(host='0.0.0.0', port=5005, debug=True)