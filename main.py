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
def log_with_ip(message,level=logging.INFO):
    ip_address = request.remote_addr
    log_message = f"{message} [IP: {ip_address}]"
    logging.log(level,log_message)

@app.route('/')
def home():
    with open('README.md','r',encoding='utf-8')as f:
        content = f.read()
        content_html=markdown.markdown(content)
        return render_template("readme.html",content=content_html)
@app.route('/reg',methods=['POST'])
def reg():
    data=request.json
    login = data.get('login')
    password = data.get('password')
    if not login or not password:
        log_with_ip("Registration attempt without login/password",logging.WARNING)
        return jsonify({'error':'Login or Password required'}),400
    if db.user_add(login, password):
        log_with_ip(f"User {login} registered")
        return jsonify({'message':'User created'}),201
    else:
        log_with_ip(f"Registration failed for {login}",logging.ERROR)
        return jsonify({'error':'Username exists'}),400
@app.route('/login',methods=['POST'])
def login():
    data = request.json
    login = data.get('login')
    password = data.get('password')
    if not login or not password:
        log_with_ip("Registration attempt without login/password",logging.WARNING)
        return jsonify({'error':'Login or Password required'}),400
    if db.auth(login, password):
        log_with_ip(f"User {login} logged in")
        db.token(login)
        return jsonify({'token':db.token(login)}),200
@app.route('/out',methods=['POST'])
def out():
    data = request.json
    login = data.get('login')
    if not login :
        log_with_ip("Registration attempt without login",logging.WARNING)
        return jsonify({'error':'Login   required'}),400
    if db.out(login):
        log_with_ip("User out sistem")
        return jsonify({'message':'User out sistem'})
    else:
        log_with_ip("User out sistem error",logging.ERROR)
        return jsonify({'error':'User out sistem Error'})
@app.route('/password',methods=['POST'])
def password():
    data = request.json
    login = data.get('login')
    password_new = data.get('password')
    if not login or not password_new:
        log_with_ip("Registration attempt without login",logging.WARNING)
        return jsonify({'error':'Login   required'}),400
    if db.password_edit(login, password_new):
        log_with_ip("User edit password")
        return jsonify({'message':'User edit password'})
    else:
        log_with_ip("User edit password error",logging.ERROR)
        return jsonify({'error':'edit password Error'})
@app.route('/character',methods=['POST'])
def character_add():
    data = request.json
    login = data.get('login')
    name = data.get('name')
    if not login or not name:
        log_with_ip("Registration attempt without login/name", logging.WARNING)
        return jsonify({'error': 'Login or name required'}), 400
    if db.character_add(login, name):
        log_with_ip(f"User {login} created haracter{name}")
        db.token(login)
        return jsonify({'message': f'User {login} created haracter{name}'}), 200
    else:
        log_with_ip(f"User {login} created haracter{name} ERROR",logging.ERROR)
        db.token(login)
        return jsonify({'error': f'User {login} created haracter{name} Error' }), 401

@app.route('level_up',methods=['POST'])
def level_up():
    data = request.json
    name = data.get('name')
    if not name:
        log_with_ip(" None name", logging.WARNING)
        return jsonify({'error': 'None name'}), 400
    if db.level_up(name):
        log_with_ip(f"created {name}")
        db.token(login)
        return jsonify({'message': f'User {login} created haracter{name}'}), 200
    else:
        log_with_ip(f"User {login} created haracter{name} ERROR",logging.ERROR)
        db.token(login)
        return jsonify({'error': f'User {login} created haracter{name} Error' }), 401


@app.route('level_down',methods=['POST'])
def level_down():
    pass



if __name__=='__main__':
    logging.info("Auth_server Start")
    app.run(host='0.0.0.0',port=5005,debug=True)