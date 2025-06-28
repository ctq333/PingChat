from extensions import db
from sqlalchemy.dialects.mysql import ENUM as MySQLEnum
from sqlalchemy.sql import func

class Friend(db.Model):
    __tablename__ = 'friends'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    friend_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    remark = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    status = db.Column(
        MySQLEnum('pending', 'accepted', 'blocked'),
        default='accepted'
    )

    __table_args__ = (
        db.UniqueConstraint('user_id', 'friend_id'),
    )