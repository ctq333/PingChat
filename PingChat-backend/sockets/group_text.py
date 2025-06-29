# sockets/group_text.py
from .user_map import user_sid_map
from extensions import db
from models import Message, GroupMember
from datetime import datetime

def get_group_user_ids(group_id):
    # 查询群成员 user_id，返回 list
    return [m.user_id for m in GroupMember.query.filter_by(group_id=group_id).all()]

def register_group_text(socketio):
    @socketio.on('group_message')
    def handle_group_message(data):
        """
        data: {
            from: user_id,
            group_id: int,
            content: str,
            msg_type: 'text',
            send_time: 时间戳或字符串
        }
        """
        # 入库
        msg = Message(
            sender_id=data['from'],
            receiver_id=None,
            group_id=data['group_id'],
            msg_type='text',
            content=data['content'],
            send_time=datetime.fromtimestamp(data['send_time']/1000) if isinstance(data['send_time'], (int, float)) else datetime.utcnow(),
            status='sent'
        )
        db.session.add(msg)
        db.session.commit()
        data['id'] = msg.id

        # 群发
        group_id = data['group_id']
        from_user = str(data['from'])
        user_ids = get_group_user_ids(group_id)
        for uid in user_ids:
            uid = str(uid)
            if uid != from_user:
                sid = user_sid_map.get(uid)
                if sid:
                    socketio.emit('group_message', data, room=sid)

    @socketio.on('group_image')
    def handle_group_image(data):
        """
        data: {
            from: user_id,
            group_id: int,
            image: base64字符串,
            filename: "xxx.png",
            msg_type: 'image',
            send_time: 时间戳或字符串,
            extra: {width, height, ...}
        }
        """
        # 保存图片消息（图片内容不存数据库，extra可存图片唯一id等）
        image_id = f'img_{int(datetime.utcnow().timestamp()*1000)}_{data["from"]}'
        msg = Message(
            sender_id=data['from'],
            receiver_id=None,
            group_id=data['group_id'],
            msg_type='image',
            content='[图片]',  # 或 data['filename']
            send_time=datetime.fromtimestamp(data['send_time']/1000) if isinstance(data['send_time'], (int, float)) else datetime.utcnow(),
            status='sent',
            extra={
                'filename': data.get('filename'),
                'image_id': image_id,
                'width': data.get('extra', {}).get('width'),
                'height': data.get('extra', {}).get('height')
            }
        )
        db.session.add(msg)
        db.session.commit()
        data['id'] = msg.id
        data['image_id'] = image_id

        # 群发
        group_id = data['group_id']
        from_user = str(data['from'])
        user_ids = get_group_user_ids(group_id)
        for uid in user_ids:
            uid = str(uid)
            if uid != from_user:
                sid = user_sid_map.get(uid)
                if sid:
                    socketio.emit('group_image', data, room=sid)