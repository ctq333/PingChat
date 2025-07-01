# sockets/__init__.py

from .user_map import user_sid_map, sid_user_map
from extensions import socketio
from flask import request
from datetime import datetime

# 在线用户信息：{user_id: {'sid':..., 'login_time':..., 'ip':...}}
user_sid_map = {}
user_online_info = {}

@socketio.on('connect')
def handle_connect():
    user_id = int(request.args.get('user_id'))  
    sid = request.sid
    user_sid_map.setdefault(user_id, []).append(sid)
    user_online_info[user_id] = {
        'sid': sid,
        'login_time': datetime.now().isoformat(),
        'ip': request.remote_addr
    }

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    for uid, sids in list(user_sid_map.items()):
        if sid in sids:
            sids.remove(sid)
            if not sids:
                del user_sid_map[uid]
            break

def register_chat_events(socketio):
    from flask import request
    from .single_text import register_single_text
    # ...你可以在此注册其它事件...

    # 注册每个功能事件
    from .single_text import register_single_text
    from .single_image import register_single_image
    from .group_text import register_group_text
    from .group_image import register_group_image
    from .admin import register_admin

    register_single_text(socketio)
    register_single_image(socketio)
    register_group_text(socketio)
    register_group_image(socketio)
    register_admin(socketio)