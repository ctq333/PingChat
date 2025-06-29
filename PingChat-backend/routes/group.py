from flask import Blueprint, request, jsonify
from extensions import db
from models import GroupChat, GroupMember, User
from sqlalchemy.sql import func

bp = Blueprint('group', __name__)

@bp.route('/create', methods=['POST'])
def create_group():
    data = request.get_json()
    group_name = (data.get('name') or '').strip()
    owner_id = data.get('owner_id')
    member_ids = data.get('member_ids', [])

    # 校验
    if not group_name:
        return jsonify({'code': 400, 'message': '群组名称不能为空'}), 400
    if not owner_id or not User.query.get(owner_id):
        return jsonify({'code': 400, 'message': '无效的群主'}), 400

    # 创建群
    group = GroupChat(name=group_name, owner_id=owner_id)
    db.session.add(group)
    db.session.flush()  # 让 group.id 生效

    # 添加群主和成员（去重）
    member_ids = list(set([owner_id] + member_ids))
    for uid in member_ids:
        if not User.query.get(uid):
            continue
        gm = GroupMember(group_id=group.id, user_id=uid, is_admin=(uid == owner_id))
        db.session.add(gm)

    db.session.commit()
    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': {
            'group_id': group.id,
            'name': group.name,
            'owner_id': owner_id,
            'member_ids': member_ids
        }
    })