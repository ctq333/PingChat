from flask import Blueprint,  request, jsonify
from extensions import db
from models import User
bp = Blueprint('user', __name__)

# 在这里注册路由
@bp.route('/list', methods=['GET'])
def list_users():
    users = User.query.all()
    result = [
        {'id': u.id, 'username': u.username, 'nickname': u.nickname or u.username, 'avatar_url': u.avatar_url}
        for u in users
    ]
    return jsonify({'code': 200, 'data': result})

# 还可以有其它路由