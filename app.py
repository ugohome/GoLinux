from flask import Flask, render_template
from flask_login import LoginManager, login_required, logout_user
from flask_bootstrap import Bootstrap
from flask_dropzone import Dropzone
from system import system
from raid import raid
from NAS import nas
from net import net
from DRS import drs
import login

app = Flask(__name__)

#app.secret_key = 'helloPTL'

app.config.from_object('config')
app.register_blueprint(system.bp)
app.register_blueprint(raid.bp)
app.register_blueprint(nas.nas_bp)
app.register_blueprint(net.net_bp)
app.register_blueprint(drs.drs_bp)
bootstrap = Bootstrap(app)
dropzone = Dropzone(app)

#初始化LoginManager
loginmanager = LoginManager()
loginmanager.login_message = '请先登陆!'
loginmanager.session_protection = 'strong'
loginmanager.login_view = '/'
loginmanager.init_app(app)

#回调函数,通过user_id重载(返回)一个User对像,判断用户的登陆状态,
#因为http是无状态的,当用户登陆成功后再次请求受保护路由,flask-login需要通过请求上下文中session(id)判断用户登陆状态,
#这由回调函数实现.
@loginmanager.user_loader
def load_user(user_id):
    return login.User.get_User(user_id)

@app.route('/', methods=['POST', 'GET'])
def index():
    return login.login()
    #return render_template('index.html')

@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='58888', debug=True)
