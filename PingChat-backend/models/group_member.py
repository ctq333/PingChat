from extensions import db
from sqlalchemy.sql import func

class GroupMember(db.Model):
    __tablename__ = 'group_members'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    group_id = db.Column(db.BigInteger, db.ForeignKey('groupchat.id'), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    joined_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    muted = db.Column(db.Boolean, default=False)

    __table_args__ = (
        db.UniqueConstraint('group_id', 'user_id'),
    )