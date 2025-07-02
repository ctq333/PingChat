from flask import Blueprint,  request, jsonify
from extensions import db, socketio
from models import User,GroupMember,Message
from sockets.__init__ import user_sid_map  # 导入映射
from flask_socketio import disconnect
bp = Blueprint('user', __name__)

# 在这里注册路由
@bp.route('/list', methods=['GET'])
def list_users():
    users = User.query.all()
    result = [
        {
            'id': u.id, 
            'username': u.username, 
            'nickname': u.nickname or u.username,
            'avatar_url': u.avatar_url,
            'is_admin': u.is_admin,
            'is_banned': u.is_banned,
            'is_muted': u.is_muted if hasattr(u, 'is_muted') else False
        }
        for u in users
    ]
    return jsonify({'code': 200, 'data': result})

# 设置/取消管理员
@bp.route('/set_admin', methods=['POST'])
def set_admin():
    data = request.get_json()
    user_id = data.get('id')
    is_admin = data.get('is_admin')  
    if user_id is None or is_admin is None:
        return jsonify({'code': 400, 'msg': '参数缺失'}), 400
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'msg': '用户不存在'}), 404
    user.is_admin = bool(is_admin)
    db.session.commit()
    return jsonify({'code': 200, 'msg': '操作成功'})

# 删除用户
from models import User, GroupMember
from extensions import db
from flask import Blueprint, request, jsonify

@bp.route('/delete', methods=['POST'])
def delete_user():
    data = request.get_json()
    user_id = data.get('id')
    if not user_id:
        return jsonify({'code': 400, 'msg': '参数缺失'}), 400
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'msg': '用户不存在'}), 404

    # 1. 先删除 group_members 里的关联
    GroupMember.query.filter_by(user_id=user_id).delete()
    # 2. 再删除 messages 里与该用户相关的所有消息
    Message.query.filter((Message.sender_id == user_id) | (Message.receiver_id == user_id)).delete(synchronize_session=False)
    # 3. 如果还有其它表有关联，也要一并删除

    db.session.delete(user)
    db.session.commit()
    return jsonify({'code': 200, 'msg': '删除成功'})

#禁止登录
@bp.route('/ban',methods=['POST'])
def ban_user():
    data = request.get_json()
    user_id = data.get('id')
    if not user_id:
        return jsonify({'code':400, 'msg':'参数缺失'}),400
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code':404, 'msg':'该用户不存在'}),404
    user.is_banned = True
    db.session.commit()
    return jsonify({'code':200,'msg':'该用户已禁用'})
    
@bp.route('/unban',methods=['POST'])
def unban_user():
    data = request.get_json()
    user_id = data.get('id')
    if not user_id:
        return jsonify({'code':400,'msg':'参数缺失'})
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code':404,'msg':'该用户不存在'})
    user.is_banned = False
    db.session.commit()
    return jsonify({'code':200,'msg':'用户已解禁'})

# 禁言用户
@bp.route('/mute', methods=['POST'])
def mute_user():
    data = request.get_json()
    user_id = data.get('id')
    if not user_id:
        return jsonify({'code': 400, 'msg': '参数缺失'}), 400
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'msg': '用户不存在'}), 404
    user.is_muted = True
    db.session.commit()
    return jsonify({'code': 200, 'msg': '用户已禁言'})

# 解除禁言
@bp.route('/unmute', methods=['POST'])
def unmute_user():
    data = request.get_json()
    user_id = data.get('id')
    if not user_id:
        return jsonify({'code': 400, 'msg': '参数缺失'}), 400
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'msg': '用户不存在'}), 404
    user.is_muted = False
    db.session.commit()
    return jsonify({'code': 200, 'msg': '已解除禁言'})

@bp.route('/kick', methods=['POST'])
def kick_user():
    data = request.get_json()
    user_id = data.get('id')
    if user_id is not None:
        user_id = int(user_id)
    if not user_id:
        return jsonify({'code': 400, 'msg': '参数缺失'}), 400
    sid = user_sid_map.get(user_id)
    if sid:
        socketio.emit('force_logout', {'msg': '您已被管理员强制下线'}, to=sid)
        disconnect(sid, namespace='/')
        return jsonify({'code': 200, 'msg': '已踢出用户'})
    else:
        return jsonify({'code': 404, 'msg': '用户不在线'}), 404

@bp.route('/online_list', methods=['GET'])
def online_list():
    # user_sid_map 的 key 是在线用户ID
    online_user_ids = list(user_sid_map.keys())
    if not online_user_ids:
        return jsonify({'code': 200, 'data': []})
    users = User.query.filter(User.id.in_(online_user_ids)).all()
    result = [
        {
            'id': u.id,
            'username': u.username,
            'nickname': u.nickname or u.username,
            'avatar_url': u.avatar_url
        }
        for u in users
    ]
    return jsonify({'code': 200, 'data': result})

# 检查用户是否在线
@bp.route('/<int:user_id>/online', methods=['GET'])
def is_user_online(user_id):
    is_online = user_id in user_sid_map
    return jsonify({'online': is_online})

