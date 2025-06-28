from flask import Blueprint

bp = Blueprint('user', __name__)

# 在这里注册路由
@bp.route('/remove', methods=['POST'])
def login():
    return 'Remove API'

# 还可以有其它路由