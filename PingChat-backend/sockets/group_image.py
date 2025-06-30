# sockets/group_image.py

from flask import request
from extensions import db
from models import Message, GroupMember
from .user_map import user_sid_map
from datetime import datetime

def get_group_user_ids(group_id):
    return [m.user_id for m in GroupMember.query.filter_by(group_id=group_id).all()]

def register_group_image(socketio):
    @socketio.on('group_image')
    def handle_group_image(data):
        group_id = data.get('group_id')
        from_user = int(data.get('from'))
        image_id = data.get('image_id')
        filename = data.get('filename')
        extra = data.get('extra') or {}
        send_time = datetime.now()

        # 把 filename 存入 extra 中（如果还没加）
        if filename:
            extra['filename'] = filename
        if image_id:
            extra['image_id'] = image_id

        # 存储消息到数据库
        msg = Message(
            sender_id=from_user,
            group_id=group_id,
            msg_type='image',
            content='[图片]',  # 内容可以写 placeholder
            send_time=send_time,
            extra=extra
        )
        db.session.add(msg)
        db.session.commit()

        # 给群里所有人广播（除了自己）
        user_ids = get_group_user_ids(group_id)
        for uid in user_ids:
            if uid != from_user:
                sid = user_sid_map.get(str(uid))
                if sid:
                    socketio.emit('group_image', {
                        'id': msg.id,
                        'group_id': group_id,
                        'sender_id': from_user,
                        'msg_type': 'image',
                        'send_time': send_time.strftime("%Y-%m-%dT%H:%M:%S"),
                        'filename': filename,
                        'image_id': image_id,
                        'extra': extra
                    }, room=sid)
