from .user_map import user_sid_map
from extensions import db
from models import Message, GroupMember
from datetime import datetime

def get_group_user_ids(group_id):
    # 查询群成员 user_id，返回 list
    return [m.user_id for m in GroupMember.query.filter_by(group_id=group_id).all()]

def register_group_image(socketio):
    @socketio.on('group_image')
    def handle_group_image(data):
        """
        data: {
            from: user_id,
            group_id: int,
            image: base64字符串,
            filename: str,
            msg_type: 'image',
            send_time: 时间戳或字符串,
            extra: {width, height, ...}
        }
        """
        # 字段校验
        required_fields = ['from', 'group_id', 'image', 'filename', 'send_time']
        missing = [f for f in required_fields if f not in data]
        if missing:
            print(f"[group_image] 缺少字段: {', '.join(missing)}，收到的数据: {data}")
            return

        # 入库（只存元数据，不存base64图片）
        msg = Message(
            sender_id=data['from'],
            receiver_id=None,
            group_id=data['group_id'],
            msg_type='image',
            content='[图片]',
            send_time=datetime.fromtimestamp(data['send_time']/1000) if isinstance(data['send_time'], (int, float)) else datetime.utcnow(),
            status='sent',
            extra={
                'filename': data.get('filename'),
                'width': data.get('extra', {}).get('width'),
                'height': data.get('extra', {}).get('height')
            }
        )
        db.session.add(msg)
        db.session.commit()
        data['id'] = msg.id

        # 群发（含base64图片）
        group_id = data['group_id']
        from_user = int(data['from'])
        user_ids = get_group_user_ids(group_id)
        for uid in user_ids:
            uid = int(uid)
            if uid != from_user:
                sid = user_sid_map.get(uid)
                if sid:
                    socketio.emit('group_image', data, room=sid)