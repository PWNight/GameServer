from flask import Flask,request,jsonify,render_template
import logging
import markdown
from models import DataBase,User

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
        log_with_ip(f"created {character_name}")
        db.token(login)
        return jsonify({ 'message': f'{character_name} level up' })
    else:
        log_with_ip(f"Error when {character_name} level up", logging.ERROR)
        db.token(login)
        return jsonify({ 'error': f'Error when {character_name} level up' }), 401

# POST метод для понижения уровня персонажа
@app.route('level_down',methods=['POST'])
def level_down():
    #TODO Разработать метод
    pass

if __name__=='__main__':
    logging.info("Auth_server Start")
    app.run(host='0.0.0.0',port=5005,debug=True)