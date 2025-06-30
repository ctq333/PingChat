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

    # 添加群主和成员（去重，一次性查出所有用户）
    member_ids = list(set([owner_id] + member_ids))
    users = User.query.filter(User.id.in_(member_ids)).all()
    user_id_set = set(u.id for u in users)
    for uid in member_ids:
        if uid not in user_id_set:
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


# 添加群成员接口
@bp.route('/add_member', methods=['POST'])
def add_member():
    data = request.get_json()
    group_id = data.get('group_id')
    user_id = data.get('user_id')
    if not group_id or not user_id:
        return jsonify({'code': 400, 'message': '参数缺失'}), 400
    group = GroupChat.query.get(group_id)
    user = User.query.get(user_id)
    if not group:
        return jsonify({'code': 404, 'message': '群聊不存在'}), 404
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404
    # 检查是否已在群中
    exists = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if exists:
        return jsonify({'code': 409, 'message': '用户已在群聊中'}), 409
    gm = GroupMember(group_id=group_id, user_id=user_id, is_admin=False)
    db.session.add(gm)
    db.session.commit()
    return jsonify({'code': 200, 'message': '添加成功'})


# 移除群成员接口
@bp.route('/remove_member', methods=['POST'])
def remove_member():
    data = request.get_json()
    group_id = data.get('group_id')
    user_id = data.get('user_id')
    if not group_id or not user_id:
        return jsonify({'code': 400, 'message': '参数缺失'}), 400
    group = GroupChat.query.get(group_id)
    user = User.query.get(user_id)
    if not group:
        return jsonify({'code': 404, 'message': '群聊不存在'}), 404
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404
    gm = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not gm:
        return jsonify({'code': 404, 'message': '该用户不在群聊中'}), 404
    db.session.delete(gm)
    db.session.commit()
    return jsonify({'code': 200, 'message': '移除成功'})


# 获取群成员列表接口
@bp.route('/members', methods=['GET'])
def get_group_members():
    group_id = request.args.get('group_id')
    if not group_id:
        return jsonify({'code': 400, 'message': '参数缺失'}), 400
    group = GroupChat.query.get(group_id)
    if not group:
        return jsonify({'code': 404, 'message': '群聊不存在'}), 404
    members = (
        db.session.query(User.id, User.username)
        .join(GroupMember, GroupMember.user_id == User.id)
        .filter(GroupMember.group_id == group_id)
        .all()
    )
    result = [{'id': m.id, 'name': m.username or ''} for m in members]
    return jsonify({'code': 200, 'data': result})


# 获取可添加进群的用户列表接口
@bp.route('/addable_users', methods=['GET'])
def get_addable_users():
    group_id = request.args.get('group_id')
    if not group_id:
        return jsonify({'code': 400, 'message': '参数缺失'}), 400
    group = GroupChat.query.get(group_id)
    if not group:
        return jsonify({'code': 404, 'message': '群聊不存在'}), 404
    # 查找已在群内的用户id
    member_ids = db.session.query(GroupMember.user_id).filter_by(group_id=group_id).subquery()
    users = User.query.filter(~User.id.in_(member_ids)).all()
    result = [{'id': u.id, 'name': u.username or ''} for u in users]
    return jsonify({'code': 200, 'data': result})


# 解散群聊接口
@bp.route('/dissolve', methods=['POST'])
def dissolve_group():
    data = request.get_json()
    group_id = data.get('group_id')
    if not group_id:
        return jsonify({'code': 400, 'message': '参数缺失'}), 400
    group = GroupChat.query.get(group_id)
    if not group:
        return jsonify({'code': 404, 'message': '群聊不存在'}), 404
    # 删除群成员
    GroupMember.query.filter_by(group_id=group_id).delete()
    # 删除群聊
    db.session.delete(group)
    db.session.commit()
    return jsonify({'code': 200, 'message': '群聊已解散'})