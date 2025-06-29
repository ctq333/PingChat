import os
from flask import Flask, send_from_directory
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()  # 读取.env文件

from extensions import db, socketio

def create_app():
    app = Flask(__name__)

    # ---- 1. 读取环境变量 ----
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = os.environ.get('MYSQL_PORT', '3306')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'test')
    MYSQL_CHARSET = os.environ.get('MYSQL_CHARSET', 'utf8mb4')
    ALLOWED_CORS_ORIGINS = os.environ.get('ALLOWED_CORS_ORIGINS', '*')

    # ---- 2. 构造 SQLALCHEMY_DATABASE_URI ----
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset={MYSQL_CHARSET}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key')
    app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', os.path.join(app.root_path, 'uploads'))

    # ---- 3. 初始化扩展 ----
    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins=ALLOWED_CORS_ORIGINS)

    # ---- 4. 注册蓝图 ----
    from routes.auth import bp as auth_bp
    from routes.user import bp as user_bp
    from routes.group import bp as group_bp
    from routes.chat import bp as chat_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(group_bp, url_prefix='/api/group')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')

    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    @app.route('/')
    def index():
        return 'Chat Backend Running!'

    return app

if __name__ == '__main__':
    app = create_app()
    CORS(app, supports_credentials=True)
    from sockets.__init__ import register_chat_events
    register_chat_events(socketio)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)