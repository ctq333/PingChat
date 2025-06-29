# sockets/admin.py

from flask import request
from .user_map import user_sid_map
from models import User
from sqlalchemy.orm.exc import NoResultFound

kicked_user_ids = set()

def register_admin(socketio):
    @socketio.on('kick_user')
    def handle_kick_user(data):
        admin_id = str(data.get('admin_id'))
        target_user_id = str(data.get('target_user_id'))
        try:
            from models import User
            admin = User.query.filter_by(id=admin_id).one()
            if not admin.is_admin:
                socketio.emit('op_result', {'ok': False, 'msg': '无权限'}, room=request.sid)
                return
        except NoResultFound:
            socketio.emit('op_result', {'ok': False, 'msg': '无此管理员'}, room=request.sid)
            return

        sid = user_sid_map.get(target_user_id)
        if sid:
            kicked_user_ids.add(target_user_id)
            socketio.emit('force_logout', {'reason': '被管理员踢出'}, room=sid)
            socketio.disconnect(sid=sid)
            socketio.emit('op_result', {'ok': True, 'msg': f'用户{target_user_id}已被踢出'}, room=request.sid)
        else:
            socketio.emit('op_result', {'ok': False, 'msg': '用户不在线'}, room=request.sid)