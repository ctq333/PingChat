from flask import request
from .user_map import user_sid_map
from extensions import db
from models import Message
from datetime import datetime

def register_single_image(socketio):
    @socketio.on('single_image')
    def handle_single_image(data):
        """
        data: {
            from, to, image: base64/Blob,
            filename, msg_type, send_time, extra
        }
        """
        # 存入数据库的仅是 metadata，不含 base64 图像
        msg = Message(
            sender_id=data['from'],
            receiver_id=data['to'],
            group_id=None,
            msg_type='image',
            content='[图片]',
            send_time=datetime.fromtimestamp(data['send_time']/1000),
            status='sent',
            extra={
                'filename': data.get('filename'),
                'width': data.get('extra', {}).get('width'),
                'height': data.get('extra', {}).get('height'),
            }
        )
        db.session.add(msg)
        db.session.commit()
        data['id'] = msg.id

        # 发给接收方（含 base64 图像）
        to_user = str(data['to'])
        sid = user_sid_map.get(to_user)
        if sid:
            socketio.emit('single_image', data, room=sid)
