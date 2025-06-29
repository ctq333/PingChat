# sockets/group_text.py

from flask import request
from .user_map import user_sid_map
from models import GroupMember

def get_group_user_ids(group_id):
    return [m.user_id for m in GroupMember.query.filter_by(group_id=group_id).all()]

def register_group_text(socketio):
    @socketio.on('group_message')
    def handle_group_message(data):
        group_id = data['group_id']
        from_user = str(data['from'])
        user_ids = get_group_user_ids(group_id)
        for uid in user_ids:
            uid = str(uid)
            if uid != from_user:
                sid = user_sid_map.get(uid)
                if sid:
                    socketio.emit('group_message', data, room=sid)