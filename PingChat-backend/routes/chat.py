from flask import Blueprint

bp = Blueprint('chat', __name__)

# 在这里注册路由
@bp.route('/chat', methods=['POST'])
def login():
    return 'Chat API'

