from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import User
import jwt
import datetime
import os

bp = Blueprint('auth', __name__)

JWT_SECRET = os.environ.get('JWT_SECRET', 'dev-secret')
JWT_EXPIRES = int(os.environ.get('JWT_EXPIRES', 7 * 24 * 3600))  # 默认7天

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    if not username or not password:
        return jsonify({'code': 400, 'message': '用户名和密码不能为空'}), 400
    if len(username) > 64:
        return jsonify({'code': 400, 'message': '用户名过长'}), 400
    if len(password) < 6:
        return jsonify({'code': 400, 'message': '密码至少6位'}), 400
    # 用户名唯一
    if User.query.filter_by(username=username).first():
        return jsonify({'code': 409, 'message': '用户名已存在'}), 409
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    user = User(username=username, password=hashed_password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'code': 201, 'message': '注册成功'}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    if not username or not password:
        return jsonify({'code': 400, 'message': '用户名和密码不能为空'}), 400
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'code': 401, 'message': '用户名不存在'}), 401
    if user.is_banned:
        return jsonify({'code': 403, 'message': '账号已被封禁'}), 403
    if not check_password_hash(user.password, password):
        return jsonify({'code': 401, 'message': '密码错误'}), 401
    # 生成 JWT
    payload = {
        'user_id': user.id,
        'username': user.username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXPIRES)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    # 返回用户基本信息和token
    user_data = {
        'id': user.id,
        'username': user.username,
        'nickname': user.nickname,
        'avatar_url': user.avatar_url,
        'is_admin': user.is_admin
    }
    return jsonify({
        'code': 200,
        'message': '登录成功',
        'data': {'user': user_data, 'token': token}
    })