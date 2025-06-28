from flask import Blueprint

bp = Blueprint('group', __name__)

# 在这里注册路由
@bp.route('/groupchat', methods=['POST'])
def login():
    return 'Group API'

# 还可以有其它路由